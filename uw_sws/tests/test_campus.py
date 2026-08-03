# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

from uw_pws.util import fdao_pws_override

from uw_sws.campus import get_all_campuses
from uw_sws.util import fdao_sws_override


@fdao_pws_override
@fdao_sws_override
class SWSTestCampus(TestCase):

    def test_all_campuses(self):
        campuses = get_all_campuses()
        self.assertEqual(len(campuses), 3)
