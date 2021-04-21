# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Contains SWS DAO implementations.
"""
import json
import time
import re
import random
from datetime import datetime, timedelta
from pytz import timezone
from commonconf import settings
from os.path import abspath, dirname
import os
from restclients_core.dao import DAO, MockDAO

SWS_TIMEZONE = timezone("US/Pacific")


def sws_now():
    """
    Return a naive datetime corresponding to the natural SWS timezone.
    """
    return datetime.fromtimestamp(
        int(datetime.utcnow().strftime('%s')) +
        int(datetime.now(SWS_TIMEZONE).utcoffset().total_seconds()))


class SWS_DAO(DAO):
    def service_name(self):
        return 'sws'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _custom_headers(self, method, url, headers, body):
        custom_headers = {}

        bearer_key = self.get_service_setting('OAUTH_BEARER')
        if bearer_key is not None:
            custom_headers["Authorization"] = "Bearer {}".format(bearer_key)

        return custom_headers

    def _edit_mock_response(self, method, url, headers, body, response):
        if "GET" == method:
            self._update_get(url, response)
        elif "PUT" == method:
            self._update_put(url, body, response)

    def _update_put(self, url, body, response):
        pass

    def _update_get(self, url, response):
        if "/student/v5/notice" in url:
            self._make_notice_date(response)

        # This is to enable mock data grading.
        if (re.match(r'/student/v\d/term/current.json', url) or
                re.match(r'/student/v\d/term/2013,spring.json', url)):
            now = sws_now()
            tomorrow = now + timedelta(days=1)
            yesterday = now - timedelta(days=1)
            json_data = json.loads(response.data)

            json_data["GradeSubmissionDeadline"] =\
                tomorrow.strftime("%Y-%m-%dT17:00:00")
            json_data["GradingPeriodClose"] =\
                tomorrow.strftime("%Y-%m-%dT17:00:00")
            json_data["GradingPeriodOpen"] =\
                yesterday.strftime("%Y-%m-%dT17:00:00")
            json_data["GradingPeriodOpenATerm"] =\
                yesterday.strftime("%Y-%m-%dT17:00:00")

            response.data = json.dumps(json_data)

    def _make_notice_date(self, response):
        """
        Set the date attribte value in the notice mock data
        """
        today = sws_now().date()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        week = today + timedelta(days=2)
        next_week = today + timedelta(weeks=1)
        future = today + timedelta(weeks=3)
        future_end = today + timedelta(weeks=5)

        json_data = json.loads(response.data)
        for notice in json_data["Notices"]:
            if notice["NoticeAttributes"] and\
                    len(notice["NoticeAttributes"]) > 0:
                for attr in notice["NoticeAttributes"]:
                    if attr["DataType"] == "date":
                        if attr["Value"] == "yesterday":
                            attr["Value"] = yesterday.strftime("%Y%m%d")
                        elif attr["Value"] == "today":
                            attr["Value"] = today.strftime("%Y%m%d")
                        elif attr["Value"] == "tomorrow":
                            attr["Value"] = tomorrow.strftime("%Y%m%d")
                        elif attr["Value"] == "future":
                            attr["Value"] = future.strftime("%Y%m%d")
                        elif attr["Value"] == "future_end":
                            attr["Value"] = future_end.strftime("%Y%m%d")
                        elif attr["Value"] == "next_week":
                            attr["Value"] = next_week.strftime("%Y%m%d")
                        elif attr["Value"] == "week":
                            attr["Value"] = week.strftime("%Y%m%d")
                        else:
                            pass   # use original

        response.data = json.dumps(json_data)


# For testing MUWM-2411
class TestBadResponse(MockDAO):
    def load(self, method, url, headers, body):
        if url == "/student/v5/course/2012,summer,PHYS,121/AQ.json":
            raise Exception("Uh oh!")
        return super(TestBadResponse, self).load(method, url, headers, body)
