from unittest import TestCase
from restclients_core.models import MockHTTP
from restclients_core.exceptions import DataFailureException
from uw_sws.exceptions import ThreadedDataError
from uw_sws.models import Term
from uw_sws.section import get_section_by_label
from uw_sws.term import get_term_by_year_and_quarter
from uw_sws.registration import (
    get_active_registrations_by_section, get_all_registrations_by_section,
    get_schedule_by_regid_and_term)
from uw_sws.util import fdao_sws_override, date_to_str
from uw_pws.util import fdao_pws_override
from decimal import Decimal
import mock


@fdao_pws_override
@fdao_sws_override
class SWSTestRegistrations(TestCase):

    def test_active_registrations_for_section(self):
        # Valid section, missing file resources
        section = get_section_by_label('2013,winter,C LIT,396/A')

        self.assertRaises(DataFailureException,
                          get_active_registrations_by_section,
                          section)

        section = get_section_by_label('2017,autumn,EDC&I,552/A')
        self.assertEqual(section.section_label(), '2017,autumn,EDC&I,552/A')
        reg = get_active_registrations_by_section(section,
                                                  transcriptable_course="all")
        self.assertEqual(len(reg), 2)

    def test_all_registrations_by_section(self):
        # Valid section, missing file resources
        section = get_section_by_label('2013,winter,C LIT,396/A')

        self.assertRaises(DataFailureException,
                          get_all_registrations_by_section,
                          section)

    def test_active_registration_status_after_drop(self):
        section = get_section_by_label('2013,winter,DROP_T,100/A')

        registrations = get_all_registrations_by_section(section)

        self.assertEquals(len(registrations), 2)

        javerage_reg = registrations[0]
        self.assertEquals(javerage_reg.person.uwnetid, 'javerage')
        self.assertEquals(javerage_reg.is_active, False)
        self.assertEquals(javerage_reg.is_auditor, False)
        self.assertEquals(javerage_reg.is_credit, True)
        self.assertEquals(date_to_str(javerage_reg.request_date),
                          '2015-11-18')
        self.assertEquals(javerage_reg.request_status, 'DROPPED FROM CLASS')
        self.assertTrue(javerage_reg.is_dropped_status())
        self.assertEquals(javerage_reg.duplicate_code, '')
        self.assertEquals(javerage_reg.repository_timestamp.isoformat(),
                          '2016-01-05T14:45:15')
        self.assertEquals(javerage_reg.repeat_course, False)
        self.assertEquals(javerage_reg.grade, 'X')
        self.assertIsNone(javerage_reg.grade_date)
        self.assertFalse(javerage_reg.is_withdrew())
        self.assertFalse(javerage_reg.eos_only())
        self.assertFalse(javerage_reg.is_fee_based())
        self.assertFalse(javerage_reg.is_standby_status())
        self.assertFalse(javerage_reg.is_pending_status())
        self.assertEquals(
            javerage_reg.json_data(),
            {'credits': '2.0',
             'duplicate_code': '',
             'end_date': None,
             'feebase_type': '',
             'grade': 'X',
             'grade_date': None,
             'is_active': False,
             'is_auditor': False,
             'is_credit': True,
             'is_dropped': True,
             'is_eos_only': False,
             'is_independent_start': False,
             'is_pending': False,
             'is_standby': False,
             'is_withdrew': False,
             'meta_data': 'RegistrationSourceLocation=SDB;',
             'repeat_course': False,
             'repository_timestamp': '2016-01-05 14:45:15',
             'request_date': '2015-11-18',
             'request_status': 'DROPPED FROM CLASS',
             'start_date': None})
        self.assertIsNotNone(str(javerage_reg))

    def test_active_registration_status_after_drop_and_add(self):
        section = get_section_by_label('2013,winter,DROP_T,100/B')
        registrations = get_all_registrations_by_section(section)

        self.assertEquals(len(registrations), 3)
        javerage_reg = registrations[2]
        self.assertEquals(javerage_reg.person.uwnetid, 'javerage')
        self.assertEquals(javerage_reg.is_active, True)
        self.assertEquals(javerage_reg.is_auditor, True)
        self.assertEquals(javerage_reg.is_credit, True)
        self.assertEquals(date_to_str(javerage_reg.request_date),
                          '2015-11-18')
        self.assertEquals(javerage_reg.request_status, 'ADDED TO CLASS')
        self.assertFalse(javerage_reg.is_pending_status())
        self.assertEquals(javerage_reg.duplicate_code, 'A')
        self.assertEquals(javerage_reg.repository_timestamp.isoformat(),
                          '2016-01-05T14:45:15')
        self.assertEquals(javerage_reg.repeat_course, False)
        self.assertEquals(javerage_reg.grade, 'X')

    @mock.patch('uw_sws.registration.get_resource')
    def test_all_registrations_with_transcriptable_course(self,
                                                          mock_get_resource):
        section = get_section_by_label('2013,winter,DROP_T,100/B')

        # Test for default resource, i.e. transcriptable_course=yes
        registrations = get_all_registrations_by_section(section)
        mock_get_resource.assert_called_with(
            '/student/v5/registration.json?curriculum_abbreviation=DROP_T&'
            'instructor_reg_id=&course_number=100&verbose=true&year=2013&'
            'quarter=winter&is_active=&section_id=B')

        # Test for transcriptable_course=yes explicitly
        registrations = get_all_registrations_by_section(
            section, transcriptable_course='yes')
        mock_get_resource.assert_called_with(
            '/student/v5/registration.json?curriculum_abbreviation=DROP_T&'
            'instructor_reg_id=&course_number=100&verbose=true&year=2013&'
            'quarter=winter&is_active=&section_id=B&transcriptable_course=yes')

        # Test for transcriptable_course=all resource
        registrations = get_all_registrations_by_section(
            section, transcriptable_course='all')
        mock_get_resource.assert_called_with(
            '/student/v5/registration.json?curriculum_abbreviation=DROP_T&'
            'instructor_reg_id=&course_number=100&verbose=true&year=2013&'
            'quarter=winter&is_active=&section_id=B&transcriptable_course=all')

        # Test for transcriptable_course=no
        registrations = get_all_registrations_by_section(
            section, transcriptable_course='no')
        mock_get_resource.assert_called_with(
            '/student/v5/registration.json?curriculum_abbreviation=DROP_T&'
            'instructor_reg_id=&course_number=100&verbose=true&year=2013&'
            'quarter=winter&is_active=&section_id=B&transcriptable_course=no')

    def _get_section_from_schedule(self, class_schedule, section_label):
        for section in class_schedule.sections:
            if section.section_label() == section_label:
                return section

    def test_get_active_schedule_by_regid_and_term(self):
        term = Term(quarter="spring", year=2013)
        class_schedule = get_schedule_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)
        self.assertEquals(len(class_schedule.sections), 5)
        section = self._get_section_from_schedule(
            class_schedule, '2013,spring,TRAIN,100/A')
        self.assertEquals(len(section.get_instructors()), 1)
        self.assertEquals(section.student_credits,
                          Decimal("{:f}".format(1.0)))
        self.assertEquals(section.student_grade, "X")
        self.assertIsNone(section.grade_date)
        self.assertTrue(section.is_primary_section)
        self.assertEquals(section.is_auditor, False)

        section = self._get_section_from_schedule(
            class_schedule, '2013,spring,PHYS,121/AC')
        self.assertEquals(section.student_credits,
                          Decimal("{:f}".format(3.0)))
        self.assertEquals(section.student_grade, "4.0")
        self.assertEquals(date_to_str(section.grade_date), "2013-06-11")
        self.assertFalse(section.is_primary_section)
        self.assertEquals(section.is_auditor, False)

    def test_get_schedule_by_regid_and_term(self):
        term = Term(quarter="spring", year=2013)

        # include TSPrint is false instructor
        class_schedule = get_schedule_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)
        self.assertEquals(len(class_schedule.sections), 5)
        section = self._get_section_from_schedule(
            class_schedule, '2013,spring,TRAIN,100/A')
        self.assertEquals(len(section.get_instructors()), 1)

        # exclude TSPrint is false instructor
        class_schedule = get_schedule_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term,
            non_time_schedule_instructors=False)
        self.assertEquals(len(class_schedule.sections), 5)
        section = self._get_section_from_schedule(
            class_schedule, '2013,spring,TRAIN,100/A')
        self.assertEquals(len(section.get_instructors()), 0)

        # not transcriptable_course
        class_schedule = get_schedule_by_regid_and_term(
            'FE36CCB8F66711D5BE060004AC494FCE',
            term, transcriptable_course="no")
        self.assertEquals(len(class_schedule.sections), 1)
        section = self._get_section_from_schedule(
            class_schedule, '2013,spring,ESS,107/A')
        self.assertEquals(len(section.get_instructors()), 1)

        # eight's schedule
        class_schedule = get_schedule_by_regid_and_term(
            '12345678901234567890123456789012', term)
        self.assertEquals(len(class_schedule.sections), 9)
        section = self._get_section_from_schedule(
            class_schedule, '2013,spring,MATH,125/G')
        self.assertEquals(section.student_credits,
                          Decimal("{:f}".format(5.0)))
        self.assertEquals(section.student_grade, "3.5")
        self.assertEquals(section.is_auditor, True)
        self.assertTrue(section.is_primary_section)

        section = self._get_section_from_schedule(
            class_schedule, '2013,spring,MATH,125/GA')
        self.assertEquals(len(section.get_instructors()), 2)
        self.assertEquals(section.student_grade, "X")
        self.assertEquals(date_to_str(section.grade_date), None)
        self.assertFalse(section.is_primary_section)
        self.assertEquals(section.is_auditor, False)

    def test_transcriptable_course_all(self):
        term = Term(quarter="winter", year=2013)
        class_schedule = get_schedule_by_regid_and_term(
            'FE36CCB8F66711D5BE060004AC494F31', term,
            transcriptable_course="all",
        )
        self.assertEquals(len(class_schedule.sections), 1)
        self.assertEquals(str(class_schedule.sections[0].start_date),
                          "2013-01-16")
        self.assertEquals(str(class_schedule.sections[0].end_date),
                          "2013-03-20")
        self.assertTrue(class_schedule.sections[0].is_source_eos())
        self.assertEquals(class_schedule.registered_summer_terms, {})

    def test_empty_request_date(self):
        section = get_section_by_label('2013,winter,DROP_T,100/A')
        registrations = get_all_registrations_by_section(section)

        self.assertEquals(len(registrations), 2)
        javerage_reg = registrations[1]
        self.assertEquals(javerage_reg.person.uwnetid, 'javerage')
        self.assertEquals(javerage_reg.request_date, None)

    def test_registered_summer_terms(self):
        class_schedule = get_schedule_by_regid_and_term(
            '12345678901234567890123456789012',
            get_term_by_year_and_quarter(2013, "summer"),
            transcriptable_course="all")
        self.assertEquals(len(class_schedule.sections), 3)
        self.assertEquals(class_schedule.registered_summer_terms,
                          {'a-term': True, 'b-term': True, 'full-term': True})
        self.assertIsNotNone(class_schedule.json_data())

    def test_not_registered(self):
        class_schedule = get_schedule_by_regid_and_term(
            '00000000000000000000000000000001',
            get_term_by_year_and_quarter(2013, "summer"),
            transcriptable_course="all")
        self.assertEqual(len(class_schedule.sections), 0)

    def test_get_schedule_section_error(self):
        term = Term(quarter="spring", year=2012)
        self.assertRaises(
            ThreadedDataError, get_schedule_by_regid_and_term,
            '9136CCB8F66711D5BE060004AC494FFE', term)
