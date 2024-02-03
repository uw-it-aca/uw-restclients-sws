# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_sws import UWPWS
from uw_sws.dao import SWS_DAO
from restclients_core.thread import Thread


class SWSCourseThread(Thread):
    url = None  # the course url to send a request
    reg_url = None
    headers = None
    response = None
    exception = None

    def run(self):
        if self.url is None:
            raise Exception("SWSCourseThread must have a url")

        args = self.headers or {}

        try:
            self.response = SWS_DAO().getURL(self.url, args)
        except Exception as ex:
            self.exception = ex

        self.final()


class SWSPersonByRegIDThread(Thread):
    regid = None
    person = None

    def run(self):
        if self.regid is None:
            raise Exception("SWSPersonByRegIDThread must have a regid")

        self.person = UWPWS.get_person_by_regid(self.regid)

        self.final()
