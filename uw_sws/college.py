# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the Student Web Service, College Search..
"""
import logging
from uw_sws.models import College
from uw_sws import get_resource


logger = logging.getLogger(__name__)
college_search_url = "/student/v5/college.json"


def get_all_colleges():
    """
    Returns a list of restclients.College models, representing all
    colleges.
    """
    return _json_to_colleges(get_resource(college_search_url))


def _json_to_colleges(data):
    colleges = []
    for college_data in data.get("Colleges", []):
        college = College()
        college.campus_label = college_data["CampusShortName"]
        college.label = college_data["CollegeAbbreviation"]
        college.name = college_data["CollegeName"]
        college.full_name = college_data["CollegeFullName"]
        college.clean_fields()
        colleges.append(college)

    return colleges
