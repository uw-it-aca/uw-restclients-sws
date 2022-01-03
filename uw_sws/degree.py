# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Interfacing with the search for a student's degree status

from uw_sws.models import DegreeStatus
from uw_sws import get_resource

degree_url = "/student/v5/person/{}/degree.json?deg_status=all"


def get_degrees_by_regid(regid):
    """
    Returns a list of uw_sws.models.DegreeStatus objects
    Raise DataFailureException if the SWS response any error
    """
    url = degree_url.format(regid)
    return _process_json_data(get_resource(url))


def _process_json_data(jdata):
    ret_list = []
    if jdata.get("Degrees") is not None:
        for data in jdata["Degrees"]:
            ret_list.append(DegreeStatus(data=data))
    return ret_list
