"""
Interfacing with the Student Web Service, Registration_Search query.
"""
import logging
import json
import re
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from decimal import Decimal, InvalidOperation
from datetime import datetime
from dateutil.parser import parse
from uw_sws.models import Registration, ClassSchedule
from restclients_core.exceptions import DataFailureException
from restclients_core.cache_manager import (enable_cache_entry_queueing,
                                            disable_cache_entry_queueing,
                                            save_all_queued_entries)
from uw_pws import PWS
from restclients_core.thread import (Thread, GenericPrefetchThread,
                                     generic_prefetch)
from uw_sws import get_resource
from uw_sws.compat import deprecation
from uw_sws.thread import SWSThread
from uw_sws.section import _json_to_section, get_prefetch_for_section_data


registration_res_url_prefix = "/student/v5/registration.json"
reg_credits_url_prefix = "/student/v5/registration/"
logger = logging.getLogger(__name__)


class SWSPersonByRegIDThread(Thread):
    regid = None
    person = None

    def run(self):
        if self.regid is None:
            raise Exception("SWSPersonByRegIDThread must have a regid")

        self.person = PWS().get_person_by_regid(self.regid)


def _registrations_for_section_with_active_flag(section, is_active,
                                                transcriptable_course=""):
    """
    Returns a list of all uw_sws.models.Registration objects
    for a section. There can be duplicates for a person.
    If is_active is True, the objects will have is_active set to True.
    Otherwise, is_active is undefined, and out of scope for this method.
    """
    instructor_reg_id = ""
    if (section.is_independent_study and
            section.independent_study_instructor_regid is not None):
        instructor_reg_id = section.independent_study_instructor_regid

    params = [
        ("curriculum_abbreviation", section.curriculum_abbr),
        ("instructor_reg_id", instructor_reg_id),
        ("course_number", section.course_number),
        ("verbose", "true"),
        ("year", section.term.year),
        ("quarter", section.term.quarter),
        ("is_active", "true" if is_active else ""),
        ("section_id", section.section_id),
    ]

    if transcriptable_course != "":
        params.append(("transcriptable_course", transcriptable_course,))

    url = "%s?%s" % (registration_res_url_prefix, urlencode(params))

    return _json_to_registrations(get_resource(url), section)


def _json_to_registrations(data, section):
    """
    Returns a list of all uw_sws.models.Registration objects
    """
    registrations = []
    person_threads = {}
    for reg_data in data.get("Registrations", []):
        registration = Registration()
        registration.section = section
        registration.is_active = reg_data["IsActive"]
        registration.is_credit = reg_data["IsCredit"]
        registration.is_auditor = reg_data["Auditor"]
        registration.is_independent_start = reg_data["IsIndependentStart"]
        if len(reg_data["StartDate"]):
            registration.start_date = parse(reg_data["StartDate"])
        if len(reg_data["EndDate"]):
            registration.end_date = parse(reg_data["EndDate"])
        if len(reg_data["RequestDate"]):
            registration.request_date = parse(reg_data["RequestDate"])
        registration.request_status = reg_data["RequestStatus"]
        registration.duplicate_code = reg_data["DuplicateCode"]
        registration.credits = reg_data["Credits"]
        registration.repository_timestamp = datetime.strptime(
            reg_data["RepositoryTimeStamp"], "%m/%d/%Y %H:%M:%S %p")
        registration.repeat_course = reg_data["RepeatCourse"]
        registration.grade = reg_data["Grade"]

        registration._uwregid = reg_data["Person"]["RegID"]
        if registration._uwregid not in person_threads:
            thread = SWSPersonByRegIDThread()
            thread.regid = registration._uwregid
            thread.start()
            person_threads[registration._uwregid] = thread

        registrations.append(registration)

    for registration in registrations:
        thread = person_threads[registration._uwregid]
        thread.join()
        registration.person = thread.person
        del registration._uwregid

    return registrations


def get_active_registrations_by_section(section, transcriptable_course=""):
    """
    Returns a list of restclients.Registration objects, representing
    active registrations for the passed section. For independent study
    sections, section.independent_study_instructor_regid limits
    registrations to that instructor.
    """
    return _registrations_for_section_with_active_flag(section, True,
                                                       transcriptable_course)


def get_all_registrations_by_section(section, transcriptable_course=""):
    """
    Returns a list of uw_sws.models.Registration objects,
    representing all (active and inactive) registrations for the passed
    section. For independent study sections,
    section.independent_study_instructor_regid limits registrations to
    that instructor.
    """
    return _registrations_for_section_with_active_flag(section, False,
                                                       transcriptable_course)


# This function won't work when the dup_code is not empty
def get_credits_by_section_and_regid(section, regid):
    """
    Returns a uw_sws.models.Registration object
    for the section and regid passed in.
    """
    deprecation("Use get_credits_by_reg_url")
    # note trailing comma in URL, it's required for the optional dup_code param
    url = "%s%s,%s,%s,%s,%s,%s,.json" % (
        reg_credits_url_prefix,
        section.term.year,
        section.term.quarter,
        re.sub(' ', '%20', section.curriculum_abbr),
        section.course_number,
        section.section_id,
        regid
    )

    reg_data = get_resource(url)

    try:
        return Decimal(reg_data['Credits'].strip())
    except InvalidOperation:
        pass


