# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


import logging
from urllib.parse import urlencode

from uw_sws import get_resource
from uw_sws.models import AdviserAssignment, AdviserReference, StudentAdviser

DEFAULT_PAGE_START = 1
DEFAULT_PAGE_SIZE = 500

adviser_search_url = "/student/v5/adviser.json"
adviser_assignments_url = "/student/v5/adviser/{}/assignments.json"
advisers_url = "/student/v5/person/{}/advisers.json"

logger = logging.getLogger(__name__)


def get_adviser_by_regid(regid, verbose=False):
    """
    Returns a uw_sws.models.AdviserReference object for the passed uwregid.
    """
    params = [
        ("adviser_reg_id", regid),
        ("verbose", "1" if verbose else "0")
    ]
    return _get_advisers_by_search(params)


def get_adviser_by_netid(netid, verbose=False):
    """
    Returns a uw_sws.models.AdviserReference object for the passed uwnetid.
    """
    params = [
        ("adviser_net_id", netid),
        ("verbose", "1" if verbose else "0")
    ]
    return _get_advisers_by_search(params)


def get_all_advisers(verbose=False):
    """
    Returns a list of uw_sws.models.AdviserReference objects.
    """
    params = [
        ("verbose", "1" if verbose else "0")
    ]
    return _get_advisers_by_search(params)


def _get_advisers_by_search(params):
    data = get_resource(f"{adviser_search_url}?{urlencode(params)}")
    ret_list = []
    for adviser_data in data.get("Advisers", []):
        ret_list.append(AdviserReference(data=adviser_data))
    return ret_list[0] if len(ret_list) == 1 else ret_list


def get_assignments_by_adviser_regid(regid):
    """
    Returns a list of AdviserAssignment objects for the passed adviser uwregid.
    This is a paginated resource.
    """
    def json_to_assignments(data):
        assignments = []
        for assignment_data in data.get("AdviserAssignments", []):
            assignments.append(AdviserAssignment(data=assignment_data))
        return assignments

    params = [
        ("page_size", DEFAULT_PAGE_SIZE),
        ("page_start", DEFAULT_PAGE_START)
    ]

    url = adviser_assignments_url.format(regid) + '?' + urlencode(params)
    data = get_resource(url)

    try:
        total_count = int(data.get("TotalCount", 0))
    except (TypeError, ValueError) as err:
        logger.error(f"AdviserAssignments TotalCount error: {err}")
        total_count = 0

    assignments = json_to_assignments(data)
    while len(assignments) and len(assignments) < total_count:
        params[-1] = ("page_start", DEFAULT_PAGE_START + len(assignments))
        url = adviser_assignments_url.format(regid) + '?' + urlencode(params)
        data = get_resource(url)
        page_assignments = json_to_assignments(data)
        if not page_assignments:
            break
        assignments.extend(page_assignments)

    return assignments


def get_advisers_by_student_regid(regid):
    """
    Returns a list of uw_sws.models.StudentAdviser objects for the passed
    student uwregid.
    """
    data = get_resource(advisers_url.format(regid))
    ret_list = []
    for adviser_data in data.get("AcademicAdvisers", []):
        ret_list.append(StudentAdviser(data=adviser_data))
    return ret_list


# Alias for the existing get_advisers_by_regid
get_advisers_by_regid = get_advisers_by_student_regid
