# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from restclients_core.exceptions import DataFailureException


class ThreadedDataError(DataFailureException):
    def __init__(self, url, status, msg):
        super().__init__(url, status, msg)


class InvalidCanvasIndependentStudyCourse(Exception):
    """Exception for invalid Canvas course."""


class InvalidCanvasSection(Exception):
    """Exception for invalid Canvas section."""


class InvalidSectionID(Exception):
    """Exception for invalid section id."""


class InvalidSectionURL(Exception):
    """Exception for invalid section url."""


class InvalidCourseID(Exception):
    """Exception for invalid section id."""
