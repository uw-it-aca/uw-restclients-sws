from datetime import date, datetime, timedelta
from pytz import timezone
from dateutil.parser import parse
from restclients_core.util.decorators import use_mock
from uw_sws.dao import SWS_DAO

fdao_sws_override = use_mock(SWS_DAO())

SWS_TIMEZONE = timezone("US/Pacific")


def sws_now():
    """
    Return a naive datetime corresponding to the natural SWS timezone.
    """
    return datetime.fromtimestamp(
        int(datetime.utcnow().strftime('%s')) +
        int(datetime.now(SWS_TIMEZONE).utcoffset().total_seconds()))


def str_to_datetime(s):
    return parse(s) if (s is not None and len(s)) else None


def str_to_date(s):
    dt = str_to_datetime(s)
    return dt.date() if dt is not None else None


def date_to_str(dt):
    return str(dt) if dt is not None else None


def abbr_week_month_day_str(adatetime):
    """
    Return a string consists of abbreviated weekday, abbreviated month,
    date with no leading zero, and without a year
    e.g., Mon, Jun 2. No punctuation is shown for
    the abbreviated weekday and month.
    """
    return "{} {:d}".format(adatetime.strftime("%a, %b"), adatetime.day)


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
