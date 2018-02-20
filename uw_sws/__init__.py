from datetime import datetime
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
from uw_sws.dao import SWS_DAO
from restclients_core.exceptions import DataFailureException
import json


QUARTER_SEQ = ["winter", "spring", "summer", "autumn"]
DAO = SWS_DAO()


def use_v5_resources():
    return True


def parse_sws_date(date_string):
    """
    Takes a date from the SWS response object
    and attempts to parse it using one of the several
    datetime formats used by the SWS
    :param date_string:
    :return: date object
    """
    if date_string is None:
        return None
    date_formats = ["%m/%d/%Y", "%Y-%m-%d", "%Y%m%d"]
    datetime_obj = None
    for fmt in date_formats:
        try:
            datetime_obj = datetime.strptime(date_string, fmt)
        except ValueError:
            continue
        break
    if datetime_obj is None:
        raise ValueError("Unknown SWS date format")
    return datetime_obj


def encode_section_label(label):
    return quote(label, safe="/,")


def get_resource(url):
    """
    Issue a GET request to SWS with the given url
    and return a response in json format.
    :returns: http response with content in json
    """
    response = DAO.getURL(url, {'Accept': 'application/json',
                                'Connection': 'keep-alive'})
    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)
    return json.loads(response.data)
