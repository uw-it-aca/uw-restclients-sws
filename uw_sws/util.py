from datetime import date, datetime, timedelta
from restclients_core.util.decorators import use_mock
from uw_sws.dao import SWS_DAO


fdao_sws_override = use_mock(SWS_DAO())


def abbr_week_month_day_str(adatetime):
    """
    Return a string consists of abbreviated weekday, abbreviated month,
    date with no leading zero, and without a year
    e.g., Mon, Jun 2. No punctuation is shown for
    the abbreviated weekday and month.
    """
    return "%s %d" % (adatetime.strftime("%a, %b"), adatetime.day)


def convert_to_begin_of_day(a_date):
    """
    @return the naive datetime object of the beginning of day
    for the give date or datetime object
    """
    if a_date is None:
        return None
    return datetime(a_date.year, a_date.month, a_date.day, 0, 0, 0)


def convert_to_end_of_day(a_date):
    """
    @return the naive datetime object of the end of day
    for the give date or datetime object
    """
    if a_date is None:
        return None
    return convert_to_begin_of_day(a_date) + timedelta(days=1)
