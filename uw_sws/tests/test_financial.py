# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.financial import get_account_balances_by_regid
import datetime


@fdao_pws_override
@fdao_sws_override
class SWSFinance(TestCase):
    def test_financial_resource(self):
        data = get_account_balances_by_regid(
            "9136CCB8F66711D5BE060004AC494FFE")
        self.assertEquals(data.tuition_accbalance, "12345.00")
        self.assertEquals(data.pce_accbalance, "0.00")

        data = get_account_balances_by_regid(
            "FE36CCB8F66711D5BE060004AC494F31")
        self.assertEquals(data.tuition_accbalance, "12345.00")
        self.assertEquals(data.pce_accbalance, "345.00")
