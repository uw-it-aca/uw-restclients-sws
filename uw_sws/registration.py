"""
Interfacing with the Student Web Service, Registration_Search query.
"""
import logging
import json
import re
from urllib.parse import urlencode
from decimal import Decimal, InvalidOperation
from datetime import datetime
from uw_sws.models import Registration, ClassSchedule
from restclients_core.exceptions import DataFailureException
from restclients_core.cache_manager import (
    enable_cache_entry_queueing, disable_cache_entry_queueing,
    save_all_queued_entries)
from restclients_core.thread import (
    Thread, GenericPrefetchThread, generic_prefetch)
from uw_sws import get_resource
from uw_sws.person import get_person_by_regid
from uw_sws.exceptions import ThreadedDataError
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

        self.person = get_person_by_regid(self.regid)


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

    url = "{}?{}".format(registration_res_url_prefix, urlencode(params))

    return _json_to_registrations(get_resource(url), section)


def _json_to_registrations(data, section):
    """
    Returns a list of all uw_sws.models.Registration objects
    """
    registrations = []
    person_threads = {}
    for reg_json in data.get("Registrations", []):
        registration = Registration(data=reg_json)
        registration._uwregid = reg_json["Person"]["RegID"]
        registration.section = section
        registrations.append(registration)

        if registration._uwregid not in person_threads:
            thread = SWSPersonByRegIDThread()
            thread.regid = registration._uwregid
            thread.start()
            person_threads[registration._uwregid] = thread

    _set_person_in_registrations(registrations, person_threads)
    return registrations


def _set_person_in_registrations(registrations, person_threads):
    for registration in registrations:
        thread = person_threads[registration._uwregid]
        thread.join()
        registration.person = thread.person
        del registration._uwregid


# This function won't work when the dup_code is not empty
def get_credits_by_section_and_regid(section, regid):
    """
    Returns a uw_sws.models.Registration object
    for the section and regid passed in.
    """
    deprecation("Use get_credits_by_reg_url")
    # note trailing comma in URL, it's required for the optional dup_code param
    url = "{}{},{},{},{},{},{},.json".format(
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
                                   transcriptable_course="",
                                   **kwargs):
    """
    Returns a uw_sws.models.ClassSchedule object
    for the regid and term passed in.
    transcriptable_course values: "{|yes|no|all}".
    kwargs:
      instructor_reg_id="{instructor regid}"
      (to search the registration with an independent study instructor).
    Exceptions: DataFailureException, ThreadedDataError
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
        ('verbose', "on")
    ])

    url = "{}?{}".format(registration_res_url_prefix, urlencode(params))

    return _json_to_stud_reg_schedule(get_resource(url), term, regid,
                                      non_time_schedule_instructors,
                                      per_section_prefetch_callback)


def _json_to_stud_reg_schedule(json_data, term, regid,
                               include_instructor_not_on_time_schedule=True,
                               per_section_prefetch_callback=None):
    sections = []
    sws_threads = []
    term_credit_hours = Decimal("0.0")
    registered_summer_terms = {}
    if len(json_data["Registrations"]) == 0:
        schedule = ClassSchedule()
        schedule.sections = sections
        schedule.term = term
        return schedule

    enable_cache_entry_queueing()
    try:
        for registration in json_data["Registrations"]:
            thread = SWSThread()
            thread.reg_json = registration
            thread.url = registration["Section"]["Href"]
            thread.headers = {"Accept": "application/json"}
            thread.start()
            sws_threads.append(thread)

        # Get the course section resource
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

                if thread.reg_url is not None:
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
                raise ThreadedDataError(thread.url,
                                        response.status,
                                        response.data)

            section = _json_to_section(json.loads(response.data), term,
                                       include_instructor_not_on_time_schedule)

            if len(section.summer_term):
                registered_summer_terms[section.summer_term.lower()] = True

            _add_registration_to_section(thread.reg_json, section)

            if section.student_credits is not None:
                term_credit_hours += section.student_credits

            # For independent study courses, only include the one relevant
            # instructor
            if thread.reg_json.get("Instructor") is not None:
                _set_actual_instructor(thread.reg_json["Instructor"], section)

            sections.append(section)

        term.credits = term_credit_hours
        term.section_count = len(sections)
        schedule = ClassSchedule()
        schedule.sections = sections
        schedule.term = term
        schedule.registered_summer_terms = registered_summer_terms
        save_all_queued_entries()
        disable_cache_entry_queueing()
    except Exception as ex:
        save_all_queued_entries()
        disable_cache_entry_queueing()
        raise ex
    return schedule


def _add_registration_to_section(reg_json, section):
    """
    Add the Registration object to section.
    """
    registration = Registration(data=reg_json)
    section.registration = registration
    section.grade_date = registration.grade_date
    section.student_grade = registration.grade
    section.is_auditor = registration.is_auditor

    if section.is_source_eos() or section.is_source_sdb_eos():
        # the student's actual enrollment
        if registration.start_date is not None:
            section.start_date = registration.start_date
        if registration.end_date is not None:
            section.end_date = registration.end_date
    try:
        section.student_credits = Decimal(registration.credits)
    except InvalidOperation:
        pass


def _set_actual_instructor(instructor_json, section):
    actual_instructor = None
    instructor_regid = instructor_json["RegID"]
    for instructor in section.meetings[0].instructors:
        if instructor.uwregid == instructor_regid:
            actual_instructor = instructor

    if actual_instructor:
        section.meetings[0].instructors = [actual_instructor]
    else:
        section.meetings[0].instructors = []

    section.independent_study_instructor_regid = instructor_regid
