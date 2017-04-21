"""
Interfacing with the Student Web Service, Enrollment resource.
"""
import logging
import re
from uw_pws import PWS
from uw_sws.models import (StudentGrades, StudentCourseGrade, Enrollment,
                           Major, Minor, SectionReference, Term,
                           IndependentStartSectionReference)
from uw_sws import get_resource, parse_sws_date
from uw_sws.section import get_section_by_url
from uw_sws.term import get_term_by_year_and_quarter


logger = logging.getLogger(__name__)
enrollment_res_url_prefix = "/student/v5/enrollment"
enrollment_search_url_prefix = "/student/v5/enrollment.json?reg_id="


def get_grades_by_regid_and_term(regid, term):
    """
    Returns a StudentGrades model for the regid and term.
    """
    url = "%s/%s,%s,%s.json" % (enrollment_res_url_prefix,
                                term.year,
                                term.quarter,
                                regid)
    return _json_to_grades(get_resource(url), regid, term)


def _json_to_grades(data, regid, term):
    grades = StudentGrades()
    grades.term = term
    grades.user = PWS().get_person_by_regid(regid)

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


def enrollment_search_by_regid(regid,
                               verbose='true',
                               transcriptable_course='all',
                               changed_since_date=''):
    """
    See SWS Enrollment search resource spec at:
    https://wiki.cac.washington.edu/x/_qjeAw
    :return: a dictionary of {Term: Enrollment}
    """
    url = "%s%s&verbose=%s&transcriptable_course=%s&changed_since_date=%s" %\
        (enrollment_search_url_prefix,
         regid,
         verbose,
         transcriptable_course,
         changed_since_date)
    return _json_to_term_enrollment_dict(get_resource(url))


def _json_to_term_enrollment_dict(json_data):
    term_enrollment_dict = {}
    if "Enrollments" not in json_data:
        return term_enrollment_dict
    for term_enro in json_data["Enrollments"]:
        if "Term" in term_enro and\
                "Year" in term_enro["Term"] and\
                "Quarter" in term_enro["Term"]:
            term = Term(year=term_enro["Term"]["Year"],
                        quarter=term_enro["Term"]["Quarter"].lower())
            enrollment = _json_to_enrollment(term_enro, term)
            term_enrollment_dict[term] = enrollment
    return term_enrollment_dict


def get_enrollment_by_regid_and_term(regid, term):
    url = "%s/%s,%s,%s.json" % (enrollment_res_url_prefix,
                                term.year,
                                term.quarter,
                                regid)
    return _json_to_enrollment(get_resource(url), term)


def _json_to_enrollment(json_data, term):
    enrollment = Enrollment()
    enrollment.regid = json_data['RegID']
    enrollment.class_level = json_data['ClassLevel']
    enrollment.is_honors = json_data['HonorsProgram']
    enrollment.is_enroll_src_pce = is_src_location_pce(json_data,
                                                       ENROLLMENT_SOURCE_PCE)

    enrollment.independent_start_sections = []
    if json_data.get('Registrations') is not None and\
            len(json_data['Registrations']) > 0:
        for registration in json_data['Registrations']:
            if registration.get('IsIndependentStart'):
                enrollment.independent_start_sections.append(
                    _json_to_independent_start_section(registration, term))

    enrollment.majors = []
    if json_data.get('Majors') is not None and len(json_data['Majors']) > 0:
        for major in json_data['Majors']:
            enrollment.majors.append(_json_to_major(major))

    enrollment.minors = []
    if json_data.get('Minors') is not None and len(json_data['Minors']) > 0:
        for minor in json_data['Minors']:
            enrollment.minors.append(_json_to_minor(minor))
    return enrollment


def _json_to_independent_start_section(json_data, aterm):
    is_section = IndependentStartSectionReference()
    is_section.section_ref = SectionReference(
        term=aterm,
        curriculum_abbr=json_data['Section']['CurriculumAbbreviation'],
        course_number=json_data['Section']['CourseNumber'],
        section_id=json_data['Section']['SectionID'],
        url=json_data['Section']['Href']
        )
    is_section.feebase_type = json_data['FeeBaseType']
    try:
        is_section.end_date = parse_sws_date(json_data['EndDate'])
    except Exception:
        is_section.end_date = ""

    try:
        is_section.start_date = parse_sws_date(json_data['StartDate'])
    except Exception:
        is_section.start_date = ""

    is_section.is_reg_src_pce = is_src_location_pce(json_data,
                                                    REGISTRATION_SOURCE_PCE)
    return is_section


def _json_to_major(json_data):
    major = Major()
    major.degree_abbr = json_data['Abbreviation']
    major.degree_name = json_data['DegreeName']
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
