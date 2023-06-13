# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from datetime import datetime, timedelta
from restclients_core.exceptions import DataFailureException
from uw_sws.models import Term
from uw_sws.term import (
    get_term_by_year_and_quarter, get_term_before, get_term_after,
    get_current_term, get_next_term, get_previous_term, get_term_by_date,
    get_specific_term, get_next_autumn_term, get_next_non_summer_term)


@fdao_sws_override
@fdao_pws_override
class SWSTestTerm(TestCase):

    def setUp(self):
        self.autumn2015 = Term()
        self.autumn2015.quarter = 'autumn'
        self.autumn2015.year = 2015

        self.winter2016 = Term()
        self.winter2016.quarter = 'winter'
        self.winter2016.year = 2016
        self.spring2016 = Term()
        self.spring2016.quarter = 'spring'
        self.spring2016.year = 2016
        self.summer2016 = Term()
        self.summer2016.quarter = 'summer'
        self.summer2016.year = 2016
        self.autumn2016 = Term()
        self.autumn2016.quarter = 'autumn'
        self.autumn2016.year = 2016

        self.winter2017 = Term()
        self.winter2017.quarter = 'winter'
        self.winter2017.year = 2017
        self.summer2017 = Term()
        self.summer2017.quarter = 'summer'
        self.summer2017.year = 2017
        self.autumn2017 = Term()
        self.autumn2017.quarter = 'autumn'
        self.autumn2017.year = 2017

    def test_mock_data_fake_grading_window(self):
        # This rounds down to 0 days, so check by seconds :(
        term = get_current_term()
        self.assertEquals(term.is_grading_period_open(),
                          False, "Grading period is open")
        self.assertEquals(term.is_grading_period_past(),
                          True, "Grading period is not past")
        now = datetime(2013, 4, 15, 0, 0, 1)
        self.assertFalse(term.is_grading_period_open(now))
        self.assertFalse(term.is_grading_period_past(now))

        now = datetime(2013, 5, 27, 8, 0, 1)
        self.assertTrue(term.is_grading_period_open(now))
        self.assertFalse(term.is_grading_period_past(now))
        now = datetime(2013, 6, 18, 17, 0, 1)
        self.assertFalse(term.is_grading_period_open(now))
        self.assertTrue(term.is_grading_period_past(now))

        # Also test for Spring 2013, as that's the "current" quarter
        term1 = get_term_by_year_and_quarter(2013, 'spring')
        self.assertEquals(term, term1)

    def test_current_quarter(self):
        term = get_current_term()
        comparison_datetime = datetime(2013, 4, 10, 0, 0, 0)
        self.assertTrue(term.is_current(comparison_datetime))
        expected_quarter = "spring"
        expected_year = 2013

        self.assertEquals(term.year, expected_year,
                          "Return {} for the current year".format(
                              expected_year))

        self.assertEquals(term.quarter, expected_quarter,
                          "Return {} for the current quarter".format(
                              expected_quarter))

        self.assertEquals(term.first_day_quarter.year, 2013)
        self.assertEquals(term.first_day_quarter.month, 4)
        self.assertEquals(term.first_day_quarter.day, 1)
        self.assertEquals(term.get_bod_first_day(),
                          datetime(2013, 4, 1, 0, 0, 0))

        self.assertEquals(term.census_day.year, 2013)
        self.assertEquals(term.census_day.month, 4)
        self.assertEquals(term.census_day.day, 12)
        self.assertEquals(term.get_eod_census_day(),
                          datetime(2013, 4, 13, 0, 0, 0))

        self.assertEquals(term.get_bod_reg_period1_start(),
                          datetime(2013, 2, 15, 0, 0, 0))

        self.assertEquals(term.get_bod_reg_period2_start(),
                          datetime(2013, 3, 4, 0, 0, 0))

        self.assertEquals(term.get_bod_reg_period3_start(),
                          datetime(2013, 4, 1, 0, 0, 0))

        self.assertEquals(term.get_eod_last_final_exam(),
                          datetime(2013, 6, 15, 0, 0, 0))

        self.assertEquals(term.last_day_instruction.year, 2013)
        self.assertEquals(term.last_day_instruction.month, 6)
        self.assertEquals(term.last_day_instruction.day, 7)
        self.assertEquals(term.get_eod_last_instruction(),
                          datetime(2013, 6, 8, 0, 0, 0))

        self.assertTrue(term.time_schedule_published.get(u'seattle'))
        self.assertTrue(term.time_schedule_published.get(u'bothell'))
        self.assertTrue(term.time_schedule_published.get(u'tacoma'))

        next_autumn_term = get_next_autumn_term(term)
        self.assertEquals(next_autumn_term.year, 2013)
        self.assertEquals(next_autumn_term.quarter, 'autumn')

        next_non_summer_term = get_next_non_summer_term(term)
        self.assertEquals(next_non_summer_term.year,
                          next_autumn_term.year)
        self.assertEquals(next_non_summer_term.quarter,
                          next_autumn_term.quarter)

        self.assertFalse(term.is_summer_quarter())

    # Expected values will have to change when the json files are updated
    def test_previous_quarter(self):
        term = get_previous_term()

        expected_quarter = "winter"
        expected_year = 2013

        comparison_datetime = datetime(2013, 4, 10, 0, 0, 0)
        self.assertTrue(term.is_past(comparison_datetime))

        self.assertEquals(term.year, expected_year,
                          "Return {} for the previous year".format(
                              expected_year))

        self.assertEquals(term.quarter, expected_quarter,
                          "Return {} for the previous quarter".format(
                              expected_quarter))

        self.assertEquals(term.get_bod_first_day(),
                          datetime(2013, 1, 7, 0, 0, 0))

        self.assertEquals(term.grading_period_open.date().year, 2013)
        self.assertEquals(term.grading_period_open.date().month, 2)
        self.assertEquals(term.grading_period_open.date().day, 25)
        self.assertEquals(term.grading_period_open.time().hour, 8)
        self.assertEquals(term.grading_period_open.time().minute, 0)

        self.assertEquals(term.get_bod_reg_period1_start(),
                          datetime(2012, 11, 2, 0, 0, 0))

        self.assertEquals(term.get_bod_reg_period2_start(),
                          datetime(2012, 11, 26, 0, 0, 0))

        self.assertEquals(term.get_bod_reg_period3_start(),
                          datetime(2013, 1, 7, 0, 0, 0))

        self.assertEquals(term.grade_submission_deadline.date().year, 2013)
        self.assertEquals(term.grade_submission_deadline.date().month, 3)
        self.assertEquals(term.grade_submission_deadline.date().day, 26)
        self.assertEquals(term.grade_submission_deadline.time().hour, 17)
        self.assertEquals(term.grade_submission_deadline.time().minute, 0)
        self.assertEquals(term.get_eod_grade_submission(),
                          datetime(2013, 3, 27, 0, 0, 0))

        self.assertEquals(term.last_final_exam_date.year, 2013)
        self.assertEquals(term.last_final_exam_date.month, 3)
        self.assertEquals(term.last_final_exam_date.day, 22)
        self.assertEquals(term.get_eod_last_final_exam(),
                          datetime(2013, 3, 23, 0, 0, 0))

        self.assertEquals(term.get_eod_last_instruction(),
                          datetime(2013, 3, 16, 0, 0, 0))

        self.assertFalse(term.is_summer_quarter())
        self.assertEquals(term.aterm_last_date, None)
        self.assertEquals(term.bterm_first_date, None)
        self.assertEquals(term.aterm_grading_period_open, None)

        self.assertEquals(len(term.time_schedule_construction), 3)
        self.assertEquals(
            term.time_schedule_construction['seattle'], False)

        self.assertEquals(len(term.time_schedule_published), 3)
        self.assertEquals(term.time_schedule_published['seattle'], True)

        self.assertFalse(term.is_grading_period_open(comparison_datetime))
        self.assertTrue(term.is_grading_period_past(comparison_datetime))
        self.assertEquals(term.term_label(), "2013,winter", "Term label")

    # Expected values will have to change when the json files are updated
    def test_next_quarter(self):
        term = get_next_term()
        self.assertTrue(term.is_summer_quarter())
        expected_quarter = "summer"
        expected_year = 2013

        comparison_datetime = datetime(2013, 4, 10, 0, 0, 0)
        self.assertTrue(term.is_future(comparison_datetime))

        self.assertEquals(term.year, expected_year,
                          "Return {} for the next year".format(
                              expected_year))

        self.assertEquals(term.quarter, expected_quarter,
                          "Return {} for the next quarter".format(
                              expected_quarter))

        self.assertEquals(term.census_day.year, 2013)
        self.assertEquals(term.census_day.month, 7)
        self.assertEquals(term.census_day.day, 5)
        self.assertEquals(term.get_eod_census_day(),
                          datetime(2013, 7, 6, 0, 0, 0))

        self.assertEquals(term.last_day_add.year, 2013)
        self.assertEquals(term.last_day_add.month, 7)
        self.assertEquals(term.last_day_add.day, 14)
        self.assertEquals(term.get_eod_last_day_add(),
                          datetime(2013, 7, 15, 0, 0, 0))

        self.assertEquals(term.last_day_drop.year, 2013)
        self.assertEquals(term.last_day_drop.month, 8)
        self.assertEquals(term.last_day_drop.day, 11)
        self.assertEquals(term.get_eod_last_day_drop(),
                          datetime(2013, 8, 12, 0, 0, 0))

        self.assertEquals(term.first_day_quarter.year, 2013)
        self.assertEquals(term.first_day_quarter.month, 6)
        self.assertEquals(term.first_day_quarter.day, 24)
        self.assertEquals(term.get_bod_first_day(),
                          datetime(2013, 6, 24, 0, 0, 0))

        self.assertEquals(term.last_day_instruction.year, 2013)
        self.assertEquals(term.last_day_instruction.month, 8)
        self.assertEquals(term.last_day_instruction.day, 23)
        self.assertEquals(term.get_eod_last_instruction(),
                          datetime(2013, 8, 24, 0, 0, 0))

        self.assertEquals(term.aterm_last_date.year, 2013)
        self.assertEquals(term.aterm_last_date.month, 7)
        self.assertEquals(term.aterm_last_date.day, 24)

        self.assertEquals(term.bterm_first_date.year, 2013)
        self.assertEquals(term.bterm_first_date.month, 7)
        self.assertEquals(term.bterm_first_date.day, 25)
        self.assertEquals(term.get_eod_summer_aterm(),
                          datetime(2013, 7, 25, 0, 0, 0))

        self.assertEquals(term.aterm_last_day_add.year, 2013)
        self.assertEquals(term.aterm_last_day_add.month, 7)
        self.assertEquals(term.aterm_last_day_add.day, 14)
        self.assertEquals(term.get_eod_aterm_last_day_add(),
                          datetime(2013, 7, 15, 0, 0, 0))

        self.assertEquals(term.bterm_last_day_add.year, 2013)
        self.assertEquals(term.bterm_last_day_add.month, 7)
        self.assertEquals(term.bterm_last_day_add.day, 31)
        self.assertEquals(term.get_eod_bterm_last_day_add(),
                          datetime(2013, 8, 1, 0, 0, 0))

        self.assertEquals(term.last_final_exam_date.year, 2013)
        self.assertEquals(term.last_final_exam_date.month, 8)
        self.assertEquals(term.last_final_exam_date.day, 23)
        self.assertEquals(term.get_eod_last_final_exam(),
                          datetime(2013, 8, 24, 0, 0, 0))

        self.assertEquals(term.grade_submission_deadline.date().year, 2013)
        self.assertEquals(term.grade_submission_deadline.date().month, 8)
        self.assertEquals(term.grade_submission_deadline.date().day, 27)
        self.assertEquals(term.grade_submission_deadline.time().hour, 17)
        self.assertEquals(term.grade_submission_deadline.time().minute, 0)
        self.assertEquals(term.get_eod_grade_submission(),
                          datetime(2013, 8, 28, 0, 0, 0))

        self.assertEquals(term.aterm_grading_period_open.date().year, 2013)
        self.assertEquals(term.aterm_grading_period_open.date().month, 7)
        self.assertEquals(term.aterm_grading_period_open.date().day, 18)
        self.assertEquals(term.aterm_grading_period_open.time().hour, 8)
        self.assertEquals(term.aterm_grading_period_open.time().minute, 0)

        self.assertEquals(len(term.time_schedule_construction), 3)
        self.assertEquals(term.time_schedule_construction['bothell'], True)

        self.assertEquals(len(term.time_schedule_published), 3)
        self.assertTrue(term.time_schedule_published['bothell'])
        comparison_datetime = datetime(2013, 9, 18, 0, 0, 0)
        self.assertFalse(term.is_grading_period_open(comparison_datetime))
        self.assertTrue(term.is_grading_period_past(comparison_datetime))
        self.assertEquals(term.term_label(), "2013,summer", "Term label")

    def test_term_before(self):
        starting = get_next_term()
        self.assertEquals(starting.year, 2013)
        self.assertEquals(starting.quarter, 'summer')

        next1 = get_term_before(starting)
        self.assertEquals(next1.year, 2013)
        self.assertEquals(next1.quarter, 'spring')

        next2 = get_term_before(next1)
        self.assertEquals(next2.year, 2013)
        self.assertEquals(next2.quarter, 'winter')

        next3 = get_term_before(next2)
        self.assertEquals(next3.year, 2012)
        self.assertEquals(next3.quarter, 'autumn')

    def test_terms_after(self):
        starting = get_next_term()
        self.assertEquals(starting.year, 2013)
        self.assertEquals(starting.quarter, 'summer')

        next_autumn = get_next_autumn_term(starting)
        next1 = get_term_after(starting)
        self.assertEquals(next1.year, 2013)
        self.assertEquals(next1.quarter, 'autumn')

        self.assertEquals(next_autumn, next1)
        next_non_summer_term = get_next_non_summer_term(get_current_term())
        self.assertEquals(next_autumn, next_non_summer_term)

        next2 = get_term_after(next1)
        self.assertEquals(next2.year, 2014)
        self.assertEquals(next2.quarter, 'winter')

    def test_specific_quarters(self):
        # Testing bad data - get_by_year_and_quarter
        self.assertRaises(DataFailureException,
                          get_term_by_year_and_quarter,
                          -2012, 'summer')

        self.assertRaises(DataFailureException,
                          get_term_by_year_and_quarter,
                          0, 'summer')

        self.assertRaises(DataFailureException,
                          get_term_by_year_and_quarter,
                          1901, 'summer')

        self.assertRaises(DataFailureException,
                          get_term_by_year_and_quarter,
                          2012, 'fall')

        self.assertRaises(DataFailureException,
                          get_term_by_year_and_quarter,
                          2012, '')

        self.assertRaises(DataFailureException,
                          get_term_by_year_and_quarter,
                          2012, ' ')

        # Equality tests
        self.assertEquals(get_term_by_year_and_quarter(2012, 'autumn'),
                          get_term_by_year_and_quarter(2012, 'autumn'))

        self.assertEquals(get_specific_term(2012, 'autumn'),
                          get_term_by_year_and_quarter(2012, 'autumn'))

        self.assertNotEquals(get_specific_term(2012, 'autumn'),
                             get_term_by_year_and_quarter(2013, 'winter'))

        # Loading a term with null Registration Periods
        term = get_term_by_year_and_quarter(2015, 'autumn')
        self.assertEquals(term.registration_services_start, None)

        # Loading a term with null Grading Periods
        term = get_term_by_year_and_quarter(1998, 'spring')
        self.assertIsNone(term.grading_period_open)
        self.assertIsNone(term.grading_period_close)
        self.assertIsNone(term.grade_submission_deadline)
        self.assertIsNone(term.aterm_grading_period_open)
        now = datetime(2013, 4, 15, 0, 0, 1)
        self.assertFalse(term.is_grading_period_open(now))
        self.assertTrue(term.is_grading_period_past(now))
        self.assertTrue(term.is_past(now))
        self.assertFalse(term.is_current(now))
        self.assertFalse(term.is_future(now))
        self.maxDiff = None
        self.assertEquals(
            term.json_data(),
            {'aterm_grading_period_open': None,
             'census_day': '1998-04-10',
             'first_day_quarter': '1998-03-30',
             'grade_submission_deadline': None,
             'grading_period_open': None,
             'label': '1998,spring',
             'last_day_add': '1998-04-19',
             'last_day_drop': '1998-05-17',
             'last_day_instruction': '1998-06-05',
             'last_final_exam_date': '1998-06-13T00:00:00',
             'quarter': 'Spring',
             'registration_periods': [
                 {'end': '1998-03-08', 'start': '1998-02-20'},
                 {'end': '1998-03-29', 'start': '1998-03-09'},
                 {'end': '1998-04-05', 'start': '1998-03-30'}],
             'time_schedule_published': {
                 'bothell': True, 'seattle': True, 'tacoma': True},
             'year': 1998}
        )

    def test_week_of_term(self):
        term = get_current_term()
        # First day of class
        start_date = datetime(2013, 4, 1, 0, 0, 1)
        self.assertEquals(term.get_week_of_term(start_date), 1,
                          "Term starting now in first week")
        self.assertEquals(term.get_week_of_term_for_date(start_date),
                          term.get_week_of_term(start_date))

        # Middle of the term
        start_date = start_date + timedelta(days=6)
        self.assertEquals(term.get_week_of_term(start_date), 1)

        start_date = start_date + timedelta(days=7)
        self.assertEquals(term.get_week_of_term(start_date), 2)

        start_date = start_date + timedelta(days=9)
        self.assertEquals(term.get_week_of_term(start_date), 4)

        start_date = datetime(2013, 4, 1, 0, 0, 1) + timedelta(weeks=11)
        self.assertEquals(term.get_week_of_term(start_date), 12)

        # Before the term
        start_date = datetime(2013, 4, 1, 0, 0, 1) - timedelta(days=1)
        self.assertEquals(term.get_week_of_term(start_date), -1)
        self.assertEquals(term.get_week_of_term_for_date(start_date), -1)

        start_date = start_date - timedelta(days=7)
        self.assertEquals(term.get_week_of_term(start_date), -2)
        self.assertEquals(term.get_week_of_term_for_date(start_date), -2)
        start_date = start_date - timedelta(days=1)
        self.assertEquals(term.get_week_of_term(start_date), -2)

    def test_canvas_sis_id(self):
        term = get_term_by_year_and_quarter(2013, 'spring')
        self.assertEquals(term.canvas_sis_id(), '2013-spring',
                          'Canvas SIS ID')

        term = get_previous_term()
        self.assertEquals(term.canvas_sis_id(), '2013-winter',
                          'Canvas SIS ID')

    def test_by_date(self):
        date = datetime.strptime("2013-01-10", "%Y-%m-%d").date()
        term = get_term_by_date(date)

        self.assertEquals(term.year, 2013)
        self.assertEquals(term.quarter, 'winter')

        date = datetime.strptime("2013-01-01", "%Y-%m-%d").date()
        term = get_term_by_date(date)

        self.assertEquals(term.year, 2012)
        self.assertEquals(term.quarter, 'autumn')

        date = datetime.strptime("2013-01-07", "%Y-%m-%d").date()
        term = get_term_by_date(date)

        self.assertEquals(term.year, 2013)
        self.assertEquals(term.quarter, 'winter')

        date = datetime.strptime("2013-01-06", "%Y-%m-%d").date()
        term = get_term_by_date(date)

        self.assertEquals(term.year, 2012)
        self.assertEquals(term.quarter, 'autumn')

        date = datetime.strptime("2013-07-04", "%Y-%m-%d").date()
        term = get_term_by_date(date)

        self.assertEquals(term.year, 2013)
        self.assertEquals(term.quarter, 'summer')

        date = datetime.strptime("2013-12-31", "%Y-%m-%d").date()
        term = get_term_by_date(date)

        self.assertEquals(term.year, 2013)
        self.assertEquals(term.quarter, 'autumn')

    def test_key(self):
        term = Term()
        term.year = 2013
        term.quarter = 'spring'
        self.assertEqual(type(term), Term)

        term1 = get_current_term()
        self.assertEqual(term, term1)
        self.assertEqual(hash(term), hash(term1))

        term2 = Term(year=2013, quarter='autumn')
        self.assertFalse(term == term2)
        self.assertFalse(hash(term) == hash(term2))

    def test_term_wo_reg_start_data(self):
        term = get_term_by_year_and_quarter(2016, 'winter')
        self.assertIsNone(term.registration_services_start)
        self.assertIsNone(term.registration_period1_start)
        self.assertIsNone(term.registration_period2_start)
        self.assertIsNone(term.registration_period3_start)
        self.assertFalse(term.time_schedule_published.get(u'seattle'))
        self.assertFalse(term.time_schedule_published.get(u'bothell'))
        self.assertFalse(term.time_schedule_published.get(u'tacoma'))

    def test_json_data(self):
        term = get_term_by_year_and_quarter(2014, 'winter')
        json_data = term.json_data()
        self.assertTrue('quarter' in json_data)
        self.assertTrue('year' in json_data)
        self.assertTrue('label' in json_data)
        self.assertTrue('last_day_add' in json_data)
        self.assertTrue('last_day_drop' in json_data)
        self.assertTrue('first_day_quarter' in json_data)
        self.assertTrue('census_day' in json_data)
        self.assertTrue('last_day_instruction' in json_data)
        self.assertTrue('grading_period_open' in json_data)
        self.assertTrue('aterm_grading_period_open' in json_data)
        self.assertTrue('grade_submission_deadline' in json_data)
        self.assertTrue('registration_periods' in json_data)
        self.assertTrue('time_schedule_published' in json_data)
        self.assertFalse(json_data['time_schedule_published']['seattle'])
        self.assertFalse(json_data['time_schedule_published']['bothell'])
        self.assertFalse(json_data['time_schedule_published']['tacoma'])

        term = get_term_by_year_and_quarter(2013, 'winter')
        json_data = term.json_data()
        self.assertTrue(json_data['time_schedule_published']['seattle'])
        self.assertTrue(json_data['time_schedule_published']['bothell'])
        self.assertTrue(json_data['time_schedule_published']['tacoma'])

    def test_lt(self):
        self.assertFalse(self.autumn2017 < self.winter2016)
        self.assertTrue(self.winter2016 < self.autumn2017)
        self.assertFalse(self.autumn2017 < self.autumn2017)

    def test_lte(self):
        self.assertFalse(self.autumn2017 <= self.winter2016)
        self.assertTrue(self.winter2016 <= self.autumn2017)
        self.assertTrue(self.autumn2017 <= self.autumn2017)

    def test_gt(self):
        self.assertTrue(self.autumn2017 > self.winter2016)
        self.assertFalse(self.winter2016 > self.autumn2017)
        self.assertFalse(self.autumn2017 > self.autumn2017)

    def test_gte(self):
        self.assertTrue(self.autumn2017 >= self.winter2016)
        self.assertFalse(self.winter2016 >= self.autumn2017)
        self.assertTrue(self.autumn2017 >= self.autumn2017)

    def test_ne(self):
        self.assertNotEqual(self.winter2016, self.autumn2017)
        self.assertFalse(self.autumn2017 != self.autumn2017)

    def test_int_key(self):
        self.assertTrue(
            self.autumn2015.int_key() < self.winter2016.int_key())
        self.assertTrue(
            self.winter2016.int_key() < self.spring2016.int_key())
        self.assertTrue(
            self.spring2016.int_key() < self.summer2016.int_key())
        self.assertTrue(
            self.summer2016.int_key() < self.autumn2016.int_key())
        self.assertTrue(
            self.autumn2016.int_key() < self.winter2017.int_key())
