# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the Student Web Service, for Section and Course resources.
"""
import logging
import re
from datetime import datetime
from urllib.parse import urlencode
from restclients_core.thread import generic_prefetch
from uw_sws.exceptions import InvalidSectionID, InvalidSectionURL
from restclients_core.exceptions import DataFailureException
from uw_sws import get_resource, encode_section_label, UWPWS
from uw_sws.util import str_to_date
from uw_sws.term import get_term_by_year_and_quarter
from uw_sws.models import (
    Section, SectionReference, FinalExam,
    SectionMeeting, GradeSubmissionDelegate, Person)


course_url_pattern = re.compile(r'^\/student\/v5\/course\/')
course_res_url_prefix = "/student/v5/course"
section_res_url_prefix = "/student/v5/section.json"
sln_pattern = re.compile(r'^[1-9]\d{4}$')
section_label_pattern = re.compile(
    r'^[1-9]\d{3},'                      # year
    '(?:winter|spring|summer|autumn),'  # quarter
    r'[\w& ]+,'                          # curriculum
    r'\d{3}\/'                           # course number
    '[A-Z][A-Z0-9]?$',                  # section id
    re.VERBOSE
)
logger = logging.getLogger(__name__)


def validate_section_label(label):
    if label is None or section_label_pattern.match(label) is None:
        raise InvalidSectionID("Invalid section label: {}".format(label))


def is_valid_sln(sln_str):
    return not (sln_str is None or sln_pattern.match(sln_str) is None)


def get_sections_by_instructor_and_term(person,
                                        term,
                                        future_terms=0,
                                        include_secondaries=True,
                                        transcriptable_course='yes',
                                        delete_flag=['active']):
    """
    Returns a list of uw_sws.models.SectionReference objects
    for the passed instructor and term.
    @param: future_terms: 0..400
    @param: transcriptable_course: 'yes', 'no', 'all'
    @param: delete_flag: ['active', 'suspended', 'withdrawn']
    """
    data = _get_sections_by_person_and_term(person,
                                            term,
                                            "Instructor",
                                            include_secondaries,
                                            future_terms,
                                            transcriptable_course,
                                            delete_flag)
    return _json_to_sectionref(data)


def get_sections_by_delegate_and_term(person,
                                      term,
                                      future_terms=0,
                                      include_secondaries=True,
                                      transcriptable_course='yes',
                                      delete_flag=['active']):
    """
    Returns a list of uw_sws.models.SectionReference objects
    for the passed grade submission delegate and term.
    @param: future_terms: 0..400
    @param: transcriptable_course: 'yes', 'no', 'all'
    @param: delete_flag: ['active', 'suspended', 'withdrawn']
    """
    data = _get_sections_by_person_and_term(person,
                                            term,
                                            "GradeSubmissionDelegate",
                                            include_secondaries,
                                            future_terms,
                                            transcriptable_course,
                                            delete_flag)
    return _json_to_sectionref(data)


def get_sections_by_curriculum_and_term(curriculum, term):
    """
    Returns a list of uw_sws.models.SectionReference objects
    for the passed curriculum and term.
    """
    url = "{}?{}".format(
        section_res_url_prefix,
        urlencode([("curriculum_abbreviation", curriculum.label,),
                   ("quarter", term.quarter.lower(),),
                   ("year", term.year,), ]))
    return _json_to_sectionref(get_resource(url))


def get_sections_by_building_and_term(building, term):
    """
    Returns a list of uw_sws.models.SectionReference objects
    for the passed building and term.
    """
    url = "{}?{}".format(
        section_res_url_prefix,
        urlencode([("quarter", term.quarter.lower(),),
                   ("facility_code", building,),
                   ("year", term.year,), ]))
    return _json_to_sectionref(get_resource(url))


def get_changed_sections_by_term(changed_since_date, term, **kwargs):
    params = []
    for key in sorted(kwargs):
        params.append((key, kwargs[key],))
    params.extend([
                   ("changed_since_date", changed_since_date,),
                   ("quarter", term.quarter.lower(),),
                   ("page_size", 1000,),
                   ("year", term.year,),
                   ])
    url = "{}?{}".format(section_res_url_prefix, urlencode(params))

    sections = []
    while url is not None:
        data = get_resource(url)
        sections.extend(_json_to_sectionref(data))

        url = None
        if data.get("Next") is not None:
            url = data.get("Next").get("Href", None)

    return sections


def _json_to_sectionref(data):
    """
    Returns a list of SectionReference object created from
    the passed json data.
    """
    section_term = None
    sections = []
    for section_data in data.get("Sections", []):
        if (section_term is None or
                section_data["Year"] != section_term.year or
                section_data["Quarter"] != section_term.quarter):
            section_term = get_term_by_year_and_quarter(
                section_data["Year"], section_data["Quarter"])
        section = SectionReference(
            term=section_term,
            curriculum_abbr=section_data["CurriculumAbbreviation"],
            course_number=section_data["CourseNumber"],
            section_id=section_data["SectionID"],
            url=section_data["Href"])
        sections.append(section)
    return sections


def _get_sections_by_person_and_term(person,
                                     term,
                                     course_role,
                                     include_secondaries,
                                     future_terms,
                                     transcriptable_course,
                                     delete_flag):
    """
    Returns the response data for a search request containing the
    passed course_role and term (including secondaries).
    @param: future_terms: 0..400
    @param: transcriptable_course: 'yes', 'no', 'all'
    @param: delete_flag: ['active', 'suspended', 'withdrawn']
    """
    params = [
        ("reg_id", person.uwregid,),
        ("search_by", course_role,),
        ("quarter", term.quarter.lower(),),
        ("include_secondaries", 'on' if include_secondaries else ''),
        ("year", term.year,),
        ("future_terms", future_terms,),
        ("transcriptable_course", transcriptable_course,),
    ]

    if delete_flag is not None:
        if not isinstance(delete_flag, list):
            raise ValueError("delete_flag must be a list")
        params.append(("delete_flag", ','.join(sorted(delete_flag)),))

    url = "{}?{}".format(section_res_url_prefix, urlencode(params))
    return get_resource(url)


def get_last_section_by_instructor_and_terms(person,
                                             term,
                                             future_terms,
                                             transcriptable_course='all',
                                             delete_flag=['active']):
    try:
        raw_resp = _get_sections_by_person_and_term(person,
                                                    term,
                                                    "Instructor",
                                                    False,
                                                    future_terms,
                                                    transcriptable_course,
                                                    delete_flag)
    except DataFailureException as ex:
        if ex.status == 404:
            return None
        raise

    data_sections = raw_resp.get("Sections", [])

    if len(data_sections):
        raw_resp["Sections"] = data_sections[-1:]  # Keep the last section
        return _json_to_sectionref(raw_resp)[0]

    return None


def get_section_by_url(url,
                       include_instructor_not_on_time_schedule=True):
    """
    Returns a uw_sws.models.Section object
    for the passed section url.
    """
    if not course_url_pattern.match(url):
        raise InvalidSectionURL(url)

    return _json_to_section(
        get_resource(url),
        include_instructor_not_on_time_schedule=(
            include_instructor_not_on_time_schedule))


def get_section_by_label(label,
                         include_instructor_not_on_time_schedule=True):
    """
    Returns a uw_sws.models.Section object for
    the passed section label.
    """
    validate_section_label(label)

    url = "{}/{}.json".format(course_res_url_prefix,
                              encode_section_label(label))

    return get_section_by_url(url,
                              include_instructor_not_on_time_schedule)


def get_linked_sections(section,
                        include_instructor_not_on_time_schedule=True):
    """
    Returns a list of uw_sws.models.Section objects,
    representing linked sections for the passed section.
    """
    linked_sections = []

    for url in section.linked_section_urls:
        section = get_section_by_url(url,
                                     include_instructor_not_on_time_schedule)
        linked_sections.append(section)

    return linked_sections


def get_joint_sections(section,
                       include_instructor_not_on_time_schedule=True):
    """
    Returns a list of uw_sws.models.Section objects,
    representing joint sections for the passed section.
    """
    joint_sections = []

    for url in section.joint_section_urls:
        section = get_section_by_url(url,
                                     include_instructor_not_on_time_schedule)
        joint_sections.append(section)

    return joint_sections


def get_prefetch_for_section_data(section_data):
    """
    This will return a list of methods that can be called to prefetch (in
    threads) content that would be fetched while building the section.

    This depends on a good cache backend.  Without that, this will just double
    the work that's needed :(

    Each method is identified by a key, so they can be deduped if multiple
    sections want the same data, such as a common instructor.
    """
    prefetch = []
    for meeting_data in section_data["Meetings"]:
        for instructor_data in meeting_data["Instructors"]:
            pdata = instructor_data["Person"]
            if "RegID" in pdata and pdata["RegID"] is not None:
                prefetch.append(["person-{}".format(pdata["RegID"]),
                                 generic_prefetch(UWPWS.get_person_by_regid,
                                                  [pdata["RegID"]])])

    return prefetch


def _json_to_section(section_data,
                     term=None,
                     include_instructor_not_on_time_schedule=True):
    """
    Returns a section model created from the passed json.
    """
    section = Section()
    if term is not None and (
            term.year == int(section_data["Course"]["Year"]) and
            term.quarter == section_data["Course"]["Quarter"]):
        section.term = term
    else:
        section.term = get_term_by_year_and_quarter(
            section_data["Course"]["Year"],
            section_data["Course"]["Quarter"])

    section.curriculum_abbr = section_data["Course"][
        "CurriculumAbbreviation"]
    section.course_number = section_data["Course"]["CourseNumber"]
    section.course_title = section_data["CourseTitle"]
    section.course_title_long = section_data["CourseTitleLong"]
    section.course_campus = section_data["CourseCampus"]
    section.course_description = section_data["CourseDescription"]
    section.section_id = section_data["SectionID"]
    section.eos_cid = section_data.get("EOS_CID", None)
    section.institute_name = section_data.get("InstituteName", "")
    section.metadata = section_data.get("Metadata", "")
    section.primary_lms = section_data.get("PrimaryLMS", None)
    section.lms_ownership = section_data.get("LMSOwnership", None)
    section.is_independent_start = section_data.get("IsIndependentStart",
                                                    False)
    section.section_type = section_data["SectionType"]
    if "independent study" == section.section_type or\
       "IS" == section.section_type:
        is_independent_study = True
    else:
        is_independent_study = False

    section.is_independent_study = section_data.get(
        "IndependentStudy", is_independent_study)

    section.credit_control = section_data.get("CreditControl", "")
    section.end_date = str_to_date(section_data.get("EndDate"))
    section.start_date = str_to_date(section_data.get("StartDate"))
    section.class_website_url = section_data.get("ClassWebsiteUrl")

    if is_valid_sln(section_data.get("SLN")):
        section.sln = int(section_data["SLN"])

    _set_summer_term(section_data, section)
    section.delete_flag = section_data.get("DeleteFlag", "")
    section.current_enrollment = int(section_data['CurrentEnrollment'])

    section.limit_estimate_enrollment = int(
        section_data['LimitEstimateEnrollment'])
    section.limit_estimate_enrollment_indicator = section_data[
        'LimitEstimateEnrollmentIndicator']

    section.auditors = int(section_data['Auditors'])
    section.allows_secondary_grading = section_data["SecondaryGradingOption"]

    primary_section = section_data["PrimarySection"]
    if (primary_section is not None and
            primary_section["SectionID"] != section.section_id):
        section.is_primary_section = False
        section.primary_section_href = primary_section["Href"]
        section.primary_section_id = primary_section["SectionID"]
        section.primary_section_curriculum_abbr = primary_section[
            "CurriculumAbbreviation"]
        section.primary_section_course_number = primary_section[
            "CourseNumber"]
    else:
        section.is_primary_section = True

    section.linked_section_urls = []
    for linked_section_type in section_data["LinkedSectionTypes"]:
        for linked_section_data in linked_section_type["LinkedSections"]:
            url = linked_section_data["Section"]["Href"]
            section.linked_section_urls.append(url)

    section.joint_section_urls = []
    for joint_section_data in section_data.get("JointSections", []):
        url = joint_section_data["Href"]
        section.joint_section_urls.append(url)

    section.grading_system = section_data['GradingSystem']
    section.grade_submission_delegates = []
    for del_data in section_data["GradeSubmissionDelegates"]:
        try:
            delegate = GradeSubmissionDelegate(
                person=UWPWS.get_person_by_regid(del_data["Person"]["RegID"]),
                delegate_level=del_data["DelegateLevel"])
        except DataFailureException:
            delegate = GradeSubmissionDelegate(
                person=Person(uwregid=del_data["Person"]["RegID"],
                              display_name=del_data["Person"]["Name"])
            )
        section.grade_submission_delegates.append(delegate)

    section.meetings = []
    for meeting_data in section_data["Meetings"]:
        meeting = SectionMeeting()
        meeting.section = section
        meeting.term = section.term
        meeting.meeting_index = meeting_data["MeetingIndex"]
        meeting.meeting_type = meeting_data["MeetingType"]

        meeting.building = meeting_data["Building"]
        if meeting_data["BuildingToBeArranged"]:
            meeting.building_to_be_arranged = True
        else:
            meeting.building_to_be_arranged = False

        meeting.room_number = meeting_data["RoomNumber"]
        if meeting_data["RoomToBeArranged"]:
            meeting.room_to_be_arranged = True
        else:
            meeting.room_to_be_arranged = False

        if meeting_data["DaysOfWeekToBeArranged"]:
            meeting.days_to_be_arranged = True
        else:
            meeting.days_to_be_arranged = False

        for day_data in meeting_data["DaysOfWeek"]["Days"]:
            attribute = "meets_{}".format(day_data["Name"].lower())
            setattr(meeting, attribute, True)

        if (len(meeting_data["StartTime"]) and
                meeting_data["StartTime"] != "00:00:00"):
            meeting.start_time = meeting_data["StartTime"]
            # in case of "18:00:00", only keep hh:mm
            if len(meeting.start_time) > 5:
                meeting.start_time = meeting.start_time[:5]

        if (len(meeting_data["EndTime"]) and
                meeting_data["EndTime"] != "00:00:00"):
            meeting.end_time = meeting_data["EndTime"]
            if len(meeting.end_time) > 5:
                meeting.end_time = meeting.end_time[:5]

        meeting.eos_start_date = str_to_date(meeting_data.get("EOS_StartDate"))
        meeting.eos_end_date = str_to_date(meeting_data.get("EOS_EndDate"))

        meeting.instructors = []
        for instructor_data in meeting_data["Instructors"]:
            # TSPrint: True
            # Instructor information currently listed on the Time Schedule
            if (instructor_data["TSPrint"] or
                    include_instructor_not_on_time_schedule):
                pdata = instructor_data["Person"]

                if "RegID" in pdata and pdata["RegID"] is not None:
                    try:
                        instructor = UWPWS.get_person_by_regid(pdata["RegID"])
                    except Exception:
                        instructor = Person(uwregid=pdata["RegID"],
                                            display_name=pdata["Name"])
                    instructor.TSPrint = instructor_data["TSPrint"]
                    meeting.instructors.append(instructor)

        section.meetings.append(meeting)

    section.final_exam = None
    if "FinalExam" in section_data and section_data["FinalExam"] is not None:
        if "MeetingStatus" in section_data["FinalExam"]:
            final_exam = FinalExam()
            final_data = section_data["FinalExam"]
            status = final_data["MeetingStatus"]
            # MeetingStatus values:
            # 0 - default final exam meeting date/time has not been confirmed
            # 1 - no final exam or no traditional final exam
            # 2 - confirmed, at the default final exam date/time/location
            # 3 - confirmed, but at a different date/time/location

            final_exam.no_exam_or_nontraditional = False
            final_exam.is_confirmed = False

            if (status == "2") or (status == "3"):
                final_exam.is_confirmed = True
            elif status == "1":
                final_exam.no_exam_or_nontraditional = True

            final_exam.building = final_data["Building"]
            final_exam.room_number = final_data["RoomNumber"]

            final_format = "%Y-%m-%d : %H:%M"

            strptime = datetime.strptime
            if final_data["Date"] and final_data["Date"] != "0000-00-00":
                if final_data["StartTime"]:
                    start_string = "{} : {}".format(final_data["Date"],
                                                    final_data["StartTime"])
                    final_exam.start_date = strptime(start_string,
                                                     final_format)

                if final_data["EndTime"]:
                    end_string = "{} : {}".format(final_data["Date"],
                                                  final_data["EndTime"])
                    try:
                        final_exam.end_date = strptime(
                            end_string, final_format)
                    except ValueError:
                        logger.info('bad final EndTime: {}'.format(end_string))
                        final_exam.end_date = None

            final_exam.clean_fields()
            section.final_exam = final_exam

    if (section_data.get("TimeScheduleComments") and
            section_data["TimeScheduleComments"].get("SectionComments")):
        comments = section_data["TimeScheduleComments"]["SectionComments"]
        if comments.get("Lines"):
            for line in comments["Lines"]:
                if is_remote(line):
                    section.is_remote = True
                    break

    return section


def is_remote(comment_dict):
    return (comment_dict.get("Text") and
            "OFFERED VIA REMOTE" in comment_dict["Text"])


def is_a_term(str):
    return str is not None and len(str) > 0 and\
        str.lower() == Section.SUMMER_A_TERM


def is_b_term(str):
    return str is not None and len(str) > 0 and\
        str.lower() == Section.SUMMER_B_TERM


def is_full_summer_term(str):
    return str is not None and len(str) > 0 and\
        str.lower() == Section.SUMMER_FULL_TERM


def is_valid_section_label(label):
    try:
        return section_label_pattern.match(label) is not None
    except TypeError:
        return False


def _set_summer_term(section_data, section):
    section.summer_term = section_data.get("SummerTerm", "")
    if (section.term.is_summer_quarter() and len(section.summer_term) == 0 and
            section.is_campus_pce() and not section.for_credit()):
        section.summer_term = "Full-term"
        # PCE non-credit summer term courses are full-term by default
