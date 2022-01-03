# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Interfaceing with the Student Web Service,
 for notice resource
"""
import copy
from dateutil import parser
import logging
import pytz
from uw_sws.models import Notice, NoticeAttribute
from uw_sws import get_resource, SWS_TIMEZONE

notice_res_url_prefix = "/student/v5/notice/"
logger = logging.getLogger(__name__)


def get_notices_by_regid(regid):
    """
    Returns a list of uw_sws.models.Notice objects
    for the passed regid.
    """
    url = notice_res_url_prefix + regid + ".json"

    return _notices_from_json(get_resource(url))


def _str_to_utc(date_str):
    date = parser.parse(date_str)
    return SWS_TIMEZONE.localize(date).astimezone(pytz.utc)


def _notices_from_json(notice_data):
    notices_list = notice_data.get("Notices")
    if notices_list is None:
        return None
    notices = []
    for notice in notices_list:
        notice_obj = Notice()
        notice_obj.notice_category = notice.get("NoticeCategory")
        notice_obj.notice_content = notice.get("NoticeContent")
        notice_obj.notice_type = notice.get("NoticeType")

        notice_attribs = []
        try:
            for notice_attrib in notice.get("NoticeAttributes"):
                attribute = NoticeAttribute()
                attribute.data_type = notice_attrib.get("DataType")
                attribute.name = notice_attrib.get("Name")

                # Currently known data types
                if attribute.data_type == "url":
                    attribute._url_value = notice_attrib.get("Value")
                elif attribute.data_type == "date":
                    # Convert to UTC datetime
                    attribute._date_value = _str_to_utc(
                        notice_attrib.get("Value"))
                elif attribute.data_type == "string":
                    attribute._string_value = notice_attrib.get("Value")
                else:
                    logger.warn(
                        "Unkown attribute type: {}\nWith Value:{}".format(
                            attribute.data_type,
                            notice_attrib.get("Value")))
                    continue
                notice_attribs.append(attribute)
        except TypeError:
            pass
        notice_obj.attributes = notice_attribs
        notices.append(notice_obj)
    return _associate_short_long(notices)


def _associate_short_long(notices):
    """
    If a notice is type ${1}Short, associate with its Long notice
    in an attribute called long_notice.
    """
    for notice in notices:
        if notice.notice_type is not None and\
                notice.notice_category == "StudentFinAid" and\
                notice.notice_type.endswith("Short"):
            notice.long_notice = _find_notice_by_type(notices,
                                                      notice.notice_type[:-5])
    return notices


def _find_notice_by_type(notices, type):
    for notice in notices:
        if notice.notice_type == type:
            return notice
    return None
