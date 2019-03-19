from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.campus import get_all_campuses
from restclients_core.exceptions import DataFailureException


@fdao_pws_override
@fdao_sws_override
class SWSTestCampus(TestCase):

    def test_all_campuses(self):
        campuses = get_all_campuses()

        self.assertEquals(len(campuses), 3)
