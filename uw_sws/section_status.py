# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_sws.exceptions import InvalidSectionID
from uw_sws.section import section_label_pattern
from uw_sws import get_resource, encode_section_label
from uw_sws.models import SectionStatus

course_res_url_prefix = "/student/v5/course"


def get_section_status_by_label(label):
    if not section_label_pattern.match(label):
        raise InvalidSectionID(label)

    url = "{}/{}/status.json".format(course_res_url_prefix,
                                     encode_section_label(label))

    return _json_to_sectionstatus(get_resource(url))

    pass


def _json_to_sectionstatus(section_data):
    """
    Returns a uw_sws.models.SectionStatus object
    created from the passed json.
    """
    section_status = SectionStatus()
    if section_data["AddCodeRequired"] == 'true':
        section_status.add_code_required = True
    else:
        section_status.add_code_required = False
    section_status.current_enrollment = int(section_data["CurrentEnrollment"])
    current_period = int(section_data["CurrentRegistrationPeriod"])
    section_status.current_registration_period = current_period
    if section_data["FacultyCodeRequired"] == 'true':
        section_status.faculty_code_required = True
    else:
        section_status.faculty_code_required = False

    limit_estimate = int(section_data["LimitEstimateEnrollment"])
    section_status.limit_estimated_enrollment = limit_estimate

    indicator = section_data["LimitEstimateEnrollmentIndicator"]
    section_status.limit_estimate_enrollment_indicator = indicator
    section_status.room_capacity = int(section_data["RoomCapacity"])
    section_status.sln = int(section_data["SLN"])
    section_status.space_available = int(section_data["SpaceAvailable"])
    if section_data["Status"] == "open":
        section_status.is_open = True
    else:
        section_status.is_open = False

    return section_status
