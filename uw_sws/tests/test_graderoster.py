import random
import re
from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.graderoster import get_graderoster, update_graderoster
from uw_sws.section import get_section_by_label
from uw_sws.models import Section
from restclients_core.exceptions import DataFailureException


@fdao_pws_override
@fdao_sws_override
class SWSTestGradeRoster(TestCase):

    def test_get_graderoster(self):
            section = get_section_by_label('2013,summer,CSS,161/A')
            instructor = section.meetings[0].instructors[0]
            requestor = instructor

            graderoster = get_graderoster(section, instructor, requestor)

            self.assertEquals(graderoster.graderoster_label(),
                              "2013,summer,CSS,161,A,%s" % instructor.uwregid,
                              "Correct graderoster_label()")
            self.assertEquals(len(graderoster.grade_submission_delegates), 2, "Grade submission delegates")
            self.assertEquals(len(graderoster.items), 5, "GradeRoster items")

            grades = ['0.7', None, '3.1', '1.5', '4.0']
            labels = ['1914B1B26A7D11D5A4AE0004AC494FFE',
                      '511FC8241DC611DB9943F9D03AACCE31',
                      'F00E253C634211DA9755000629C31437',
                      'C7EED7406A7C11D5A4AE0004AC494FFE',
                      'A9D2DDFA6A7D11D5A4AE0004AC494FFE,A']
            for idx, item in enumerate(graderoster.items):
                self.assertEquals(len(item.grade_choices), 36, "grade_choices returns correct grades")
                self.assertEquals(item.grade, grades[idx], "Correct default grade")
                self.assertEquals(item.student_label(), labels[idx], "Correct student label")

    def test_put_graderoster(self):
            section = get_section_by_label('2013,summer,CSS,161/A')
            instructor = section.meetings[0].instructors[0]
            requestor = instructor

            graderoster = get_graderoster(section, instructor, requestor)

            for item in graderoster.items:
                new_grade = str(round(random.uniform(1, 4), 1))
                item.grade = new_grade

            orig_xhtml = split_xhtml(graderoster.xhtml())

            new_graderoster = update_graderoster(graderoster, requestor)
            new_xhtml = split_xhtml(new_graderoster.xhtml())
            self.assertEquals(orig_xhtml, new_xhtml, "XHTML is equal")


def split_xhtml(xhtml):
    return re.split(r'\s*\n\s*', xhtml.strip())
