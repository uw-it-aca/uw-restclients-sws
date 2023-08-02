# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.registration import get_schedule_by_regid_and_term
from uw_sws.term import get_term_by_year_and_quarter


@fdao_pws_override
@fdao_sws_override
class SWSMissingRegid(TestCase):
    def test_instructor_list(self):
        term = get_term_by_year_and_quarter(2013, "spring")
        schedule = get_schedule_by_regid_and_term(
            "BB000000000000000000000000009994", term)

        self.assertEquals(len(schedule.sections), 1, "Has 1 section")

        instructors = schedule.sections[0].meetings[0].instructors
