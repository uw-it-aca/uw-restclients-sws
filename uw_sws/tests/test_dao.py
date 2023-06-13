# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from datetime import datetime
from uw_sws.dao import SWS_DAO, sws_now, SWS_TIMEZONE
from commonconf import override_settings


class SWSTestDao(TestCase):

    def test_custom_headers(self):
        self.assertEquals(SWS_DAO()._custom_headers('GET', '/', {}, None), {})
        with override_settings(RESTCLIENTS_SWS_OAUTH_BEARER='token'):
            self.assertEquals(
                SWS_DAO()._custom_headers('GET', '/', {}, None),
                {'Authorization': 'Bearer token'}
            )

    def test_sws_now(self):
        now = sws_now()
        now_tz = datetime.now(SWS_TIMEZONE)
        self.assertEquals(now.day, now_tz.day)
        self.assertEquals(now.hour, now_tz.hour)
        self.assertEquals(now.day, now_tz.day)
        self.assertEquals(now.minute, now_tz.minute)
        self.assertIsNone(now.tzname())
