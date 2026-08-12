# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_sws import encode_section_label, get_resource
from uw_sws.exceptions import InvalidSectionID
from uw_sws.models import SectionStatus
from uw_sws.section import section_label_pattern

course_res_url_prefix = "/student/v5/course"


def get_section_status_by_label(label):
    if not section_label_pattern.match(label):
        raise InvalidSectionID(label)

    url = f"{course_res_url_prefix}/{encode_section_label(label)}/status.json"
    return _json_to_sectionstatus(get_resource(url))


def _json_to_sectionstatus(section_data):
    """
    Returns a uw_sws.models.SectionStatus object
    created from the passed json.
    """
    section_status = SectionStatus()
    section_status.add_code_required = bool(
        section_data.get("AddCodeRequired", "") == "true")
    section_status.current_enrollment = int(section_data.get("CurrentEnrollment", 0))
    section_status.current_registration_period = int(
        section_data.get("CurrentRegistrationPeriod"))
    section_status.faculty_code_required = bool(
        section_data.get("FacultyCodeRequired") == "true")
    section_status.limit_estimated_enrollment = int(
        section_data.get("LimitEstimateEnrollment", 0))
    section_status.limit_estimate_enrollment_indicator = section_data.get(
        "LimitEstimateEnrollmentIndicator")
    section_status.room_capacity = int(section_data.get("RoomCapacity", 0))
    section_status.sln = section_data.get("SLN")
    section_status.space_available = int(section_data.get("SpaceAvailable", 0))
    section_status.is_open = bool(section_data.get("Status", "") == "open")

    section_status.joint_current_enrollment = int(
        section_data.get("JointCurrentEnrollment", 0))
    section_status.joint_limit_estimate_enrollment = int(
        section_data.get("JointLimitEstimateEnrollment", 0))
    section_status.joint_space_available = int(
        section_data.get("JointSpaceAvailable", 0))
    section_status.responsible_course_number = section_data.get(
        "ResponsibleCourseNumber")
    section_status.responsible_curriculum_abbreviation = section_data.get(
        "ResponsibleCurriculumAbbreviation")
    section_status.responsible_section_id = section_data.get("ResponsibleSectionID")
    section_status.responsible_section_joint_current_enrollment = int(
        section_data.get("ResponsibleSectionJointCurrentEnrollment", 0))
    section_status.responsible_section_joint_limit_estimate_enrollment = int(
        section_data.get("ResponsibleSectionJointLimitEstimateEnrollment", 0))
    section_status.responsible_section_joint_space_available = int(
        section_data.get("ResponsibleSectionJointSpaceAvailable", 0))

    return section_status
