from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_sws.advisers import get_advisers


@fdao_sws_override
class AdviserTest(TestCase):
    def test_get_advisers(self):
        advisers = get_advisers("9136CCB8F66711D5BE060004AC494FFE")
        self.assertEquals(len(advisers), 1)
        self.assertEquals(advisers[0].uwnetid, "uwhonors")
        self.assertEquals(
            advisers[0].json_data(),
            {'booking_url': 'https://honors.uw.edu/advising/',
             'email_address': 'uwhonors@uw.edu',
             'full_name': 'UNIVERSITY HONORS PROGRAM',
             'is_active': True,
             'is_dept_adviser': False,
             'phone_number': '+1 206 543-7444',
             'program': 'UW Honors',
             'regid': '24A20F50AE3511D68CBC0004AC494FFE',
             'uwnetid': 'uwhonors'})
        self.assertIsNotNone(str(advisers))

    def test_error_case(self):
        self.assertEquals(
            len(get_advisers("00000000000000000000000000000001")), 0)
        self.assertIsNone(get_advisers("00000000000000000000000000000002"))
