# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from restclients_core.exceptions import DataFailureException
from uw_sws.degree import get_degrees_by_regid


@fdao_sws_override
class AdviserTest(TestCase):
    def test_get_degrees(self):
        degrees = get_degrees_by_regid(
            "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEquals(len(degrees), 1)
        self.assertEquals(
            degrees[0].json_data(),
            {
                'campus': 'SEATTLE',
                'diploma_mail': 0,
                'diploma_mail_to_local_address': False,
                'has_applied': True,
                'is_admin_hold': False,
                'is_granted': False,
                'is_incomplete': False,
                'level': 1,
                'name_on_diploma': 'John Joseph Average',
                'quarter': 'spring',
                'status': 5,
                'title': 'BACHELOR OF ARTS (POLITICAL SCIENCE)',
                'type': 1,
                'year': 2014
            })
        self.assertIsNotNone(str(degrees[0]))
        degrees[0].status = 9
        self.assertTrue(degrees[0].is_granted())
        degrees[0].status = 1
        self.assertTrue(degrees[0].is_admin_hold())
        degrees[0].status = 2
        self.assertTrue(degrees[0].is_incomplete())

    def test_error_case(self):
        self.assertRaises(
            DataFailureException, get_degrees_by_regid,
            "00000000000000000000000000000001")
