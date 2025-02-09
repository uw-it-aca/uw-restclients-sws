# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the Student Web Service, Department Search.
"""
import logging
from urllib.parse import urlencode
from uw_sws.models import Department
from uw_sws.term import get_current_term
from uw_sws import get_resource


logger = logging.getLogger(__name__)
dept_search_url_prefix = "/student/v5/department.json"


def get_departments_by_college(college, term=None):
    """
    Returns a list of restclients.Department models, for the passed
    College model.
    """
    if term is None:
        term = get_current_term()

    url = "{}?{}".format(dept_search_url_prefix, urlencode([
        ("college_abbreviation", college.label,),
        ("year", term.year,),
        ("quarter", term.quarter,)
    ]))
    return _json_to_departments(get_resource(url), college)


def _json_to_departments(data, college):
    departments = []
    for dept_data in data.get("Departments", []):
        department = Department()
        department.college_label = college.label
        department.label = dept_data["DepartmentAbbreviation"]
        department.name = dept_data["DepartmentFullName"]
        department.full_name = dept_data["DepartmentFullName"]
        department.clean_fields()
        departments.append(department)

    return departments
