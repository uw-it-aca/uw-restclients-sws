# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.college import get_all_colleges
from restclients_core.exceptions import DataFailureException


@fdao_pws_override
@fdao_sws_override
class SWSTestCollege(TestCase):

    def test_all_colleges(self):
        colleges = get_all_colleges()
        self.assertEquals(len(colleges), 20)
