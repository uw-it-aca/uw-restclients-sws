"""
This class interfaces with the Student Web Service, Term resource.
"""
import logging
from datetime import datetime
from uw_sws import get_resource, QUARTER_SEQ
from uw_sws.models import Term as TermModel
from restclients_core.exceptions import DataFailureException


term_res_url_prefix = "/student/v5/term"
logger = logging.getLogger(__name__)


def get_term_by_year_and_quarter(year, quarter):
    """
    Returns a uw_sws.models.Term object,
    for the passed year and quarter.
    """
    url = "{}/{},{}.json".format(
        term_res_url_prefix, year, quarter.lower())
    return _json_to_term_model(get_resource(url))


def get_current_term():
    """
    Returns a uw_sws.models.Term object,
    for the current term.
    """
    url = "{}/current.json".format(term_res_url_prefix)
    term = _json_to_term_model(get_resource(url))

    # A term doesn't become "current" until 2 days before the start of
    # classes.  That's too late to be useful, so if we're after the last
    # day of grade submission window, use the next term resource.
    if datetime.now() > term.grade_submission_deadline:
        return get_next_term()

    return term


def get_next_term():
    """
    Returns a uw_sws.models.Term object,
    for the next term.
    """
    url = "{}/next.json".format(term_res_url_prefix)
    return _json_to_term_model(get_resource(url))


def get_previous_term():
    """
    Returns a uw_sws.models.Term object,
    for the previous term.
    """
    url = "{}/previous.json".format(term_res_url_prefix)
    return _json_to_term_model(get_resource(url))


def get_term_before(aterm):
    """
    Returns a uw_sws.models.Term object,
    for the term before the term given.
    """
    prev_year = aterm.year
    prev_quarter = QUARTER_SEQ[QUARTER_SEQ.index(aterm.quarter) - 1]

    if prev_quarter == "autumn":
        prev_year -= 1

    return get_term_by_year_and_quarter(prev_year, prev_quarter)


def get_term_after(aterm):
    """
    Returns a uw_sws.models.Term object,
    for the term after the term given.
    """
    next_year = aterm.year
    if aterm.quarter == "autumn":
        next_quarter = QUARTER_SEQ[0]
    else:
        next_quarter = QUARTER_SEQ[QUARTER_SEQ.index(aterm.quarter) + 1]

    if next_quarter == "winter":
        next_year += 1

    return get_term_by_year_and_quarter(next_year, next_quarter)


def get_term_by_date(date):
    """
    Returns a term for the datetime.date object given.
    """
    year = date.year

    term = None
    for quarter in ('autumn', 'summer', 'spring', 'winter'):
        term = get_term_by_year_and_quarter(year, quarter)

        if date >= term.first_day_quarter:
            break

    # If we're in a year, before the start of winter quarter, we need to go
    # to the previous year's autumn term:
    if date < term.first_day_quarter:
        term = get_term_by_year_and_quarter(year - 1, 'autumn')

    # Autumn quarter should always last through the end of the year,
    # with winter of the next year starting in January.  But this makes sure
    # we catch it if not.
    term_after = get_term_after(term)
    if term_after.first_day_quarter > date:
        return term
    else:
        return term_after

    pass


def _json_to_term_model(term_data):
    """
    Returns a term model created from the passed json data.
    param: term_data loaded json data
    """
    def to_dt(s, fmt):
        return datetime.strptime(s, fmt) if s is not None else None

    date_fmt = "%Y-%m-%d"
    datetime_fmt = "%Y-%m-%dT%H:%M:%S"

    term = TermModel()
    term.year = term_data["Year"]
    term.quarter = term_data["Quarter"]

    term.last_day_add = to_dt(term_data["LastAddDay"], date_fmt)
    term.first_day_quarter = to_dt(term_data["FirstDay"], date_fmt)
    term.last_day_instruction = to_dt(term_data["LastDayOfClasses"], date_fmt)
    term.last_day_drop = to_dt(term_data["LastDropDay"], date_fmt)
    term.census_day = to_dt(term_data["CensusDay"], date_fmt)
    term.aterm_last_date = to_dt(term_data["ATermLastDay"], date_fmt)
    term.bterm_first_date = to_dt(term_data["BTermFirstDay"], date_fmt)
    term.aterm_last_day_add = to_dt(term_data["LastAddDayATerm"], date_fmt)
    term.bterm_last_day_add = to_dt(term_data["LastAddDayBTerm"], date_fmt)
    term.last_final_exam_date = to_dt(term_data["LastFinalExamDay"], date_fmt)
    term.grading_period_open = to_dt(
        term_data["GradingPeriodOpen"], datetime_fmt)
    term.aterm_grading_period_open = to_dt(
        term_data["GradingPeriodOpenATerm"], datetime_fmt)
    term.grading_period_close = to_dt(
        term_data["GradingPeriodClose"], datetime_fmt)
    term.grade_submission_deadline = to_dt(
        term_data["GradeSubmissionDeadline"], datetime_fmt)
    term.registration_services_start = to_dt(
        term_data["RegistrationServicesStart"], date_fmt)
    term.registration_period1_start = to_dt(
        term_data["RegistrationPeriods"][0]["StartDate"], date_fmt)
    term.registration_period1_end = to_dt(
        term_data["RegistrationPeriods"][0]["EndDate"], date_fmt)
    term.registration_period2_start = to_dt(
        term_data["RegistrationPeriods"][1]["StartDate"], date_fmt)
    term.registration_period2_end = to_dt(
        term_data["RegistrationPeriods"][1]["EndDate"], date_fmt)
    term.registration_period3_start = to_dt(
        term_data["RegistrationPeriods"][2]["StartDate"], date_fmt)
    term.registration_period3_end = to_dt(
        term_data["RegistrationPeriods"][2]["EndDate"], date_fmt)

    term.time_schedule_construction = {}
    for campus in term_data["TimeScheduleConstruction"]:
        term.time_schedule_construction[campus.lower()] = True if (
            term_data["TimeScheduleConstruction"][campus]) else False

    term.time_schedule_published = {}
    for campus in term_data["TimeSchedulePublished"]:
        term.time_schedule_published[campus.lower()] = True if (
            term_data["TimeSchedulePublished"][campus]) else False

    term.clean_fields()
    return term


def get_specific_term(year, quarter):
    """
    Rename the get_term_by_year_and_quarter to a short name.
    """
    return get_term_by_year_and_quarter(year, quarter.lower())


def get_next_autumn_term(term):
    """
    Return the Term object for the next autumn quarter
    in the same year as the given term
    """
    return get_specific_term(term.year, 'autumn')


def get_next_non_summer_term(term):
    """
    Return the Term object for the quarter after
    as the given term (skip the summer quarter)
    """
    next_term = get_term_after(term)
    if next_term.is_summer_quarter():
        return get_next_autumn_term(next_term)
    return next_term
