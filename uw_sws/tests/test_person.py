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
            self.assertEquals(data.email, "javerage@u.washington.edu")
            self.assertEquals(data.employee_id, "123456789")
            self.assertEquals(data.gender, "M")
            self.assertEquals(data.first_name, "John Joseph")
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
            self.assertEquals(data.permanent_address.street_line1, "1645 140th Ave NE")
            self.assertEquals(data.permanent_address.street_line2, "APT 980")
            self.assertEquals(data.permanent_address.postal_code, "")
            self.assertEquals(data.permanent_address.state, "WA")
            self.assertEquals(data.permanent_address.zip_code, "98005-1234")

            self.assertEquals(data.last_enrolled.href, "/student/v5/term/2013,autumn.json")
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
            self.assertEquals(data.student_name, "Chakrabarti,Japendra")
            self.assertEquals(data.student_number, "1233334")
            self.assertEquals(data.student_system_key, "000018235")
            self.assertEquals(data.visa_type, "F1")
            self.assertEquals(data.local_phone, "2065554567")
            self.assertEquals(data.local_address.city, "Seattle")
            self.assertEquals(data.local_address.country, "")
            self.assertEquals(data.local_address.street_line1, "2344 Eastlake Ave E")
            self.assertEquals(data.local_address.street_line2, "APT 204")
            self.assertEquals(data.local_address.postal_code, "")
            self.assertEquals(data.local_address.state, "WA")
            self.assertEquals(data.local_address.zip_code, "98102")

            self.assertEquals(data.permanent_phone, None)
            self.assertEquals(data.permanent_address.city, "Fort")
            self.assertEquals(data.permanent_address.country, "India")
            self.assertEquals(data.permanent_address.street_line1, "Veer Nariman Road")
            self.assertEquals(data.permanent_address.street_line2, "")
            self.assertEquals(data.permanent_address.postal_code, "400001")
            self.assertEquals(data.permanent_address.state, "Mumbai")
            self.assertEquals(data.permanent_address.zip_code, "")

    def test_person_none(self):
            data = get_person_by_regid("00000000000000000000000000000001")
            self.assertEquals(data.uwnetid, "none")
            self.assertEquals(data.uwregid, "00000000000000000000000000000001")
            self.assertEquals(data.directory_release, None)
            self.assertEquals(data.email, None)
            self.assertEquals(data.employee_id, None)
            self.assertEquals(data.gender, None)
            self.assertEquals(data.first_name, "No")
            self.assertEquals(data.last_name, "Ne")
            self.assertEquals(data.student_name, None)
            self.assertEquals(data.student_number, None)
            self.assertEquals(data.student_system_key, None)
            self.assertEquals(data.visa_type, None)
            self.assertEquals(data.local_phone, None)
            self.assertEquals(data.local_address, None)
            self.assertEquals(data.permanent_phone, None)
            self.assertEquals(data.permanent_address, None)

    def test_json_datat(self):
            data = get_person_by_regid("9136CCB8F66711D5BE060004AC494FFE")
            self.assertEquals(data.json_data()['email'], "javerage@u.washington.edu")
