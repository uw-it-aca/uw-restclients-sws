# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

from restclients_core.exceptions import DataFailureException
from uw_pws.util import fdao_pws_override

from uw_sws.curriculum import get_curricula_by_department, get_curricula_by_term
from uw_sws.models import Department, Term
from uw_sws.util import fdao_sws_override


@fdao_pws_override
@fdao_sws_override
class SWSTestCurriculum(TestCase):
    def test_curricula_for_department(self):
        department = Department(label="EDUC")
        curricula = get_curricula_by_department(department)

        self.assertEqual(len(curricula), 7)

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
        self.assertEqual(len(curricula), 7)

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
        self.assertEqual(len(curricula), 423)

        curricula = get_curricula_by_term(term, view_unpublished=True)
        self.assertEqual(len(curricula), 423)

        # Valid terms, no files for them
        self.assertRaises(DataFailureException,
                          get_curricula_by_term,
                          Term(quarter='spring', year=2012))

        self.assertRaises(DataFailureException,
                          get_curricula_by_term,
                          Term(quarter='autumn', year=2012))
