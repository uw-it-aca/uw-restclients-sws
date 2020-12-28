"""
This class interfaces with the Student Web Service, Term resource.
"""
import logging
from uw_sws import get_resource, QUARTER_SEQ
from uw_sws.models import Term
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
    return Term(data=get_resource(url))


def get_current_term():
    """
    Returns a uw_sws.models.Term object,
    for the current term.
    """
    url = "{}/current.json".format(term_res_url_prefix)
    term = Term(data=get_resource(url))

    # A term doesn't become "current" until 2 days before the start of
    # classes.  That's too late to be useful, so if we're after the last
    # day of grade submission window, use the next term resource.
    if term.is_grading_period_past():
        return get_next_term()
    return term


def get_next_term():
    """
    Returns a uw_sws.models.Term object,
    for the next term.
    """
    url = "{}/next.json".format(term_res_url_prefix)
    return Term(data=get_resource(url))


def get_previous_term():
    """
    Returns a uw_sws.models.Term object,
    for the previous term.
    """
    url = "{}/previous.json".format(term_res_url_prefix)
    return Term(data=get_resource(url))


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
