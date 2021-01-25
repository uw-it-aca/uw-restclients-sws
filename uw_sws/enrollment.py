"""
Interfacing with the Student Web Service, Enrollment resource.
"""
import logging
import re
from urllib.parse import urlencode
from uw_sws.models import (StudentGrades, StudentCourseGrade, Enrollment,
                           Major, Minor, SectionReference, Term, Registration)
from uw_sws import get_resource, UWPWS
from uw_sws.section import get_section_by_url
from uw_sws.term import get_term_by_year_and_quarter


logger = logging.getLogger(__name__)
enrollment_res_url_prefix = "/student/v5/enrollment"
enrollment_search_url_prefix = "/student/v5/enrollment.json?reg_id="


def get_grades_by_regid_and_term(regid, term):
    """
    Returns a StudentGrades model for the regid and term.
    """
    url = "{}/{},{},{}.json".format(enrollment_res_url_prefix,
                                    term.year,
                                    term.quarter,
                                    regid)
    return _json_to_grades(get_resource(url), regid, term)


def _json_to_grades(data, regid, term):
    grades = StudentGrades()
    grades.term = term
    grades.user = UWPWS.get_person_by_regid(regid)

    grades.grade_points = data["QtrGradePoints"]
    grades.credits_attempted = data["QtrGradedAttmp"]
    grades.non_grade_credits = data["QtrNonGrdEarned"]
    grades.grades = []

    for registration in data["Registrations"]:
        grade = StudentCourseGrade()
        grade.grade = registration["Grade"]
        grade.credits = registration["Credits"].replace(" ", "")
        grade.section = get_section_by_url(registration["Section"]["Href"])
        grades.grades.append(grade)

    return grades


def _enrollment_search(regid, verbose, transcriptable, changed_since_date):
    """
    See SWS Enrollment search resource spec at:
    https://wiki.cac.washington.edu/x/_qjeAw
    :return: search result json data
    """
    url = "{}{}&{}".format(enrollment_search_url_prefix,
                           regid,
                           urlencode(
                               {"verbose": verbose,
                                "transcriptable_course": transcriptable,
                                "changed_since_date": changed_since_date}))
    return get_resource(url)


def enrollment_search_by_regid(regid,
                               verbose='true',
                               transcriptable_course='all',
                               changed_since_date='',
                               include_unfinished_pce_course_reg=True):
    """
    :return: a dictionary of {Term: Enrollment}
    """
    return _json_to_term_enrollment_dict(
        _enrollment_search(regid, verbose, transcriptable_course,
                           changed_since_date),
        include_unfinished_pce_course_reg)


def _json_to_term_enrollment_dict(json_data,
                                  include_unfinished_pce_course_reg):
    term_enrollment_dict = {}
    if "Enrollments" not in json_data:
        return term_enrollment_dict
    for term_enro in json_data["Enrollments"]:
        if "Term" in term_enro and\
                "Year" in term_enro["Term"] and\
                "Quarter" in term_enro["Term"]:
            term = get_term_by_year_and_quarter(term_enro["Term"]["Year"],
                                                term_enro["Term"]["Quarter"])
            enrollment = _json_to_enrollment(term_enro,
                                             term,
                                             include_unfinished_pce_course_reg)
            term_enrollment_dict[term] = enrollment
    return term_enrollment_dict


def get_enrollment_by_regid_and_term(regid, term):
    url = "{}/{},{},{}.json".format(enrollment_res_url_prefix,
                                    term.year,
                                    term.quarter,
                                    regid)
    return _json_to_enrollment(get_resource(url), term)


