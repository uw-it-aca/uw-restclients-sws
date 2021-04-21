# Copyright 2021 UW-IT, University of Washington
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
        self.assertEquals(data.uwnetid, "javerage")
        self.assertEquals(data.uwregid, "9136CCB8F66711D5BE060004AC494FFE")
        self.assertTrue(data.directory_release)
        self.assertEquals(str(data.birth_date), "1961-10-26")
        self.assertEquals(data.email, "javerage@u.washington.edu")
        self.assertEquals(data.employee_id, "123456789")
        self.assertEquals(data.gender, "M")
        self.assertEquals(data.first_name, "John Joseph")
        self.assertEquals(data.pronouns, "he/him/his")
        self.assertEquals(data.last_name, "Average")
        self.assertEquals(data.student_name, "Average,John Joseph")
        self.assertEquals(data.student_number, "1033334")
        self.assertEquals(data.student_system_key, "000083856")
        self.assertEquals(data.visa_type, None)
        self.assertEquals(data.local_phone, None)
        self.assertEquals(data.local_address.city, "Seattle")
        self.assertEquals(data.local_address.country, "United States")
        self.assertEquals(data.local_address.street_line1, "4634 26th Ave NE")
        self.assertEquals(data.local_address.street_line2, "APT 102")
        self.assertEquals(data.local_address.postal_code, "")
        self.assertEquals(data.local_address.state, "WA")
        self.assertEquals(data.local_address.zip_code, "98105")

        self.assertEquals(data.permanent_phone, "4255556789")
        self.assertEquals(data.permanent_address.city, "Bellevue")
        self.assertEquals(data.permanent_address.country, "")
        self.assertEquals(data.permanent_address.street_line1,
                          "1645 140th Ave NE")
        self.assertEquals(data.permanent_address.street_line2, "APT 980")
        self.assertEquals(data.permanent_address.postal_code, "")
        self.assertEquals(data.permanent_address.state, "WA")
        self.assertEquals(data.permanent_address.zip_code, "98005-1234")

        self.assertEquals(data.last_enrolled.href,
                          "/student/v5/term/2013,autumn.json")
        self.assertEquals(data.last_enrolled.quarter, "autumn")
        self.assertEquals(data.last_enrolled.year, 2013)

    def test_person_jinter(self):
        data = get_person_by_regid("9136CCB8F66711D5BE060004AC494F31")
        self.assertEquals(data.uwnetid, "jinter")
        self.assertEquals(data.uwregid, "9136CCB8F66711D5BE060004AC494F31")
        self.assertFalse(data.directory_release)
        self.assertEquals(data.email, "jinter@u.washington.edu")
        self.assertEquals(data.employee_id, "133456789")
        self.assertEquals(data.gender, "F")
        self.assertEquals(data.first_name, "Japendra")
        self.assertEquals(data.last_name, "Chakrabarti")
        self.assertEquals(data.pronouns, "she/her/hers")
        self.assertEquals(data.student_name, "Chakrabarti,Japendra")
        self.assertEquals(data.student_number, "1233334")
        self.assertEquals(data.student_system_key, "000018235")
        self.assertEquals(data.visa_type, "F1")
        self.assertTrue(data.is_F1())
        self.assertFalse(data.is_J1())
        self.assertEquals(data.local_phone, "2065554567")
        self.assertEquals(data.local_address.city, "Seattle")
        self.assertEquals(data.local_address.country, "")
        self.assertEquals(data.local_address.street_line1,
                          "2344 Eastlake Ave E")
        self.assertEquals(data.local_address.street_line2, "APT 204")
        self.assertEquals(data.local_address.postal_code, "")
        self.assertEquals(data.local_address.state, "WA")
        self.assertEquals(data.local_address.zip_code, "98102")

        self.assertEquals(data.permanent_phone, None)
        self.assertEquals(data.permanent_address.city, "Fort")
        self.assertEquals(data.permanent_address.country, "India")
        self.assertEquals(data.permanent_address.street_line1,
                          "Veer Nariman Road")
        self.assertEquals(data.permanent_address.street_line2, "")
        self.assertEquals(data.permanent_address.postal_code, "400001")
        self.assertEquals(data.permanent_address.state, "Mumbai")
        self.assertEquals(data.permanent_address.zip_code, "")

        data = get_person_by_regid("12345678901234567890123456789012")
        self.assertTrue(data.is_J1())
        self.assertEquals(data.pronouns, "they/them/theirs")

    def test_person_none(self):
        data = get_person_by_regid("00000000000000000000000000000001")
        self.assertEquals(data.uwnetid, "none")
        self.assertEquals(data.uwregid, "00000000000000000000000000000001")
        self.assertIsNone(data.birth_date)
        self.assertIsNone(data.directory_release)
        self.assertIsNone(data.email)
        self.assertIsNone(data.employee_id)
        self.assertIsNone(data.gender)
        self.assertIsNone(data.first_name)
        self.assertEquals(data.pronouns, None)
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

    def test_json_datat(self):
        data = get_person_by_regid("9136CCB8F66711D5BE060004AC494FFE")
        self.assertEquals(data.json_data()['email'],
                          "javerage@u.washington.edu")
