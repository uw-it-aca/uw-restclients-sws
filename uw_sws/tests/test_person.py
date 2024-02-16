# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.person import get_person_by_regid
import datetime


@fdao_pws_override
@fdao_sws_override
class PersonTest(TestCase):
    def test_person_resource(self):
        data = get_person_by_regid("9136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(data.uwnetid, "javerage")
        self.assertEqual(data.uwregid, "9136CCB8F66711D5BE060004AC494FFE")
        self.assertTrue(data.directory_release)
        self.assertEqual(str(data.birth_date), "1961-10-26")
        self.assertEqual(data.email, "javerage@u.washington.edu")
        self.assertEqual(data.employee_id, "123456789")
        self.assertEqual(data.gender, "M")
        self.assertEqual(data.first_name, "John Joseph")
        self.assertEqual(data.pronouns, "he/him/his")
        self.assertEqual(data.last_name, "Average")
        self.assertEqual(data.student_name, "John Joseph Average")
        self.assertEqual(data.student_number, "1033334")
        self.assertEqual(data.student_system_key, "000083856")
        self.assertEqual(data.visa_type, '')
        self.assertFalse(data.is_veteran())
        self.assertEqual(data.local_phone, '2063333333')
        self.assertEqual(data.local_address.city, "SEATTLE")
        self.assertEqual(data.local_address.country, "United States")
        self.assertEqual(data.local_address.street_line1, "4634 26th Ave NE")
        self.assertEqual(data.local_address.street_line2, "APT 102")
        self.assertEqual(data.local_address.postal_code, "")
        self.assertEqual(data.local_address.state, "WA")
        self.assertEqual(data.local_address.zip_code, "98105")

        self.assertEqual(data.permanent_phone, "2065555555")
        self.assertEqual(data.permanent_address.city, "Bellevue")
        self.assertEqual(data.permanent_address.country, "")
        self.assertEqual(data.permanent_address.street_line1,
                         "1645 140th Ave NE")
        self.assertEqual(data.permanent_address.street_line2, "APT 980")
        self.assertEqual(data.permanent_address.postal_code, "")
        self.assertEqual(data.permanent_address.state, "WA")
        self.assertEqual(data.permanent_address.zip_code, "98005-1234")

        self.assertEqual(data.last_enrolled.href,
                         "/student/v5/term/2013,autumn.json")
        self.assertEqual(data.last_enrolled.quarter, "autumn")
        self.assertEqual(data.last_enrolled.year, 2013)
        self.assertEqual(data.resident_code, 1)

    def test_person_jinter(self):
        data = get_person_by_regid("9136CCB8F66711D5BE060004AC494F31")
        self.assertEqual(data.uwnetid, "jinter")
        self.assertEqual(data.uwregid, "9136CCB8F66711D5BE060004AC494F31")
        self.assertFalse(data.directory_release)
        self.assertEqual(data.email, "jinter@u.washington.edu")
        self.assertEqual(data.employee_id, "133456789")
        self.assertEqual(data.gender, "F")
        self.assertEqual(data.first_name, "Japendra")
        self.assertEqual(data.last_name, "Chakrabarti")
        self.assertEqual(data.pronouns, "she/her/hers")
        self.assertEqual(data.student_name, "Chakrabarti,Japendra")
        self.assertEqual(data.student_number, "1233334")
        self.assertEqual(data.student_system_key, "000018235")
        self.assertEqual(data.visa_type, "F1")
        self.assertTrue(data.is_F1())
        self.assertFalse(data.is_J1())
        self.assertEqual(data.local_phone, "2065554567")
        self.assertEqual(data.local_address.city, "Seattle")
        self.assertEqual(data.local_address.country, "")
        self.assertEqual(data.local_address.street_line1,
                         "2344 Eastlake Ave E")
        self.assertEqual(data.local_address.street_line2, "APT 204")
        self.assertEqual(data.local_address.postal_code, "")
        self.assertEqual(data.local_address.state, "WA")
        self.assertEqual(data.local_address.zip_code, "98102")

        self.assertEqual(data.permanent_phone, None)
        self.assertEqual(data.permanent_address.city, "Fort")
        self.assertEqual(data.permanent_address.country, "India")
        self.assertEqual(data.permanent_address.street_line1,
                         "Veer Nariman Road")
        self.assertEqual(data.permanent_address.street_line2, "")
        self.assertEqual(data.permanent_address.postal_code, "400001")
        self.assertEqual(data.permanent_address.state, "Mumbai")
        self.assertEqual(data.permanent_address.zip_code, "")
        self.assertIsNone(data.resident_code)

        data = get_person_by_regid("12345678901234567890123456789012")
        self.assertTrue(data.is_J1())
        self.assertEqual(data.pronouns, "they/them/theirs")

    def test_person_none(self):
        data = get_person_by_regid("00000000000000000000000000000001")
        self.assertEqual(data.uwnetid, "none")
        self.assertEqual(data.uwregid, "00000000000000000000000000000001")
        self.assertIsNone(data.birth_date)
        self.assertIsNone(data.directory_release)
        self.assertIsNone(data.email)
        self.assertIsNone(data.employee_id)
        self.assertIsNone(data.gender)
        self.assertIsNone(data.first_name)
        self.assertEqual(data.pronouns, None)
        self.assertIsNone(data.last_name)
        self.assertEqual(data.student_name, "SYSTEM OVERHEAD")
        self.assertIsNone(data.student_number)
        self.assertIsNone(data.student_system_key)
        self.assertIsNone(data.visa_type)
        self.assertFalse(data.is_J1())
        self.assertFalse(data.is_F1())
        self.assertIsNone(data.local_phone)
        self.assertIsNone(data.local_address)
        self.assertIsNone(data.permanent_phone)
        self.assertIsNone(data.permanent_address)
        self.assertIsNone(data.resident_code)

    def test_json_datat(self):
        data = get_person_by_regid("9136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(data.json_data()['email'],
                         "javerage@u.washington.edu")