def get_credits_by_reg_url(url):
    """
    Returns a decimal value of the course credits
    """
    reg_data = get_resource(url)

    try:
        return Decimal(reg_data['Credits'].strip())
    except InvalidOperation:
        pass


def get_schedule_by_regid_and_term(regid, term,
                                   non_time_schedule_instructors=True,
                                   per_section_prefetch_callback=None,
                                   transcriptable_course="", **kwargs):
    """
    Returns a uw_sws.models.ClassSchedule object
    for the regid and term passed in.
    """

    if "include_instructor_not_on_time_schedule" in kwargs:
        include = kwargs["include_instructor_not_on_time_schedule"]
        non_time_schedule_instructors = include
    params = [
        ('reg_id', regid),
    ]

    if transcriptable_course != "":
        params.append(("transcriptable_course", transcriptable_course,))

    params.extend([
        ('quarter', term.quarter),
        ('is_active', 'true'),
        ('year', term.year),
    ])

    url = "%s?%s" % (registration_res_url_prefix, urlencode(params))

    return _json_to_schedule(get_resource(url), term, regid,
                             non_time_schedule_instructors,
                             per_section_prefetch_callback)


def _json_to_schedule(term_data, term, regid,
                      include_instructor_not_on_time_schedule=True,
                      per_section_prefetch_callback=None):
    sections = []
    sws_threads = []
    term_credit_hours = Decimal("0.0")

    enable_cache_entry_queueing()
    try:
        for registration in term_data["Registrations"]:
            reg_url = registration["Href"]

            # Skip a step here, and go right to the course section resource
            course_url = re.sub('registration', 'course', reg_url)
            course_url = re.sub('^(.*?,.*?,.*?,.*?,.*?),.*',
                                '\\1.json',
                                course_url)
            course_url = re.sub(',([^,]*).json', '/\\1.json', course_url)

            thread = SWSThread()
            thread.url = course_url
            thread.reg_url = reg_url
            thread.headers = {"Accept": "application/json"}
            thread.start()
            sws_threads.append(thread)

        for thread in sws_threads:
            thread.join()

        try:
            section_prefetch = []
            seen_keys = {}
            for thread in sws_threads:
                response = thread.response
                if response and response.status == 200:
                    data = json.loads(response.data)
                    sd_prefetch = get_prefetch_for_section_data(data)
                    section_prefetch.extend(sd_prefetch)
                    if per_section_prefetch_callback:
                        client_callbacks = per_section_prefetch_callback(data)
                        section_prefetch.extend(client_callbacks)

                url = thread.reg_url
                section_prefetch.append([url,
                                         generic_prefetch(get_resource,
                                                          [url])])

            prefetch_threads = []
            for entry in section_prefetch:
                key = entry[0]
                if key not in seen_keys:
                    seen_keys[key] = True
                    thread = GenericPrefetchThread()
                    prefetch_method = entry[1]
                    thread.method = prefetch_method
                    prefetch_threads.append(thread)
                    thread.start()

            for thread in prefetch_threads:
                thread.join()

        except Exception as ex:
            # If there's a real problem, it'll come up in the data fetching
            # step - no need to raise an exception here
            pass

        for thread in sws_threads:
            response = thread.response
            if not response:
                raise DataFailureException(thread.url,
                                           500,
                                           thread.exception)
            if response.status != 200:
                raise DataFailureException(thread.url,
                                           response.status,
                                           response.data)

            section = _json_to_section(json.loads(response.data), term,
                                       include_instructor_not_on_time_schedule)
            _add_credits_grade_to_section(thread.reg_url, section)
            if section.student_credits is not None:
                term_credit_hours += section.student_credits
            # For independent study courses, only include the one relevant
            # instructor
            if registration["Instructor"]:
                actual_instructor = None
                instructor_regid = registration["Instructor"]["RegID"]

                for instructor in section.meetings[0].instructors:
                    if instructor.uwregid == instructor_regid:
                        actual_instructor = instructor

                if actual_instructor:
                    section.meetings[0].instructors = [actual_instructor]
                else:
                    section.meetings[0].instructors = []

                instructor_regid = registration["Instructor"]
                section.independent_study_instructor_regid = instructor_regid
            sections.append(section)

        term.credits = term_credit_hours
        term.section_count = len(sections)
        schedule = ClassSchedule()
        schedule.sections = sections
        schedule.term = term

        save_all_queued_entries()
        disable_cache_entry_queueing()
    except Exception as ex:
        save_all_queued_entries()
        disable_cache_entry_queueing()
        raise ex
    return schedule


def _add_credits_grade_to_section(url, section):
    """
    Given the registration url passed in,
    add credits, grade, grade date in the section object
    """
    section_reg_data = get_resource(url)
    if section_reg_data is not None:
        section.student_grade = section_reg_data['Grade']
        section.is_auditor = section_reg_data['Auditor']
        if len(section_reg_data['GradeDate']) > 0:
            section.grade_date = parse(section_reg_data["GradeDate"]).date()
        try:
            raw_credits = section_reg_data['Credits'].strip()
            section.student_credits = Decimal(raw_credits)
        except InvalidOperation:
            pass
