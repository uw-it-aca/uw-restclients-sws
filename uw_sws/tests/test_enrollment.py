from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.models import Term
from uw_sws.term import get_current_term, get_next_term,\
    get_term_by_year_and_quarter, get_term_after
from uw_sws.enrollment import get_grades_by_regid_and_term,\
    is_src_location_pce, ENROLLMENT_SOURCE_PCE, has_start_end_dates,\
    get_enrollment_by_regid_and_term, enrollment_search_by_regid
from restclients_core.exceptions import DataFailureException


@fdao_pws_override
@fdao_sws_override
class SWSTestEnrollments(TestCase):
    def test_javerage_grades(self):
        term = get_current_term()
        grades = get_grades_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)

        self.assertEquals(grades.term.year, 2013)
        self.assertEquals(grades.term.quarter, "spring")
        self.assertEquals(grades.user.uwnetid, "javerage")
        self.assertEquals(grades.grade_points, 30)
        self.assertEquals(grades.credits_attempted, 10)
        self.assertEquals(grades.non_grade_credits, 2)

        self.assertEquals(grades.grades[0].grade, 'CR')
        self.assertEquals(grades.grades[2].grade, '3.1')
        self.assertEquals(grades.grades[2].credits, '3.0')
        self.assertEquals(grades.grades[2].section.course_number, '121')

    def test_javerage_major(self):
        term = get_current_term()
        enrollement = get_enrollment_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)
        self.assertEquals(enrollement.class_level, "SENIOR")
        self.assertEquals(enrollement.is_honors, False)
        self.assertEquals(len(enrollement.majors), 1)
        self.assertEquals(enrollement.majors[0].campus, "Seattle")
        self.assertEquals(
            enrollement.majors[0].degree_name,
            "BACHELOR OF SCIENCE (APPLIED & COMPUTATIONAL MATH SCIENCES)")
        self.assertEquals(enrollement.minors[0].campus, "Seattle")
        self.assertEquals(enrollement.minors[0].name, "AMERICAN SIGN LANGUAGE")
        self.assertFalse(enrollement.is_non_matric())
        self.assertFalse(enrollement.has_off_term_course())
        self.assertFalse(enrollement.is_enroll_src_pce)

    def test_is_src_location_pce(self):
        self.assertFalse(is_src_location_pce(
                {'Metadata': ''},
                ENROLLMENT_SOURCE_PCE))
        self.assertFalse(is_src_location_pce(
                {'Metadata': "EnrollmentSourceLocation=SDB;"},
                ENROLLMENT_SOURCE_PCE))
        self.assertTrue(is_src_location_pce(
                {'Metadata': "EnrollmentSourceLocation=SDB_EOS"},
                ENROLLMENT_SOURCE_PCE))
        self.assertTrue(is_src_location_pce(
                {'Metadata': "EnrollmentSourceLocation=EOS"},
                ENROLLMENT_SOURCE_PCE))

    def test_offterm_enrolled_courses(self):
        term = get_term_by_year_and_quarter(2013, 'winter')
        enrollement = get_enrollment_by_regid_and_term(
            'AABBCCDDEEFFAABBCCDDEEFFAABBCCDC', term)
        self.assertEquals(enrollement.class_level, u'NON_MATRIC')
        self.assertTrue(enrollement.is_enroll_src_pce)
        self.assertTrue(enrollement.is_non_matric())
        self.assertTrue(enrollement.has_off_term_course())
        self.assertEqual(len(enrollement.off_term_sections), 2)

        self.assertTrue(
            enrollement.off_term_sections.get("2013,winter,COM,201/A"))
        section1 = enrollement.off_term_sections["2013,winter,COM,201/A"]
        self.assertTrue(section1.is_fee_based())
        self.assertEqual(str(section1.end_date), '2013-04-29 00:00:00')
        self.assertEqual(str(section1.start_date), '2013-01-28 00:00:00')
        self.assertTrue(section1.is_reg_src_pce)
        self.assertEqual(section1.json_data(),
                         {'start_date': '2013-01-28 00:00:00',
                          'end_date': '2013-04-29 00:00:00',
                          'feebase_type': u'Fee based course',
                          'is_reg_src_pce': True,
                          })
        self.assertEqual(
            section1.section_ref.json_data(),
            {'course_number': u'201',
             'curriculum_abbr': u'COM',
             'quarter': u'winter',
             'section_id': u'A',
             'section_label': u'2013,winter,COM,201/A',
             'url': u'/student/v5/course/2013,winter,COM,201/A.json',
             'year': 2013})

        self.assertTrue(
            enrollement.off_term_sections.get("2013,winter,PSYCH,203/A"))
        section2 = enrollement.off_term_sections["2013,winter,PSYCH,203/A"]
        self.assertTrue(section2.is_fee_based())
        self.assertEqual(str(section2.end_date), '2013-06-22 00:00:00')
        self.assertEqual(str(section2.start_date), '2013-01-29 00:00:00')
        self.assertTrue(section2.is_reg_src_pce)
        self.assertEqual(
            section2.section_ref.json_data(),
            {'course_number': u'203',
             'curriculum_abbr': u'PSYCH',
             'quarter': u'winter',
             'section_id': u'A',
             'section_label': u'2013,winter,PSYCH,203/A',
             'url': u'/student/v5/course/2013,winter,PSYCH,203/A.json',
             'year': 2013})

        self.assertFalse(
            enrollement.off_term_sections.get("2014,winter,PSYCH,203/A"))


    def test_enrollment_search(self):
        result_dict = enrollment_search_by_regid(
            '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(len(result_dict), 6)
        term = get_current_term()
        self.assertTrue(term in result_dict)
        self.assertIsNotNone(result_dict.get(term))
        enrollement = result_dict.get(term)
        self.assertEquals(enrollement.class_level, "SENIOR")
        self.assertEquals(len(enrollement.majors), 1)
        self.assertEquals(len(enrollement.minors), 1)

        term2 = get_term_by_year_and_quarter(2013, 'autumn')
        self.assertIsNone(result_dict.get(term2))

        term3 = get_term_by_year_and_quarter(2012, 'spring')
        self.assertTrue(term3 in result_dict)
        self.assertIsNotNone(result_dict.get(term3))

        term1 = get_term_by_year_and_quarter(2013, 'summer')
        self.assertTrue(term1 in result_dict)
        self.assertIsNotNone(result_dict.get(term1))

        term4 = Term(year=1996, quarter='autumn')
        self.assertTrue(term4 in result_dict)
        self.assertIsNotNone(result_dict.get(term4))

        # regid of none
        result_dict = enrollment_search_by_regid(
            '00000000000000000000000000000001')
        self.assertEqual(len(result_dict), 0)

    def test_has_start_end_dates(self):
        json_data = {u'StartDate': u'01/29/2013',
                     u'EndDate': u'06/22/2013'}
        self.assertTrue(has_start_end_dates(json_data))
        json_data = {"FeeBaseType": ""}
        self.assertFalse(has_start_end_dates(json_data))
        json_data = {"FeeBaseType": "", "StartDate":"", "EndDate":""}
        self.assertFalse(has_start_end_dates(json_data))
