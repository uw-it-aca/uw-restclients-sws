# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the Student Web Service, Enrollment resource.
"""
from urllib.parse import urlencode
from uw_sws.models import StudentGrades, StudentCourseGrade, Enrollment
from uw_sws import get_resource, UWPWS, DAO
from uw_sws.section import get_section_by_url
from uw_sws.term import (
    Term, get_term_by_year_and_quarter, get_current_term)


enrollment_res_url_prefix = "/student/v5/enrollment"
enrollment_search_url_prefix = "/student/v5/enrollment.json"
ENROLLMENT_CUTOFF_DELTA = 20   # SWS PROD limit


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


def _enrollment_search(regid,
                       verbose=True,
                       transcriptable="all",
                       changed_since_date=None):
    """
    See SWS Enrollment search resource spec at:
    https://wiki.cac.washington.edu/x/_qjeAw
    :return: search result json data
    """
    params = {
        "reg_id": regid,
        "verbose": "true" if verbose else "",
        "transcriptable_course": transcriptable,
        "changed_since_date": changed_since_date if (
            changed_since_date is not None) else "",
    }
    url = "{}?{}".format(enrollment_search_url_prefix, urlencode(params))
    return get_resource(url)


def enrollment_search_by_regid(regid,
                               verbose=True,
                               transcriptable_course="all",
                               changed_since_date=None,
                               include_unfinished_pce_course_reg=True):
    """
    :return: a dictionary of {Term: Enrollment}
    """
    results = _enrollment_search(
        regid, verbose, transcriptable_course, changed_since_date)
    return _json_to_term_enrollment_dict(
        results, include_unfinished_pce_course_reg)


def _get_term(term_enro_json_data):
    current_year = get_current_term().year
    if ("Term" in term_enro_json_data and
            "Year" in term_enro_json_data["Term"] and
            "Quarter" in term_enro_json_data["Term"]):
        term_quarter = term_enro_json_data["Term"]["Quarter"]
        term_year = int(term_enro_json_data["Term"]["Year"])
        if (DAO.get_implementation().is_live() and
                current_year - term_year > ENROLLMENT_CUTOFF_DELTA):
            return Term(term_year, term_quarter)
        return get_term_by_year_and_quarter(term_year, term_quarter)
    return None


def _json_to_enrollment_list(json_data,
                             include_unfinished_pce_course_reg):
    enrollment_list = []
    for term_enr in json_data.get("Enrollments", []):
        enrollment = Enrollment(
            data=term_enr,
            term=_get_term(term_enr),
            include_unfinished_pce_course_reg=include_unfinished_pce_course_reg
        )
        enrollment_list.append(enrollment)
    return enrollment_list


def _json_to_term_enrollment_dict(json_data,
                                  include_unfinished_pce_course_reg):
    enrollment_dict = {}
    for enrollment in _json_to_enrollment_list(
            json_data, include_unfinished_pce_course_reg):
        enrollment_dict[enrollment.term] = enrollment
    return enrollment_dict


def get_enrollment_by_regid_and_term(regid, term):
    term_enrollment_dict = enrollment_search_by_regid(regid)
    return term_enrollment_dict.get(term)


def get_enrollment_history_by_regid(regid,
                                    verbose=True,
                                    transcriptable_course='all',
                                    changed_since_date=None,
                                    include_unfinished_pce_course_reg=False):
    """
    :return: a complete chronological list of all the enrollemnts
    [Enrollment], where the Enrollment object has a term element.
    """
    results = _enrollment_search(
        regid, verbose, transcriptable_course, changed_since_date)
    return _json_to_enrollment_list(
        results, include_unfinished_pce_course_reg)
