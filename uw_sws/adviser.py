# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Interfacing with the search for a student's academic advisers

from restclients_core.exceptions import DataFailureException
from uw_sws.models import StudentAdviser
from uw_sws import get_resource

advisers_url = "/student/v5/person/{}/advisers.json"


def get_advisers_by_regid(regid):
    """
    Returns a list of uw_sws.models.StudentAdviser objects
    Raise DataFailureException if the SWS response any error
    """
    url = advisers_url.format(regid)
    return _process_json_data(get_resource(url))


def _process_json_data(jdata):
    ret_list = []
    if jdata.get("AcademicAdvisers") is not None:
        for adviser_data in jdata["AcademicAdvisers"]:
            ret_list.append(StudentAdviser(data=adviser_data))
    return ret_list
