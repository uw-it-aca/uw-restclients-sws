# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from restclients_core.exceptions import DataFailureException
from uw_sws.adviser import get_advisers_by_regid


@fdao_sws_override
class AdviserTest(TestCase):
    def test_get_advisers(self):
        advisers = get_advisers_by_regid(
            "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEquals(len(advisers), 1)
        self.assertEquals(advisers[0].uwnetid, "uwhonors")
        self.assertTrue(advisers[0].is_honors_program())
        self.assertEquals(
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
             'timestamp': '2020-03-24 13:07:14'})
        self.assertIsNotNone(str(advisers))

    def test_error_case(self):
        self.assertRaises(
            DataFailureException, get_advisers_by_regid,
            "00000000000000000000000000000001")
