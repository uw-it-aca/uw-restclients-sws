# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

from restclients_core.exceptions import DataFailureException

from uw_sws.adviser import (
    get_adviser_by_netid,
    get_adviser_by_regid,
    get_advisers_by_student_regid,
    get_all_advisers,
    get_assignments_by_adviser_regid,
)
from uw_sws.util import fdao_sws_override


@fdao_sws_override
class AdviserTest(TestCase):
    def test_get_advisers_by_student(self):
        advisers = get_advisers_by_student_regid(
            "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(len(advisers), 1)
        self.assertEqual(advisers[0].uwnetid, "uwhonors")
        self.assertTrue(advisers[0].is_honors_program())
        self.assertEqual(
            advisers[0].json_data(),
            {'booking_url': 'https://honors.uw.edu/advising/',
             'email_address': 'uwhonors@uw.edu',
             'full_name': 'UNIVERSITY HONORS PROGRAM',
             'metadata': "AcademicAdviserSourceKey=UAA;",
             'pronouns': "he/him/his",
             'is_active': True,
             'is_dept_adviser': False,
             'phone_number': '+1 206 543-7444',
             'program': 'UW Honors',
             'is_honors_program': True,
             'regid': '24A20F50AE3511D68CBC0004AC494FFE',
             'uwnetid': 'uwhonors',
             'timestamp': '2020-03-24T13:07:14'})
        self.assertIsNotNone(str(advisers))

    def test_invalid_student_regid(self):
        self.assertRaises(
            DataFailureException, get_advisers_by_student_regid,
            "00000000000000000000000000000001")


@fdao_sws_override
class AdviserSearchTest(TestCase):
    def test_get_adviser_by_regid(self):
        adviser = get_adviser_by_regid("9136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(adviser.uwregid, "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(adviser.full_name, "J Average")

        adviser = get_adviser_by_regid("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        self.assertIsNone(adviser)

    def test_get_adviser_by_netid(self):
        adviser = get_adviser_by_netid("javerage")
        self.assertEqual(adviser.uwregid, "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(adviser.full_name, "J Average")

        adviser = get_adviser_by_netid("xxxxxxx")
        self.assertIsNone(adviser)

    def test_get_all_advisers(self):
        advisors = get_all_advisers()
        self.assertEqual(len(advisors), 3)
        self.assertEqual(advisors[0].uwregid, "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(advisors[1].uwregid, "705C657CAE3411D689DA0004AC494FFE")
        self.assertEqual(advisors[2].uwregid, "705C67D4AE3411D689DA0004AC494FFE")


@fdao_sws_override
class AdviserAssignmentTest(TestCase):
    def test_get_assignments_by_adviser_regid(self):
        assignments = get_assignments_by_adviser_regid(
            '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(len(assignments), 3)

        assignments = get_assignments_by_adviser_regid(
            '705C67D4AE3411D689DA0004AC494FFE')
        self.assertEqual(len(assignments), 0)
