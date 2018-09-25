from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.models import Term, Curriculum, Person
from restclients_core.exceptions import DataFailureException
from uw_sws.exceptions import InvalidSectionID
from uw_sws.section_status import get_section_status_by_label
from uw_sws import get_resource


@fdao_pws_override
@fdao_sws_override
class SWSTestSectionStatusData(TestCase):
    def test_section_by_label(self):
        # Valid data, shouldn't throw any exceptions
        section_status = get_section_status_by_label('2012,autumn,CSE,100/W')

        self.assertFalse(section_status.add_code_required)
        self.assertEquals(section_status.current_enrollment, 305)
        self.assertEquals(section_status.current_registration_period, 3)
        self.assertFalse(section_status.faculty_code_required)
        self.assertEquals(section_status.limit_estimated_enrollment, 345)
        self.assertEquals(
            section_status.limit_estimate_enrollment_indicator, 'limit')
        self.assertEquals(section_status.room_capacity, 345)
        self.assertEquals(section_status.sln, 12588)
        self.assertEquals(section_status.space_available, 40)
        self.assertEquals(section_status.is_open, True)