def _json_to_enrollment(json_data,
                        term,
                        include_unfinished_pce_course_reg=True):
    enrollment = Enrollment()
    enrollment.registrations = []
    enrollment.regid = json_data['RegID']
    enrollment.class_level = json_data['ClassLevel']
    enrollment.is_honors = json_data['HonorsProgram']

    value = json_data['PendingMajorChange']
    enrollment.has_pending_major_change = value

    enrollment.is_enroll_src_pce = is_src_location_pce(json_data,
                                                       ENROLLMENT_SOURCE_PCE)

    registrations = json_data.get('Registrations', [])
    enrollment.is_registered = len(registrations) > 0
    if enrollment.is_registered:
        enrollment.unf_pce_courses = {}

        for reg_json in registrations:
            registration = Registration(data=reg_json)
            registration.section_ref = _json_to_section_ref(reg_json, term)
            enrollment.registrations.append(registration)

            if include_unfinished_pce_course_reg:
                # dictionary {section_label: Registration}
                if is_unfinished_pce_course(reg_json):
                    key = registration.section_ref.section_label()
                    enrollment.unf_pce_courses[key] = registration

    enrollment.majors = []
    if json_data.get('Majors') is not None and len(json_data['Majors']) > 0:
        for major in json_data['Majors']:
            enrollment.majors.append(_json_to_major(major))

    enrollment.minors = []
    if json_data.get('Minors') is not None and len(json_data['Minors']) > 0:
        for minor in json_data['Minors']:
            enrollment.minors.append(_json_to_minor(minor))
    return enrollment


def has_start_end_dates(registration_json_data):
    start_date = registration_json_data.get('StartDate')
    end_date = registration_json_data.get('EndDate')
    return (start_date is not None and len(start_date) > 0 and
            end_date is not None and len(start_date) > 0)


def is_unfinished_pce_course(registration):
    return has_start_end_dates(registration) and\
        is_src_location_pce(registration, REGISTRATION_SOURCE_PCE)


def _json_to_section_ref(reg_json, term):
    return SectionReference(
        term=term,
        curriculum_abbr=reg_json['Section']['CurriculumAbbreviation'],
        course_number=reg_json['Section']['CourseNumber'],
        section_id=reg_json['Section']['SectionID'],
        url=reg_json['Section']['Href'])


def _json_to_major(json_data):
    major = Major()
    major.degree_abbr = json_data['Abbreviation']
    try:
        major.college_abbr = json_data['CollegeAbbreviation']
    except KeyError:
        major.college_abbr = ""
    try:
        major.college_full_name = json_data['CollegeFullName']
    except KeyError:
        major.college_full_name = ""

    major.degree_name = json_data['DegreeName']
    major.degree_level = int(json_data['DegreeLevel'])
    major.full_name = json_data['FullName']
    major.major_name = json_data['MajorName']
    major.short_name = json_data['ShortName']
    major.campus = json_data['Campus']
    return major


def _json_to_minor(json_data):
    minor = Minor()
    minor.abbr = json_data['Abbreviation']
    minor.campus = json_data['CampusName']
    minor.name = json_data['Name']
    minor.full_name = json_data['FullName']
    minor.short_name = json_data['ShortName']
    return minor


ENROLLMENT_SOURCE_PCE = re.compile('^EnrollmentSourceLocation=', re.I)
REGISTRATION_SOURCE_PCE = re.compile('^RegistrationSourceLocation=', re.I)


def is_src_location_pce(json_data, pattern):
    try:
        return (re.match(pattern, json_data['Metadata']) is not None and
                "EOS" in json_data['Metadata'])
    except KeyError:
        return False


def get_enrollment_history_by_regid(regid,
                                    verbose='true',
                                    transcriptable_course='all',
                                    changed_since_date='',
                                    include_unfinished_pce_course_reg=False):
    """
    :return: a complete chronological list of all the enrollemnts
    [Enrollment], where the Enrollment object has a term element.
    """
    return _json_to_enrollment_list(
        _enrollment_search(regid, verbose, transcriptable_course,
                           changed_since_date),
        include_unfinished_pce_course_reg)


def _json_to_enrollment_list(json_data,
                             include_unfinished_pce_course_reg):
    term_enrollment_list = []
    if "Enrollments" not in json_data:
        return term_enrollment_list
    for term_enro in json_data["Enrollments"]:
        if "Term" in term_enro and\
           "Year" in term_enro["Term"] and\
           "Quarter" in term_enro["Term"]:
            term = get_term_by_year_and_quarter(term_enro["Term"]["Year"],
                                                term_enro["Term"]["Quarter"])
            enrlmt = _json_to_enrollment(term_enro,
                                         term,
                                         include_unfinished_pce_course_reg)
            enrlmt.term = term
            term_enrollment_list.append(enrlmt)
    return term_enrollment_list
