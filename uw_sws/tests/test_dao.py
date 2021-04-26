# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.dao import SWS_DAO
from commonconf import override_settings


class SWSTestDao(TestCase):

    def test_custom_headers(self):
        self.assertEquals(SWS_DAO()._custom_headers('GET', '/', {}, None), {})
        with override_settings(RESTCLIENTS_SWS_OAUTH_BEARER='token'):
            self.assertEquals(
                SWS_DAO()._custom_headers('GET', '/', {}, None),
                {'Authorization': 'Bearer token'}
            )
