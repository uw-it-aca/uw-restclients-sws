from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.models import Department, Term
from restclients_core.exceptions import DataFailureException
from uw_sws.curriculum import (
    get_curricula_by_department, get_curricula_by_term)


@fdao_pws_override
@fdao_sws_override
class SWSTestCurriculum(TestCase):
    def test_curricula_for_department(self):
        department = Department(label="EDUC")
        curricula = get_curricula_by_department(department)

        self.assertEquals(len(curricula), 7)

        # Valid department labels, no files for them
        self.assertRaises(DataFailureException,
                          get_curricula_by_department,
                          Department(label="BIOL"))

        self.assertRaises(DataFailureException,
                          get_curricula_by_department,
                          Department(label="CSE"))

        # Test future_terms
        # Valid value but no file
        self.assertRaises(DataFailureException,
                          get_curricula_by_department,
                          department,
                          future_terms=1)

        # Valid future_terms value
        curricula = get_curricula_by_department(department,
                                                future_terms=0)
        self.assertEquals(len(curricula), 7)

        # Invalid future_terms values
        self.assertRaises(ValueError,
                          get_curricula_by_department,
                          department,
                          future_terms=3)

        self.assertRaises(ValueError,
                          get_curricula_by_department,
                          department,
                          future_terms=-1)

        self.assertRaises(ValueError,
                          get_curricula_by_department,
                          department,
                          future_terms='x')

    def test_curricula_for_term(self):
        term = Term(quarter='winter', year=2013)
        curricula = get_curricula_by_term(term)
        self.assertEquals(len(curricula), 423)

        curricula = get_curricula_by_term(term, view_unpublished=True)
        self.assertEquals(len(curricula), 423)

        # Valid terms, no files for them
        self.assertRaises(DataFailureException,
                          get_curricula_by_term,
                          Term(quarter='spring', year=2012))

        self.assertRaises(DataFailureException,
                          get_curricula_by_term,
                          Term(quarter='autumn', year=2012))
