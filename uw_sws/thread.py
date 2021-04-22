# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_sws.dao import SWS_DAO
from restclients_core.thread import Thread


class SWSThread(Thread):
    url = None  # the course url to send a request
    reg_url = None
    headers = None
    response = None
    exception = None

    def run(self):
        if self.url is None:
            raise Exception("SWSThread must have a url")

        args = self.headers or {}

        try:
            self.response = SWS_DAO().getURL(self.url, args)
        except Exception as ex:
            self.exception = ex
