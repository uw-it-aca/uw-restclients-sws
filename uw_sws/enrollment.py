# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the Student Web Service, Enrollment resource.
"""
import logging
from urllib.parse import urlencode
from restclients_core.exceptions import DataFailureException
from uw_sws.models import StudentGrades, StudentCourseGrade, Enrollment, Major
from uw_sws import get_resource, UWPWS
from uw_sws.section import get_section_by_url
from uw_sws.term import Term, get_term_by_year_and_quarter
from uw_sws.worker import Worker


logger = logging.getLogger(__name__)
enrollment_res_url_prefix = "/student/v5/enrollment"
enrollment_search_url_prefix = "/student/v5/enrollment.json"


def get_grades_by_regid_and_term(regid, term):
    """
    Returns a StudentGrades model for the regid and term.
    """
    url = "{}/{},{},{}.json".format(enrollment_res_url_prefix,
                                    term.year,
                                    term.quarter,
                                    regid)
    logger.debug(f"Get grades {url}")
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
    logger.debug(f"Enrollment search {url}")
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
    if ("Term" in term_enro_json_data and
            "Year" in term_enro_json_data["Term"] and
            "Quarter" in term_enro_json_data["Term"]):
        term_quarter = term_enro_json_data["Term"]["Quarter"]
        term_year = int(term_enro_json_data["Term"]["Year"])
        try:
            return get_term_by_year_and_quarter(term_year, term_quarter)
        except DataFailureException as ex:
            logger.error("Invalid Term in Enrollment payload: {}".format(ex))
            return Term(term_year, term_quarter)
    logger.error(
        "Invalid Term in Enrollment payload: {}".format(
            term_enro_json_data))
    return None


def _json_to_enrollment_list(json_data,
                             include_unfinished_pce_course):
    enrollment_list = []
    for term_enr in json_data.get("Enrollments", []):
        term = _get_term(term_enr)
        # no longer a meaningful enrollment record without the term
        if term:
            enrollment = Enrollment(
                data=term_enr,
                term=term,
                include_unfinished_pce_course_reg=include_unfinished_pce_course
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


def get_majors_by_regid_and_term(regid, term):
    """
    A light weight function to get student term specific majors, class level
    """
    url = (
        f"{enrollment_res_url_prefix}/{term.year},{term.quarter},{regid}.json"
    )
    logger.debug(f"Get majors {url}")
    return _json_to_majors(get_resource(url))


def _json_to_majors(data):
    majors = []
    major_items = data.get("Majors")
    if major_items:
        for item in major_items:
            majors.append(Major(data=item))

    return {
        "class_code": data.get("ClassCode"),
        "class_level": data.get("ClassLevel"),
        "majors": majors,
    }


class StudentMajorGetter(Worker):
    """
    Get major and class level for each student in regid_set and the given term
    """

    def __init__(self, regid_set, term):
        self.regid_list = list(regid_set or [])
        self.term = term

    def get_task_ids(self):
        return self.regid_list

    def task(self, tid):
        return get_majors_by_regid_and_term(tid, self.term)
