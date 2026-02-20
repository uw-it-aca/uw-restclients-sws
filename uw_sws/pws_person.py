# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfacing with the PWS, Person resource
"""
import logging
from uw_sws import UWPWS
from uw_sws.worker import PersonGetter


logger = logging.getLogger(__name__)


class PWSPersonGetter(PersonGetter):
    """
    Get PWS Person object for a list of regids
    """

    def task(self, tid):
        return UWPWS.get_person_by_regid(tid)
