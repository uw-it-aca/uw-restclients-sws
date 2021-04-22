# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from restclients_core.exceptions import DataFailureException
from uw_sws.term import get_current_term, get_next_term, get_previous_term
from uw_sws.term import get_term_by_year_and_quarter
from uw_sws.registration import get_schedule_by_regid_and_term


@fdao_pws_override
@fdao_sws_override
class SWSTestScheduleData(TestCase):
    def test_bad_response(self):
        term = get_term_by_year_and_quarter(2012, 'summer')

        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9936CCB8F66711D5BE060004AC494FFE",
                          term)

    def test_sws_schedule_data(self):
        # Valid data, shouldn't throw exceptions
        term = get_previous_term()
        get_schedule_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)

        term = get_current_term()
        get_schedule_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)

        term = get_next_term()
        get_schedule_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)

        term = get_term_by_year_and_quarter(2012, 'summer')
        get_schedule_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)
        term = get_current_term()

        # Bad data, should throw exceptions
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFF",
                          term)

        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFX",
                          term)

        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "javerage",
                          term)

        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "",
                          term)

        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          " ",
                          term)

        term.year = None
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.year = 1929
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.year = 2399
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.year = 0
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.year = -2012
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.quarter = "spring"
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.quarter = "fall"
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.quarter = ""
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.quarter = " "
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)

        term.quarter = "Spring"
        self.assertRaises(DataFailureException,
                          get_schedule_by_regid_and_term,
                          "9136CCB8F66711D5BE060004AC494FFE",
                          term)
