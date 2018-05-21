"""
Interfacing with the Student Web Service, for Section and Course resources.
"""
import logging
import re
from datetime import datetime
from dateutil.parser import parse
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
from restclients_core.thread import generic_prefetch
from uw_sws.exceptions import InvalidSectionID, InvalidSectionURL
from restclients_core.exceptions import DataFailureException
from uw_sws import get_resource, encode_section_label, UWPWS
from uw_sws.term import get_term_by_year_and_quarter
from uw_sws.models import (Section, SectionReference, FinalExam,
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
        raise InvalidSectionID("Invalid section label: %s" % label)


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
    return _get_sections_by_person_and_term(person,
                                            term,
                                            "Instructor",
                                            include_secondaries,
                                            future_terms,
                                            transcriptable_course,
                                            delete_flag)


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
    return _get_sections_by_person_and_term(person,
                                            term,
                                            "GradeSubmissionDelegate",
                                            include_secondaries,
                                            future_terms,
                                            transcriptable_course,
                                            delete_flag)


def get_sections_by_curriculum_and_term(curriculum, term):
    """
    Returns a list of uw_sws.models.SectionReference objects
    for the passed curriculum and term.
    """
    url = "%s?%s" % (section_res_url_prefix,
                     urlencode([("curriculum_abbreviation", curriculum.label,),
                                ("quarter", term.quarter.lower(),),
                                ("year", term.year,),
                                ]))
    return _json_to_sectionref(get_resource(url), term)


def get_sections_by_building_and_term(building, term):
    """
    Returns a list of uw_sws.models.SectionReference objects
    for the passed building and term.
    """
    url = "%s?%s" % (section_res_url_prefix,
                     urlencode([
                                ("quarter", term.quarter.lower(),),
                                ("facility_code", building,),
                                ("year", term.year,),
                                ]))
    return _json_to_sectionref(get_resource(url), term)


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
    url = "%s?%s" % (section_res_url_prefix, urlencode(params))

    sections = []
    while url is not None:
        data = get_resource(url)
        sections.extend(_json_to_sectionref(data, term))

        url = None
        if data.get("Next") is not None:
            url = data.get("Next").get("Href", None)

    return sections


def _json_to_sectionref(data, aterm):
    """
    Returns a list of SectionReference object created from
    the passed json data.
    """
    sections = []
    for section_data in data.get("Sections", []):
        section = SectionReference(
            term=aterm,
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
    Returns a list of uw_sws.models.SectionReference object
    for the passed course_role and term (including secondaries).
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

    url = "%s?%s" % (section_res_url_prefix, urlencode(params))

    return _json_to_sectionref(get_resource(url), term)


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

    url = "%s/%s.json" % (
        course_res_url_prefix,
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
                prefetch.append(["person-%s" % pdata["RegID"],
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

    if "StartDate" in section_data and\
       len(section_data["StartDate"]) > 0:
        section.start_date = parse(section_data["StartDate"]).date()

    if "EndDate" in section_data and\
       len(section_data["EndDate"]) > 0:
        section.end_date = parse(section_data["EndDate"]).date()

    section.class_website_url = section_data["ClassWebsiteUrl"]

    if is_valid_sln(section_data["SLN"]):
        section.sln = int(section_data["SLN"])
    else:
        section.sln = 0

    if "SummerTerm" in section_data:
        section.summer_term = section_data["SummerTerm"]
    else:
        section.summer_term = ""

    section.delete_flag = section_data["DeleteFlag"]
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
        delegate = GradeSubmissionDelegate(
            person=UWPWS.get_person_by_regid(del_data["Person"]["RegID"]),
            delegate_level=del_data["DelegateLevel"])
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
            attribute = "meets_%s" % day_data["Name"].lower()
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
                    start_string = "%s : %s" % (final_data["Date"],
                                                final_data["StartTime"])
                    final_exam.start_date = strptime(start_string,
                                                     final_format)

                if final_data["EndTime"]:
                    end_string = "%s : %s" % (final_data["Date"],
                                              final_data["EndTime"])
                    try:
                        final_exam.end_date = strptime(
                            end_string, final_format)
                    except ValueError:
                        logger.info('bad final EndTime: %s' % end_string)
                        final_exam.end_date = None

            final_exam.clean_fields()
            section.final_exam = final_exam

    return section


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
