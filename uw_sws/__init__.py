import json
from urllib.parse import quote
from restclients_core.exceptions import DataFailureException
from uw_pws import PWS
from uw_sws.dao import SWS_DAO, SWS_TIMEZONE, sws_now

QUARTER_SEQ = ["winter", "spring", "summer", "autumn"]
DAO = SWS_DAO()
UWPWS = PWS()


def use_v5_resources():
    return True


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
