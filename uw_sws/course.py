# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the Student Web Service, for Section and Course resources.
"""
import logging
import re
from uw_sws.exceptions import InvalidCourseID
from restclients_core.exceptions import DataFailureException
from uw_sws import get_resource, encode_section_label
from uw_sws.models import Course

course_url_pattern = re.compile(r'^\/student\/v5\/course\/')
course_res_url_prefix = "/student/v5/course"
course_label_pattern = re.compile(
    r'^[1-9]\d{3},'                      # year
    '(?:winter|spring|summer|autumn),'  # quarter
    r'[\w& ]+,'                          # curriculum
    r'\d{3}',                           # course number
    re.VERBOSE
)
logger = logging.getLogger(__name__)


def validate_course_label(label):
    if label is None or course_label_pattern.match(label) is None:
        raise InvalidCourseID("Invalid Course label: {}".format(label))


def get_course_by_label(label):
    validate_course_label(label)
    label = encode_section_label(label)
    try:
        return _json_to_courseref(_get_course_by_label(label))
    except DataFailureException as ex:
        if ex.status == 404:
            return None
        raise


def _get_course_by_label(label):
    """
    Returns the response data for a search request containing the
    passed course label.
    """

    url = "{}/{}.json".format(course_res_url_prefix, label)
    return get_resource(url)


def _json_to_courseref(data):
    """
    Returns a Course object created from the passed json data.
    """
    course = Course()
    course.curriculum_abbr = data['Curriculum']['CurriculumAbbreviation']
    course.course_number = data['CourseNumber']
    course.course_title = data['CourseTitle']
    course.course_title_long = data['CourseTitleLong']
    course.course_campus = data['CourseCampus']
    course.course_description = data['CourseDescription']
    return course
