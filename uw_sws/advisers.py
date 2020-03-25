"""
Interfacing with the search for a student's academic advisers
"""

from restclients_core.exceptions import DataFailureException
from uw_sws.models import StudentAdvisers
from uw_sws import get_resource

advisers_url = "/student/v5/person/{}/advisers.json"


def get_advisers(regid):
    """
    Returns a list of uw_sws.models.StudentAdvisers objects
    Return None if the SWS response if the 404 error
    """
    url = advisers_url.format(regid)
    try:
        return _process_json_data(get_resource(url))
    except DataFailureException as ex:
        if ex.status == 404:
            return None
        raise


def _process_json_data(jdata):
    ret_list = []
    if jdata.get("AcademicAdvisers") is not None:
        for adviser_data in jdata["AcademicAdvisers"]:
            ret_list.append(StudentAdvisers(data=adviser_data))
    return ret_list
