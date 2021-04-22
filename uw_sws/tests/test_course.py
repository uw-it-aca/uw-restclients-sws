# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.course import validate_course_label, get_course_by_label
from uw_sws.exceptions import InvalidCourseID


@fdao_pws_override
@fdao_sws_override
class SWSTestCourseData(TestCase):
    def test_validate(self):
        good_label = "2019,winter,CSE,142"
        bad_label = "winter,2019,142,CSE"
        self.assertRaises(InvalidCourseID, validate_course_label, bad_label)
        validate_course_label(good_label)

    def test_get_by_label(self):
        course = get_course_by_label("2013,spring,CSE,142")

        course_resp = {"curriculum_abbr": "CSE",
                       "course_number": "142",
                       "course_title": "COMPUTER PRGRMNG I",
                       "course_title_long": "Computer Programming I",
                       "course_campus": "Seattle",
                       "course_description": "Basic programming-in-the-small "
                                             "abilities and concepts including"
                                             " procedural programming (methods"
                                             ", parameters, return, values),"
                                             " basic control structures "
                                             "(sequence, if/else, for loop,"
                                             " while loop), file processing,"
                                             " arrays, and an introduction to"
                                             " defining objects. Intended for"
                                             " students without prior "
                                             "programming experience. "
                                             "Offered: AWSpS."}
        self.assertEqual(course.json_data(), course_resp)

        self.assertIsNone(get_course_by_label("2013,spring,FOO,123"))

        self.assertIsNotNone(get_course_by_label("2013,spring,ATMO S,142"))
