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
