# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase
from datetime import date, datetime
import pytz
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.notice import get_notices_by_regid
from uw_sws.dao import sws_now, SWS_TIMEZONE
from uw_sws.util import str_to_date
from datetime import timedelta


def date_to_dtime(adate):
    return str(SWS_TIMEZONE.localize(
        datetime(year=adate.year, month=adate.month,
                 day=adate.day)).astimezone(pytz.utc))


@fdao_pws_override
@fdao_sws_override
class SWSNotice(TestCase):

    def test_notice_resource(self):
        notices = get_notices_by_regid("9136CCB8F66711D5BE060004AC494FFE")
        self.assertEquals(len(notices), 17)

        today = sws_now().date()
        yesterday = date_to_dtime(today - timedelta(days=1))
        tomorrow = date_to_dtime(today + timedelta(days=1))
        week = date_to_dtime(today + timedelta(days=2))
        next_week = date_to_dtime(today + timedelta(weeks=1))
        future = date_to_dtime(today + timedelta(weeks=3))
        future_end = date_to_dtime(today + timedelta(weeks=5))

        notice = notices[0]
        self.assertEquals(notice.notice_category, "StudentALR")
        self.assertEquals(notice.notice_type, "IntlStuCheckIn")
        attribute = notice.attributes[1]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), yesterday)

        notice = notices[1]
        self.assertEquals(notice.notice_category, "StudentDAD")
        self.assertEquals(notice.notice_type, "QtrBegin")
        self.assertEquals(notice.notice_content,
                          "Summer quarter begins <b>June 23, 2014</b>")

        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), future_end)

        attribute = notice.attributes[3]
        self.assertEquals(attribute.name, "Quarter")
        self.assertEquals(attribute.data_type, "string")
        self.assertEquals(attribute.get_value(), "Summer")

        attribute = notice.attributes[4]
        self.assertEquals(attribute.name, "Link")
        self.assertEquals(attribute.data_type, "url")
        self.assertEquals(attribute.get_value(), "http://www.uw.edu")

        # Ensure unknown attributes aren't included
        self.assertEquals(len(notice.attributes), 5)

        # Default custom category
        self.assertEquals(notice.custom_category, "Uncategorized")

        notice = notices[2]
        self.assertEquals(notice.notice_category, "StudentDAD")
        self.assertEquals(notice.notice_type, "EstPd1RegDate")
        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), next_week)

        notice = notices[3]
        self.assertEquals(notice.notice_category, "StudentALR")
        self.assertEquals(notice.notice_type, "PreRegNow")
        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), week)

        notice = notices[4]
        self.assertEquals(notice.notice_category, "StudentALR")
        self.assertEquals(notice.notice_type, "PreRegNow")
        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), week)

        notice = notices[4]
        self.assertEquals(notice.notice_category, "StudentALR")
        self.assertEquals(notice.notice_type, "PreRegNow")
        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), week)

        notice = notices[5]
        self.assertEquals(notice.notice_category, "StudentALR")
        self.assertEquals(notice.notice_type, "IntlStuCheckIn")
        self.assertEquals(len(notice.attributes), 0)

        notice = notices[7]
        self.assertEquals(notice.notice_category, "StudentGEN")
        self.assertEquals(notice.notice_type, "AcctBalance")
        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), next_week)

        notice = notices[8]
        self.assertEquals(notice.notice_category, "StudentDAD")
        self.assertEquals(notice.notice_type, "TuitDue")
        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), next_week)

        notice = notices[12]
        self.assertEquals(notice.notice_category, "StudentDAD")
        self.assertEquals(notice.notice_type, "QtrEnd")
        attribute = notice.attributes[0]
        self.assertEquals(attribute.name, "Date")
        self.assertEquals(attribute.data_type, "date")
        self.assertEquals(attribute.get_value(), future_end)

        notice = notices[13]
        self.assertEquals(notice.notice_category, "StudentFinAid")
        self.assertEquals(notice.notice_type, "DirectDeposit")

        notice = notices[14]
        self.assertEquals(notice.notice_category, "StudentFinAid")
        self.assertEquals(notice.notice_type, "DirectDepositShort")
        self.assertEquals(notice.long_notice.notice_type, "DirectDeposit")

        notice = notices[15]
        self.assertEquals(notice.notice_category, "StudentFinAid")
        self.assertEquals(notice.notice_type, "AidPriorityDate")

        notice = notices[16]
        self.assertEquals(notice.notice_category, "StudentFinAid")
        self.assertEquals(notice.notice_type, "AidPriorityDateShort")
        self.assertEquals(notice.long_notice.notice_type, "AidPriorityDate")
