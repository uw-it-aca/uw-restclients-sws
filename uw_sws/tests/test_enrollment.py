from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.term import get_current_term, get_term_by_year_and_quarter
from uw_sws.enrollment import get_grades_by_regid_and_term,\
    get_enrollment_by_regid_and_term
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
        self.assertFalse(enrollement.has_independent_start_course())
        self.assertFalse(enrollement.is_enroll_src_pce)

    def test_offterm_enrolled_courses(self):
        term = get_term_by_year_and_quarter(2013, 'winter')
        enrollement = get_enrollment_by_regid_and_term(
            'AABBCCDDEEFFAABBCCDDEEFFAABBCCDC', term)
        self.assertEquals(enrollement.class_level, u'NON_MATRIC')
        self.assertTrue(enrollement.is_enroll_src_pce)
        self.assertTrue(enrollement.is_non_matric())
        self.assertTrue(enrollement.has_independent_start_course())
        self.assertEqual(len(enrollement.independent_start_sections), 2)
        section1 = enrollement.independent_start_sections[0]
        self.assertTrue(section1.is_fee_based())
        self.assertEqual(str(section1.end_date), '2013-04-29 00:00:00')
        self.assertEqual(str(section1.start_date), '2013-01-28 00:00:00')
        self.assertTrue(section1.is_reg_src_pce)
        self.assertEqual(
            section1.section_ref.json_data(),
            {'course_number': u'201',
             'curriculum_abbr': u'COM',
             'quarter': u'winter',
             'section_id': u'A',
             'section_label': u'2013,winter,COM,201/A',
             'url': u'/student/v5/course/2013,winter,COM,201/A.json',
             'year': 2013})

        section2 = enrollement.independent_start_sections[1]
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
