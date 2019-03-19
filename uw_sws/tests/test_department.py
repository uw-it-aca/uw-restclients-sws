from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.models import College
from restclients_core.exceptions import DataFailureException
from uw_sws.department import get_departments_by_college


@fdao_pws_override
@fdao_sws_override
class SWSTestDepartment(TestCase):

    def test_departments_for_college(self):
        college = College(label="MED")
        depts = get_departments_by_college(college)

        self.assertEquals(len(depts), 30)

        # Valid department labels, no files for them
        self.assertRaises(DataFailureException,
                          get_departments_by_college,
                          College(label="NURS"))
