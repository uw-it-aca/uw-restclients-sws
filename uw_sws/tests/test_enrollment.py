from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.term import get_current_term
from uw_sws.enrollment import get_grades_by_regid_and_term, get_enrollment_by_regid_and_term
from restclients_core.exceptions import DataFailureException


@fdao_pws_override
@fdao_sws_override
class SWSTestEnrollments(TestCase):
    def test_javerage_grades(self):
            term = get_current_term()
            grades = get_grades_by_regid_and_term('9136CCB8F66711D5BE060004AC494FFE', term)

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
            enrollement = get_enrollment_by_regid_and_term('9136CCB8F66711D5BE060004AC494FFE', term)
            self.assertEquals(enrollement.class_level, "SENIOR")
            self.assertEquals(enrollement.is_honors, False)
            self.assertEquals(len(enrollement.majors), 1)
            self.assertEquals(enrollement.majors[0].campus, "Seattle")
            self.assertEquals(enrollement.majors[0].degree_name, "BACHELOR OF SCIENCE (APPLIED & COMPUTATIONAL MATH SCIENCES)")
            self.assertEquals(enrollement.minors[0].campus, "Seattle")
            self.assertEquals(enrollement.minors[0].name, "AMERICAN SIGN LANGUAGE")
