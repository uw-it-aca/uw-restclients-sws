# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.worker import PWSPerson


@fdao_pws_override
@fdao_sws_override
class WorkerTest(TestCase):
    def test_run_tasks(self):
        regid_set = {
            "9136CCB8F66711D5BE060004AC494FFE",
            "9136CCB8F66711D5BE060004AC494F31",
            "00000000000000000000000000000001",
            "12345678901234567890123456789012",
            "2817F385001347AD80D653A8E352FDC9",
            "260A0DEC95CB11D78BAA000629C31437",
            "1914B1B26A7D11D5A4AE0004AC494FFE",
            "357C15A6D5794648BE667830EF20E6D8",
            "40B1BC0B6A7945219437C8585AEFCF63"
        }
        cworker = PWSPerson(regid_set)
        results = cworker.run_tasks()
        self.assertIsNotNone(results)
        self.assertEqual(len(results), len(regid_set))
        for regid in regid_set:
            self.assertIn(regid, results)
            self.assertIsNotNone(results[regid])
            self.assertEqual(results[regid].uwregid, regid)
