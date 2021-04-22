# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Code for (old) restclients compatability.  None of this should be needed, but
it's here in the interest of not changing restclients tests during the move
to individual client libraries.
"""
import warnings


def get_current_sws_version():
    return 5


def use_v5_resources():
    return True


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


class SWS(object):
    """
    The SWS object has methods for getting information
    about courses, and everything related.
    """

    def get_term_by_year_and_quarter(self, year, quarter):
        deprecation("Use uw_sws.term.get_term_by_year_and_quarter")
        from uw_sws.term import get_term_by_year_and_quarter
        return get_term_by_year_and_quarter(year, quarter)

    def get_current_term(self):
        deprecation("Use uw_sws.term.get_current_term")
        from uw_sws.term import get_current_term
        return get_current_term()

    def get_next_term(self):
        deprecation("Use uw_sws.term.get_next_term")
        from uw_sws.term import get_next_term
        return get_next_term()

    def get_previous_term(self):
        deprecation("Use uw_sws.term.get_previous_term")
        from uw_sws.term import get_previous_term
        return get_previous_term()

    def get_term_before(self, aterm):
        deprecation("Use uw_sws.term.get_term_before")
        from uw_sws.term import get_term_before
        return get_term_before(aterm)

    def get_term_after(self, aterm):
        deprecation("Use uw_sws.term.get_term_after")
        from uw_sws.term import get_term_after
        return get_term_after(aterm)

    def get_sections_by_instructor_and_term(self, person, term):
        deprecation("Use uw_sws.section.get_sections_by_instructor_and_term")
        from uw_sws.section import get_sections_by_instructor_and_term
        return get_sections_by_instructor_and_term(person, term)

    def get_sections_by_delegate_and_term(self, person, term):
        deprecation("Use uw_sws.section.get_sections_by_delegate_and_term")
        from uw_sws.section import get_sections_by_delegate_and_term
        return get_sections_by_delegate_and_term(person, term)

    def get_sections_by_curriculum_and_term(self, curriculum, term):
        deprecation("Use uw_sws.section.get_sections_by_curriculum_and_term")
        from uw_sws.section import get_sections_by_curriculum_and_term
        return get_sections_by_curriculum_and_term(curriculum, term)

    def get_section_by_label(self, label,
                             include_instructor_not_on_time_schedule=True):
        deprecation("Use uw_sws.section.get_section_by_label")
        from uw_sws.section import get_section_by_label
        return get_section_by_label(label,
                                    include_instructor_not_on_time_schedule)

    def get_section_by_url(self, url,
                           include_instructor_not_on_time_schedule=True):
        deprecation("Use uw_sws.section.get_section_by_url")
        from uw_sws.section import get_section_by_url
        return get_section_by_url(url, include_instructor_not_on_time_schedule)

    def get_section_status_by_label(self, label):
        deprecation("Use uw_sws.section.get_section_status_by_label")
        from uw_sws.section_status import get_section_status_by_label
        return get_section_status_by_label(label)

    def get_linked_sections(self, asection,
                            include_instructor_not_on_time_schedule=True):
        deprecation("Use uw_sws.section.get_linked_sections")
        from uw_sws.section import get_linked_sections
        return get_linked_sections(asection,
                                   include_instructor_not_on_time_schedule)

    def get_joint_sections(self, asection,
                           include_instructor_not_on_time_schedule=True):
        deprecation("Use uw_sws.section.get_joint_sections")
        from uw_sws.section import get_joint_sections
        return get_joint_sections(asection,
                                  include_instructor_not_on_time_schedule)

    def get_all_registrations_for_section(self, section):
        deprecation(
            "Use uw_sws.registration.get_all_registrations_by_section")
        from uw_sws.registration import get_all_registrations_by_section
        return get_all_registrations_by_section(section)

    def get_active_registrations_for_section(self, section):
        deprecation(
            "Use uw_sws.registration.get_active_registrations_by_section")
        from uw_sws.registration import get_active_registrations_by_section
        return get_active_registrations_by_section(section)

    def short_name(self, regid, term,
                   include_instructor_not_on_time_schedule=True):

        x = include_instructor_not_on_time_schedule
        return self.schedule_for_regid_and_term(regid, term, x)

    def schedule_for_regid_and_term(self, *args, **kwargs):
        deprecation(
            "Use uw_sws.registration.get_schedule_by_regid_and_term")
        from uw_sws.registration import get_schedule_by_regid_and_term
        return get_schedule_by_regid_and_term(*args, **kwargs)

    def grades_for_regid_and_term(self, regid, term):
        deprecation(
            "Use uw_sws.enrollment.get_grades_by_regid_and_term")
        from uw_sws.enrollment import get_grades_by_regid_and_term
        return get_grades_by_regid_and_term(regid, term)

    def get_all_campuses(self):
        deprecation(
            "Use uw_sws.campus.get_all_campuses")
        from uw_sws.campus import get_all_campuses
        return get_all_campuses()

    def get_all_colleges(self):
        deprecation(
            "Use uw_sws.college.get_all_colleges")
        from uw_sws.college import get_all_colleges
        return get_all_colleges()

    def get_departments_for_college(self, college):
        deprecation(
            "Use uw_sws.department.get_departments_by_college")
        from uw_sws.department import get_departments_by_college
        return get_departments_by_college(college)

    def get_curricula_for_department(self, department, future_terms=0):
        deprecation(
            "Use uw_sws.curriculum.get_curricula_by_department")
        from uw_sws.curriculum import get_curricula_by_department
        return get_curricula_by_department(department, future_terms)

    def get_curricula_for_term(self, term):
        deprecation(
            "Use uw_sws.curriculum.get_curricula_by_term")
        from uw_sws.curriculum import get_curricula_by_term
        return get_curricula_by_term(term)
