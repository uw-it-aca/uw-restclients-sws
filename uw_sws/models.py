import json
import re
from uw_pws.models import Person
from uw_sws.exceptions import (
    InvalidCanvasIndependentStudyCourse, InvalidCanvasSection)
from uw_sws.util import (
    abbr_week_month_day_str, convert_to_begin_of_day, convert_to_end_of_day,
    str_to_datetime, str_to_date, date_to_str)
from uw_sws.dao import sws_now
from restclients_core import models

SWS_TERM_LABEL = "{year},{quarter}"
SWS_SECTION_LABEL = "{year},{quarter},{curr_abbr},{course_num}/{section_id}"

CANVAS_TERM_ID = "{year}-{quarter}"
CANVAS_COURSE_ID = "{year}-{quarter}-{curr_abbr}-{course_num}-{section_id}"
CANVAS_IND_STUDY_COURSE_ID = (
    "{year}-{quarter}-{curr_abbr}-{course_num}-{section_id}-{inst_regid}")


class LastEnrolled(models.Model):
    href = models.CharField(max_length=200)
    quarter = models.CharField(max_length=16)
    year = models.PositiveSmallIntegerField()

    def json_data(self):
        return {'href': self.href,
                'quarter': self.quarter,
                'year': self.year
                }

    def __str__(self):
        return json.dumps(self.json_data())


class StudentAddress(models.Model):
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    street_line1 = models.CharField(max_length=255)
    street_line2 = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=32)
    state = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=32)

    def json_data(self):
        return {'city': self.city,
                'country': self.country,
                'street_line1': self.street_line1,
                'street_line2': self.street_line2,
                'postal_code': self.postal_code,
                'state': self.state,
                'zip_code': self.zip_code
                }

    def __str__(self):
        return json.dumps(self.json_data())


def get_student_address_json(address):
    if address is not None:
        return address.json_data()
    return None


class SwsPerson(models.Model):
    uwregid = models.CharField(max_length=32,
                               db_index=True,
                               unique=True)
    uwnetid = models.SlugField(max_length=16,
                               db_index=True,
                               unique=True)
    birth_date = models.DateField(null=True, default=None)
    directory_release = models.NullBooleanField(null=True)
    employee_id = models.SlugField(max_length=16, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    pronouns = models.CharField(max_length=64, null=True, blank=True)
    student_name = models.CharField(max_length=255)
    student_number = models.SlugField(max_length=16, null=True, blank=True)
    student_system_key = models.SlugField(max_length=16, null=True, blank=True)
    last_enrolled = models.ForeignKey(
        LastEnrolled,
        on_delete=models.PROTECT,
        null=True)
    local_address = models.ForeignKey(
        StudentAddress,
        on_delete=models.PROTECT,
        null=True,
        related_name='local_address')
    local_phone = models.CharField(max_length=64, null=True, blank=True)
    permanent_address = models.ForeignKey(
        StudentAddress,
        on_delete=models.PROTECT,
        null=True,
        related_name='permanent_address')
    permanent_phone = models.CharField(max_length=64, null=True, blank=True)
    visa_type = models.CharField(max_length=2, null=True, blank=True)

    def is_F1(self):
        return self.visa_type is not None and self.visa_type.lower() == 'f1'

    def is_J1(self):
        return self.visa_type is not None and self.visa_type.lower() == 'j1'

    def json_data(self):
        return {
            'uwnetid': self.uwnetid,
            'uwregid': self.uwregid,
            'birth_date': date_to_str(self.birth_date),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'pronouns': self.pronouns,
            'student_name': self.student_name,
            'student_number': self.student_number,
            'employee_id': self.employee_id,
            'directory_release': self.directory_release,
            'local_address': get_student_address_json(self.local_address),
            'local_phone': self.local_phone,
            'permanent_address': get_student_address_json(
                self.permanent_address),
            'permanent_phone': self.permanent_phone,
            'visa_type': self.visa_type
                }

    def __str__(self):
        return json.dumps(self.json_data())


class Term(models.Model):
    SPRING = 'spring'
    SUMMER = 'summer'
    AUTUMN = 'autumn'
    WINTER = 'winter'

    QUARTERNAME_CHOICES = (
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
        (AUTUMN, 'Autumn'),
        (WINTER, 'Winter'),
    )

    quarter = models.CharField(max_length=6,
                               choices=QUARTERNAME_CHOICES)
    year = models.PositiveSmallIntegerField()
    last_day_add = models.DateField()
    last_day_drop = models.DateField()
    first_day_quarter = models.DateField()
    census_day = models.DateField()
    last_day_instruction = models.DateField()
    aterm_last_date = models.DateField(null=True)
    bterm_first_date = models.DateField(null=True)
    aterm_last_day_add = models.DateField(null=True)
    bterm_last_day_add = models.DateField(null=True)
    last_final_exam_date = models.DateField()
    grading_period_open = models.DateTimeField(null=True)
    aterm_grading_period_open = models.DateTimeField(null=True)
    grading_period_close = models.DateTimeField(null=True)
    grade_submission_deadline = models.DateTimeField(null=True)
    registration_services_start = models.DateField(null=True)
    registration_period1_start = models.DateField(null=True)
    registration_period1_end = models.DateField(null=True)
    registration_period2_start = models.DateField(null=True)
    registration_period2_end = models.DateField(null=True)
    registration_period3_start = models.DateField(null=True)
    registration_period3_end = models.DateField(null=True)

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data is None:
            return super(Term, self).__init__(*args, **kwargs)

        self.year = data["Year"]
        self.quarter = data["Quarter"]
        self.last_day_add = str_to_date(data["LastAddDay"])
        self.first_day_quarter = str_to_date(data["FirstDay"])
        self.last_day_instruction = str_to_date(data["LastDayOfClasses"])
        self.last_day_drop = str_to_date(data["LastDropDay"])
        self.census_day = str_to_date(data["CensusDay"])
        self.aterm_last_date = str_to_date(data["ATermLastDay"])
        self.bterm_first_date = str_to_date(data["BTermFirstDay"])
        self.aterm_last_day_add = str_to_date(data["LastAddDayATerm"])
        self.bterm_last_day_add = str_to_date(data["LastAddDayBTerm"])
        self.last_final_exam_date = str_to_date(data["LastFinalExamDay"])
        self.grading_period_open = str_to_datetime(data["GradingPeriodOpen"])
        self.aterm_grading_period_open = str_to_datetime(
            data["GradingPeriodOpenATerm"])
        self.grading_period_close = str_to_datetime(data["GradingPeriodClose"])
        self.grade_submission_deadline = str_to_datetime(
            data["GradeSubmissionDeadline"])
        self.registration_services_start = str_to_date(
            data["RegistrationServicesStart"])
        self.registration_period1_start = str_to_date(
            data["RegistrationPeriods"][0]["StartDate"])
        self.registration_period1_end = str_to_date(
            data["RegistrationPeriods"][0]["EndDate"])
        self.registration_period2_start = str_to_date(
            data["RegistrationPeriods"][1]["StartDate"])
        self.registration_period2_end = str_to_date(
            data["RegistrationPeriods"][1]["EndDate"])
        self.registration_period3_start = str_to_date(
            data["RegistrationPeriods"][2]["StartDate"])
        self.registration_period3_end = str_to_date(
            data["RegistrationPeriods"][2]["EndDate"])

        self.time_schedule_construction = {}
        for campus in data["TimeScheduleConstruction"]:
            self.time_schedule_construction[campus.lower()] = True if (
                data["TimeScheduleConstruction"][campus]) else False

        self.time_schedule_published = {}
        for campus in data["TimeSchedulePublished"]:
            self.time_schedule_published[campus.lower()] = True if (
                data["TimeSchedulePublished"][campus]) else False

    @staticmethod
    def _quarter_to_int(quarter):
        if quarter.lower() == Term.WINTER:
            return 1
        if quarter.lower() == Term.SPRING:
            return 2
        if quarter.lower() == Term.SUMMER:
            return 3
        return 4

    def int_key(self):
        return int(self.year) * 10 + self._quarter_to_int(self.quarter)

    def __eq__(self, other):
        return (other is not None and
                type(self) == type(other) and
                self.int_key() == other.int_key())

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return (type(self) == type(other) and
                self.int_key() < other.int_key())

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        return (type(self) == type(other) and
                self.int_key() > other.int_key())

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __hash__(self):
        return hash(self.__key())

    def __key(self):
        return (str(self.year), self.quarter)

    def is_grading_period_open(self, cmp_dt=None):
        if cmp_dt is None:
            cmp_dt = sws_now()

        if self.is_summer_quarter():
            open_date = self.aterm_grading_period_open
        else:
            open_date = self.grading_period_open

        return (open_date is not None and
                self.grade_submission_deadline is not None and
                open_date <= cmp_dt <= self.grade_submission_deadline)

    def is_grading_period_past(self, cmp_dt=None):
        if cmp_dt is None:
            cmp_dt = sws_now()
        return (self.grade_submission_deadline is None or
                cmp_dt > self.grade_submission_deadline)

    def get_week_of_term(self, cmp_dt=None):
        if cmp_dt is None:
            cmp_dt = sws_now()
        return self.get_week_of_term_for_date(cmp_dt)

    def get_week_of_term_for_date(self, date):
        days = (date.date() - self.first_day_quarter).days
        if days >= 0:
            return (days // 7) + 1

        return (days // 7)

    def get_bod_first_day(self):
        # returns a datetime object of the midnight at begining of day
        return convert_to_begin_of_day(self.first_day_quarter)

    def get_bod_reg_period1_start(self):
        return convert_to_begin_of_day(self.registration_period1_start)

    def get_bod_reg_period2_start(self):
        return convert_to_begin_of_day(self.registration_period2_start)

    def get_bod_reg_period3_start(self):
        return convert_to_begin_of_day(self.registration_period3_start)

    def get_eod_grade_submission(self):
        # returns a datetime object of the midnight at end of day
        return convert_to_end_of_day(self.grade_submission_deadline)

    def get_end_of_the_term(self):
        return self.get_eod_grade_submission()

    def get_eod_aterm_last_day_add(self):
        if not self.is_summer_quarter():
            return None
        return convert_to_end_of_day(self.aterm_last_day_add)

    def get_eod_bterm_last_day_add(self):
        if not self.is_summer_quarter():
            return None
        return convert_to_end_of_day(self.bterm_last_day_add)

    def get_eod_last_day_add(self):
        return convert_to_end_of_day(self.last_day_add)

    def get_eod_last_day_drop(self):
        return convert_to_end_of_day(self.last_day_drop)

    def get_eod_census_day(self):
        return convert_to_end_of_day(self.census_day)

    def get_eod_last_final_exam(self):
        return convert_to_end_of_day(self.last_final_exam_date)

    def get_eod_last_instruction(self):
        return convert_to_end_of_day(self.last_day_instruction)

    def get_eod_summer_aterm(self):
        if not self.is_summer_quarter():
            return None
        return convert_to_end_of_day(self.aterm_last_date)

    def is_current(self, cmp_dt):
        return (self.get_end_of_the_term() is not None and
                self.get_bod_first_day() < cmp_dt and
                cmp_dt < self.get_end_of_the_term())

    def is_past(self, cmp_dt):
        return (self.get_end_of_the_term() is None and
                cmp_dt > self.get_eod_last_final_exam() or
                cmp_dt > self.get_end_of_the_term())

    def is_future(self, cmp_dt):
        return cmp_dt < self.get_bod_first_day()

    def is_summer_quarter(self):
        return self.quarter.lower() == Term.SUMMER

    def term_label(self):
        return SWS_TERM_LABEL.format(year=self.year, quarter=self.quarter)

    def canvas_sis_id(self):
        return CANVAS_TERM_ID.format(
            year=self.year, quarter=self.quarter.lower())

    def json_data(self):
        registration_period = []
        if self.registration_period1_start:
            registration_period.append({
                'start': date_to_str(self.registration_period1_start),
                'end': date_to_str(self.registration_period1_end)
            })
        if self.registration_period2_start:
            registration_period.append({
                'start': date_to_str(self.registration_period2_start),
                'end': date_to_str(self.registration_period2_end)
            })
        if self.registration_period3_start:
            registration_period.append({
                'start': date_to_str(self.registration_period3_start),
                'end': date_to_str(self.registration_period3_end)
            })

        time_schedule_published = {}
        for key in self.time_schedule_published:
            time_schedule_published[key] = self.time_schedule_published[key]

        data = {
            'quarter': self.get_quarter_display(),
            'year': self.year,
            'label': self.term_label(),
            'last_day_add': date_to_str(self.last_day_add),
            'last_day_drop': date_to_str(self.last_day_drop),
            'first_day_quarter': date_to_str(self.first_day_quarter),
            'census_day': date_to_str(self.census_day),
            'last_day_instruction': date_to_str(self.last_day_instruction),
            'grading_period_open': date_to_str(self.grading_period_open),
            'aterm_grading_period_open': date_to_str(
                self.aterm_grading_period_open),
            'grade_submission_deadline': date_to_str(
                self.grade_submission_deadline),
            'registration_periods': registration_period,
            'time_schedule_published': time_schedule_published
        }
        if self.last_final_exam_date:
            data['last_final_exam_date'] = self.last_final_exam_date.strftime(
                "%Y-%m-%d 23:59:59")  # Datetime for backwards compatibility
        return data

    def __str__(self):
        return json.dumps(self.json_data())


class FinalExam(models.Model):
    is_confirmed = models.NullBooleanField()
    no_exam_or_nontraditional = models.NullBooleanField()
    start_date = models.DateTimeField(null=True, default=None)  # StartTime
    end_date = models.DateTimeField(null=True, default=None)  # EndTime
    building = models.CharField(max_length=20, null=True, blank=True)
    room_number = models.CharField(max_length=10, null=True, blank=True)

    def json_data(self):
        data = {
            "is_confirmed": self.is_confirmed,
            "no_exam_or_nontraditional": self.no_exam_or_nontraditional,
        }

        if self.start_date:
            data["start_date"] = self.start_date.strftime("%Y-%m-%d %H:%M")
            data["end_date"] = self.end_date.strftime("%Y-%m-%d %H:%M")
        if self.building:
            data["building"] = self.building
        if self.room_number:
            data["room_number"] = self.room_number
            data["room"] = self.room_number
        return data

    def __str__(self):
        return json.dumps(self.json_data())


class Section(models.Model):
    INSTITUTE_NAME_PCE = "UW PROFESSIONAL AND CONTINUING EDUCATION"
    EARLY_FALL_START = "EARLY FALL START"
    SUMMER_A_TERM = "a-term"
    SUMMER_B_TERM = "b-term"
    SUMMER_FULL_TERM = "full-term"

    LMS_CANVAS = "CANVAS"
    LMS_CATALYST = "CATALYST"
    LMS_MOODLE = "MOODLE"
    LMS_NONE = "NONE"

    PRIMARY_LMS_CHOICES = (
        (LMS_CANVAS, LMS_CANVAS),
        (LMS_CATALYST, LMS_CATALYST),
        (LMS_MOODLE, LMS_MOODLE),
        (LMS_NONE, LMS_NONE),
    )

    LMS_OWNER_CAMPUS = "CAMPUS"
    LMS_OWNER_AP = "PCE_AP"
    LMS_OWNER_IELP = "PCS_IELP"
    LMS_OWNER_OL = "PCE_OL"

    LMS_OWNER_CHOICES = (
        (LMS_OWNER_CAMPUS, LMS_OWNER_CAMPUS),
        (LMS_OWNER_AP, LMS_OWNER_AP),
        (LMS_OWNER_IELP, LMS_OWNER_IELP),
        (LMS_OWNER_OL, LMS_OWNER_OL),
    )

    DELETE_FLAG_ACTIVE = 'active'
    DELETE_FLAG_SUSPENDED = 'suspended'
    DELETE_FLAG_WITHDRAWN = 'withdrawn'

    DELETE_FLAG_CHOICES = (
        (DELETE_FLAG_ACTIVE, DELETE_FLAG_ACTIVE),
        (DELETE_FLAG_SUSPENDED, DELETE_FLAG_SUSPENDED),
        (DELETE_FLAG_WITHDRAWN, DELETE_FLAG_WITHDRAWN),
    )

    term = models.ForeignKey(Term,
                             on_delete=models.PROTECT)
    final_exam = models.ForeignKey(FinalExam,
                                   on_delete=models.PROTECT,
                                   null=True)

    curriculum_abbr = models.CharField(max_length=6,
                                       db_index=True)
    course_number = models.PositiveSmallIntegerField(db_index=True)
    section_id = models.CharField(max_length=2,
                                  db_index=True)
    course_title = models.CharField(max_length=20)
    course_title_long = models.CharField(max_length=50)
    course_campus = models.CharField(max_length=7)
    credit_control = models.CharField(max_length=32, null=True)
    section_type = models.CharField(max_length=30, null=True)
    is_independent_study = models.BooleanField(default=False)
    independent_study_instructor_regid = models.CharField(max_length=32,
                                                          null=True)
    institute_name = models.CharField(max_length=200, null=True)
    metadata = models.CharField(max_length=100, null=True)
    class_website_url = models.URLField(max_length=255,
                                        blank=True)
    sln = models.PositiveIntegerField(default=0)
    eos_cid = models.CharField(max_length=10, null=True, default=None)
    summer_term = models.CharField(max_length=12, default="")
    delete_flag = models.CharField(max_length=20, choices=DELETE_FLAG_CHOICES)
    primary_lms = models.CharField(max_length=12, choices=PRIMARY_LMS_CHOICES,
                                   null=True)
    lms_ownership = models.CharField(max_length=12, choices=LMS_OWNER_CHOICES)
    current_enrollment = models.IntegerField()
    limit_estimate_enrollment = models.IntegerField()
    limit_estimate_enrollment_indicator = models.CharField(max_length=20)
    auditors = models.IntegerField()

    # EOS is the only system that have IsIndependentStart set to true.
    # Not all PCE courses will have IsIndependentStart set to true.
    is_independent_start = models.BooleanField(default=False)

    # EOS courses may have specific start/end dates
    # indicating when the course is offered
    start_date = models.DateField(null=True, default=None)
    end_date = models.DateField(null=True, default=None)

    primary_section_href = models.CharField(
                                            max_length=200,
                                            null=True,
                                            blank=True,
                                            )
    primary_section_curriculum_abbr = models.CharField(
                                                        max_length=6,
                                                        null=True,
                                                        blank=True,
                                                        )
    primary_section_course_number = models.PositiveSmallIntegerField(
                                                            null=True,
                                                            blank=True,
                                                            )
    primary_section_id = models.CharField(max_length=2, null=True, blank=True)
    is_primary_section = models.BooleanField(default=False)
    allows_secondary_grading = models.BooleanField(default=False)
    is_auditor = models.BooleanField(default=False)
    student_credits = models.DecimalField(max_digits=3, decimal_places=1)
    student_grade = models.CharField(max_length=6, null=True, blank=True)
    grade_date = models.DateField(null=True, blank=True, default=None)
    grading_system = models.CharField(max_length=32, null=True, blank=True)
    course_description = models.TextField()
    is_remote = models.BooleanField(default=False)

    def is_campus_seattle(self):
        return (self.course_campus is not None and
                self.course_campus.lower() == 'seattle')

    def is_campus_bothell(self):
        return (self.course_campus is not None and
                self.course_campus.lower() == 'bothell')

    def is_campus_tacoma(self):
        return (self.course_campus is not None and
                self.course_campus.lower() == 'tacoma')

    def is_campus_pce(self):
        return (self.course_campus is not None and
                self.course_campus.lower() == 'pce')

    def is_inst_pce(self):
        return self.institute_name == Section.INSTITUTE_NAME_PCE

    def is_early_fall_start(self):
        return self.institute_name == Section.EARLY_FALL_START

    def is_active(self):
        return self.delete_flag == Section.DELETE_FLAG_ACTIVE

    def is_suspended(self):
        return self.delete_flag == Section.DELETE_FLAG_SUSPENDED

    def is_withdrawn(self):
        return self.delete_flag == Section.DELETE_FLAG_WITHDRAWN

    def is_source_sdb(self):
        return "SectionSourceKey=SDB;" in self.metadata

    def is_source_sdb_eos(self):
        return "SectionSourceKey=SDB_EOS;" in self.metadata

    def is_source_eos(self):
        return "SectionSourceKey=EOS;" in self.metadata

    def section_label(self):
        return SWS_SECTION_LABEL.format(
            year=self.term.year, quarter=self.term.quarter,
            curr_abbr=self.curriculum_abbr, course_num=self.course_number,
            section_id=self.section_id)

    def primary_section_label(self):
        return SWS_SECTION_LABEL.format(
            year=self.term.year, quarter=self.term.quarter,
            curr_abbr=self.primary_section_curriculum_abbr,
            course_num=self.primary_section_course_number,
            section_id=self.primary_section_id)

    def get_instructors(self):
        instructors = {}
        for meeting in self.meetings:
            for instructor in meeting.instructors:
                instructors[instructor.uwregid] = instructor
        return list(instructors.values())

    def is_instructor(self, person):
        for meeting in self.meetings:
            if person in meeting.instructors:
                return True
        return False

    def is_grade_submission_delegate(self, person):
        for delegate in self.grade_submission_delegates:
            if person == delegate.person:
                return True
        return False

    def is_grading_period_open(self, cmp_dt=None):
        if cmp_dt is None:
            cmp_dt = sws_now()

        if self.is_summer_a_term():
            open_date = self.term.aterm_grading_period_open
        else:
            open_date = self.term.grading_period_open

        try:
            return (open_date <= cmp_dt <= self.term.grade_submission_deadline)
        except TypeError:  # Undefined term dates
            return False

    def canvas_course_sis_id(self):
        if self.is_primary_section:
            if self.is_ind_study():
                if self.independent_study_instructor_regid is None:
                    raise InvalidCanvasIndependentStudyCourse((
                        "Undefined instructor for independent study "
                        "section: {}").format(self.section_label()))
                sis_id = CANVAS_IND_STUDY_COURSE_ID.format(
                    year=self.term.year, quarter=self.term.quarter,
                    curr_abbr=self.curriculum_abbr.upper(),
                    course_num=self.course_number,
                    section_id=self.section_id.upper(),
                    inst_regid=self.independent_study_instructor_regid)
            else:
                sis_id = CANVAS_COURSE_ID.format(
                    year=self.term.year, quarter=self.term.quarter,
                    curr_abbr=self.curriculum_abbr.upper(),
                    course_num=self.course_number,
                    section_id=self.section_id.upper())
        else:
            sis_id = CANVAS_COURSE_ID.format(
                year=self.term.year, quarter=self.term.quarter,
                curr_abbr=self.primary_section_curriculum_abbr.upper(),
                course_num=self.primary_section_course_number,
                section_id=self.primary_section_id.upper())

        return sis_id

    def canvas_section_sis_id(self):
        if self.is_primary_section:
            sis_id = self.canvas_course_sis_id()

            if not self.is_ind_study() and len(self.linked_section_urls):
                raise InvalidCanvasSection(sis_id)

            sis_id += "--"
        else:
            sis_id = CANVAS_COURSE_ID.format(
                year=self.term.year, quarter=self.term.quarter,
                curr_abbr=self.curriculum_abbr.upper(),
                course_num=self.course_number,
                section_id=self.section_id.upper())

        return sis_id

    def for_credit(self):
        return self.credit_control is not None

    def is_summer_a_term(self):
        return self.summer_term.lower() == self.SUMMER_A_TERM

    def is_summer_b_term(self):
        return self.summer_term.lower() == self.SUMMER_B_TERM

    def is_half_summer_term(self):
        return self.is_summer_a_term() or self.is_summer_b_term()

    def is_full_summer_term(self):
        return self.summer_term.lower() == self.SUMMER_FULL_TERM

    def is_same_summer_term(self, summer_term):
        return (summer_term is not None and
                self.summer_term.lower() == summer_term.lower() or
                summer_term is None and len(self.summer_term) == 0)

    def is_clerkship(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "clerkship" or
             self.section_type.lower() == "ck")

    def is_clinic(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "clinic" or
             self.section_type.lower() == "cl")

    def is_conference(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "conference" or
             self.section_type.lower() == "co")

    def is_lab(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "laboratory" or
             self.section_type.lower() == "lb")

    def is_lecture(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "lecture" or
             self.section_type.lower() == "lc")

    def is_ind_study(self):
        return self.is_independent_study

    def is_practicum(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "practicum" or
             self.section_type.lower() == "pr")

    def is_quiz(self):
        return self.section_type is not None and\
            (self.section_type == "quiz" or
             self.section_type.lower() == "qz")

    def is_seminar(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "seminar" or
             self.section_type.lower() == "sm")

    def is_studio(self):
        return self.section_type is not None and\
            (self.section_type.lower() == "studio" or
             self.section_type.lower() == "st")

    def json_data(self):
        data = {
            'curriculum_abbr': self.curriculum_abbr,
            'course_number': self.course_number,
            'section_id': self.section_id,
            'eos_cid': self.eos_cid,
            'is_primary_section': self.is_primary_section,
            'is_independent_study': self.is_ind_study(),
            'section_type': self.section_type,
            'independent_study_instructor_regid':
                self.independent_study_instructor_regid,
            'course_title': self.course_title,
            'course_campus': self.course_campus,
            'course_description': self.course_description,
            'class_website_url': self.class_website_url,
            'sln': self.sln,
            'summer_term': self.summer_term,
            'start_date': date_to_str(self.start_date),
            'end_date': date_to_str(self.end_date),
            'current_enrollment': self.current_enrollment,
            'limit_estimate_enrollment': self.limit_estimate_enrollment,
            'limit_estimate_enrollment_indicator':
                self.limit_estimate_enrollment_indicator,
            'auditors': self.auditors,
            'meetings': [],
            'for_credit': self.for_credit(),
            'credits': str(self.student_credits),
            'is_auditor':  self.is_auditor,
            'grade': self.student_grade,
            'grade_date': date_to_str(self.grade_date),
            'grading_system': self.grading_system,
            'is_remote': self.is_remote
        }

        if self.final_exam is not None:
            data["final_exam"] = self.final_exam.json_data()

        for meeting in self.meetings:
            data["meetings"].append(meeting.json_data())

        return data

    def __str__(self):
        return json.dumps(self.json_data())


class SectionReference(models.Model):
    term = models.ForeignKey(Term,
                             on_delete=models.PROTECT)
    curriculum_abbr = models.CharField(max_length=6)
    course_number = models.PositiveSmallIntegerField()
    section_id = models.CharField(max_length=2)
    url = models.URLField(max_length=255,
                          blank=True)

    def __eq__(self, other):
        return (other is not None and
                type(self) == type(other) and
                self.section_label() == other.section_label())

    def section_label(self):
        return SWS_SECTION_LABEL.format(
            year=self.term.year, quarter=self.term.quarter,
            curr_abbr=self.curriculum_abbr,
            course_num=self.course_number,
            section_id=self.section_id)

    def json_data(self):
        return {'year': self.term.year,
                'quarter': self.term.quarter,
                'curriculum_abbr': self.curriculum_abbr,
                'course_number': self.course_number,
                'section_id': self.section_id,
                'url': self.url,
                'section_label': self.section_label()}

    def __str__(self):
        return json.dumps(self.json_data())


class SectionStatus(models.Model):
    add_code_required = models.NullBooleanField(default=False)
    current_enrollment = models.IntegerField()
    current_registration_period = models.IntegerField()
    faculty_code_required = models.NullBooleanField(default=False)
    limit_estimated_enrollment = models.IntegerField()
    limit_estimate_enrollment_indicator = models.CharField(max_length=8)
    room_capacity = models.IntegerField()
    sln = models.PositiveIntegerField()
    space_available = models.IntegerField()
    is_open = models.CharField(max_length=6)

    def json_data(self):
        data = {
            'add_code_required': self.add_code_required,
            'current_enrollment': self.current_enrollment,
            'current_registration_period': self.current_registration_period,
            'faculty_code_required': self.faculty_code_required,
            'limit_estimated_enrollment': self.limit_estimated_enrollment,
            'limit_estimate_enrollment_indicator':
                self.limit_estimate_enrollment_indicator,
            'room_capacity': self.room_capacity,
            'sln': self.sln,
            'space_available': self.space_available,
            'is_open': self.status,
        }
        return data

    def __str__(self):
        return json.dumps(self.json_data())


WITHDREW_GRADE_PATTERN = re.compile(r'^W')


class Registration(models.Model):
    credits = models.CharField(max_length=5)
    duplicate_code = models.CharField(max_length=3)
    grade = models.CharField(max_length=5, blank=True)
    grade_date = models.DateField(blank=True, null=True, default=None)
    feebase_type = models.CharField(max_length=64, blank=True)
    is_active = models.NullBooleanField()
    is_auditor = models.NullBooleanField()
    is_credit = models.NullBooleanField()

    # The IsIndependentStart should match with the value in the section
    is_independent_start = models.NullBooleanField()
    meta_data = models.CharField(max_length=96, blank=True, null=True)

    # The StartDate and EndDate indicate when the student's actual enrollment
    # is. And they should be contained within the section start
    # and end dates
    start_date = models.DateField(null=True, default=None)
    end_date = models.DateField(null=True, default=None)
    repeat_course = models.NullBooleanField()
    repository_timestamp = models.DateTimeField()
    request_date = models.DateField(blank=True, null=True, default=None)
    request_status = models.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        self.section = None  # either Section or SectionReference
        self.person = None
        reg_json = kwargs.get("data")
        if reg_json is None:
            return super(Registration, self).__init__(*args, **kwargs)

        self.credits = reg_json["Credits"].strip()
        self.duplicate_code = reg_json.get("DuplicateCode")
        self.feebase_type = reg_json.get("FeeBaseType")
        self.grade = reg_json.get("Grade")
        self.is_active = reg_json.get("IsActive")
        self.is_auditor = reg_json.get("Auditor")
        self.is_credit = reg_json.get("IsCredit")
        self.is_independent_start = reg_json.get("IsIndependentStart")
        self.meta_data = reg_json.get("Metadata")
        self.request_status = reg_json.get("RequestStatus")
        self.repeat_course = reg_json.get("RepeatCourse")
        self.grade_date = str_to_date(reg_json.get("GradeDate"))
        self.start_date = str_to_date(reg_json.get("StartDate"))
        self.end_date = str_to_date(reg_json.get("EndDate"))
        self.request_date = str_to_date(reg_json.get("RequestDate"))
        self.repository_timestamp = str_to_datetime(
            reg_json.get("RepositoryTimeStamp"))

    def eos_only(self):
        return (self.meta_data is not None and
                "RegistrationSourceLocation=EOS;" in self.meta_data)

    def is_fee_based(self):
        return self.feebase_type.lower() == "fee based course"

    def is_dropped_status(self):
        return (len(self.request_status) and
                self.request_status.lower() == "dropped from class")

    def is_pending_status(self):
        return (len(self.request_status) and
                self.request_status.lower() == "pending added to class")

    def is_standby_status(self):
        return (len(self.request_status) and
                self.request_status.lower() == "added to standby")

    def is_withdrew(self):
        return (WITHDREW_GRADE_PATTERN.match(self.grade) is not None)

    def json_data(self):
        return {
            'credits': self.credits,
            'duplicate_code': self.duplicate_code,
            'grade': self.grade,
            'grade_date': date_to_str(self.grade_date),
            'feebase_type': self.feebase_type,
            'is_active': self.is_active,
            'is_auditor': self.is_auditor,
            'is_credit': self.is_credit,
            'is_independent_start': self.is_independent_start,
            'meta_data': self.meta_data,
            'end_date': date_to_str(self.end_date),
            'start_date': date_to_str(self.start_date),
            'repeat_course': self.repeat_course,
            'repository_timestamp': date_to_str(self.repository_timestamp),
            'request_date': date_to_str(self.request_date),
            'request_status': self.request_status,
            'is_dropped': self.is_dropped_status(),
            'is_pending': self.is_pending_status(),
            'is_standby': self.is_standby_status(),
            'is_withdrew': self.is_withdrew(),
            'is_eos_only': self.eos_only()}

    def __str__(self):
        return json.dumps(self.json_data())


class SectionMeeting(models.Model):
    NON_MEETING = "NON"
    term = models.ForeignKey(Term,
                             on_delete=models.PROTECT)
    section = models.ForeignKey(Section,
                                on_delete=models.PROTECT)
    meeting_index = models.PositiveSmallIntegerField()
    meeting_type = models.CharField(max_length=20)
    building_to_be_arranged = models.NullBooleanField()
    building = models.CharField(max_length=5)
    room_to_be_arranged = models.NullBooleanField()
    room_number = models.CharField(max_length=5)
    days_to_be_arranged = models.NullBooleanField()
    eos_start_date = models.DateField(null=True, default=None)
    eos_end_date = models.DateField(null=True, default=None)
    start_time = models.TimeField(null=True, default=None)
    end_time = models.TimeField(null=True, default=None)

    meets_monday = models.NullBooleanField()
    meets_tuesday = models.NullBooleanField()
    meets_wednesday = models.NullBooleanField()
    meets_thursday = models.NullBooleanField()
    meets_friday = models.NullBooleanField()
    meets_saturday = models.NullBooleanField()
    meets_sunday = models.NullBooleanField()
    # instructor = models.ForeignKey(Instructor, on_delete=models.PROTECT)

    def wont_meet(self):
        return self.meeting_type == SectionMeeting.NON_MEETING

    def no_meeting(self):
        return not(self.meets_monday or
                   self.meets_tuesday or
                   self.meets_wednesday or
                   self.meets_thursday or
                   self.meets_friday or
                   self.meets_saturday or
                   self.meets_sunday)

    def json_data(self):
        data = {
            'index': self.meeting_index,
            'type': self.meeting_type,
            'days_tbd': self.days_to_be_arranged,
            'eos_start_date': self.eos_start_date,
            'eos_end_date': self.eos_end_date,
            'meeting_days': {
                'monday': self.meets_monday,
                'tuesday': self.meets_tuesday,
                'wednesday': self.meets_wednesday,
                'thursday': self.meets_thursday,
                'friday': self.meets_friday,
                'saturday': self.meets_saturday,
                'sunday': self.meets_sunday,
            },
            'wont_meet': self.wont_meet(),
            'no_meeting': self.no_meeting(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'building_tbd': self.building_to_be_arranged,
            'building': self.building,
            'room_tbd': self.room_to_be_arranged,
            'room': self.room_number,
            'room_number': self.room_number,
            'instructors': [],
        }

        for instructor in self.instructors:
            data["instructors"].append(instructor.json_data())

        return data

    def __str__(self):
        return json.dumps(self.json_data())


class StudentGrades(models.Model):
    user = models.ForeignKey(Person)
    term = models.ForeignKey(Term)

    grade_points = models.DecimalField(max_digits=5, decimal_places=2)
    credits_attempted = models.DecimalField(max_digits=3, decimal_places=1)
    non_grade_credits = models.DecimalField(max_digits=3, decimal_places=1)


class StudentCourseGrade(models.Model):
    grade = models.CharField(max_length=10)
    credits = models.DecimalField(max_digits=3, decimal_places=1)
    section = models.ForeignKey(Section,
                                on_delete=models.PROTECT)


class ClassSchedule(models.Model):
    user = models.ForeignKey(Person)
    term = models.ForeignKey(Term,
                             on_delete=models.PROTECT)
    registered_summer_terms = {}

    def json_data(self):
        data = {
            'year': self.term.year,
            'quarter': self.term.quarter,
            'term': self.term.json_data(),
            'sections': [],
            'registered_summer_terms': self.registered_summer_terms
        }

        for section in self.sections:
            data["sections"].append(section.json_data())
        return data


class Campus(models.Model):
    label = models.SlugField(max_length=15, unique=True)
    name = models.CharField(max_length=20)
    full_name = models.CharField(max_length=60)


class College(models.Model):
    campus_label = models.SlugField(max_length=15)
    label = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=60)
    full_name = models.CharField(max_length=60)


class Department(models.Model):
    college_label = models.CharField(max_length=15)
    label = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=60)
    full_name = models.CharField(max_length=60)


class Curriculum(models.Model):
    label = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=60)
    full_name = models.CharField(max_length=60)


class GradeSubmissionDelegate(models.Model):
    person = models.ForeignKey(Person,
                               on_delete=models.PROTECT)
    delegate_level = models.CharField(max_length=20)


class NoticeAttribute(models.Model):
    name = models.CharField(max_length=100)
    data_type = models.CharField(max_length=100)

    _url_value = models.URLField(blank=True)
    _string_value = models.CharField(max_length=100, blank=True)
    _date_value = models.DateField(blank=True)

    def get_value(self):
        if self.data_type == "date":
            return date_to_str(self._date_value)
        if self.data_type == "string":
            return self._string_value
        if self.data_type == "url":
            return self._url_value

    def get_formatted_date_value(self):
        if self._date_value:
            return abbr_week_month_day_str(self._date_value)
        return None


class Notice(models.Model):
    notice_category = models.CharField(max_length=100)
    notice_content = models.TextField()
    notice_type = models.CharField(max_length=100)
    custom_category = models.CharField(max_length=100,
                                       default="Uncategorized"
                                       )
    # long_notice: if it is a short notice, this attribute
    # will point to the corresponding long notice

    def json_data(self, include_abbr_week_month_day_format=False):

        attrib_data = []

        for attrib in self.attributes:
            if (attrib.data_type == "date" and
                    include_abbr_week_month_day_format):
                attrib_data.append(
                    {'name': attrib.name,
                     'data_type': attrib.data_type,
                     'value': attrib.get_value(),
                     'formatted_value': attrib.get_formatted_date_value()
                     })
            else:
                attrib_data.append(
                    {'name': attrib.name,
                     'data_type': attrib.data_type,
                     'value': attrib.get_value()
                     })

        data = {
            'notice_content': self.notice_content,
            'attributes': attrib_data
        }
        return data

    def __str__(self):
        return json.dumps(self.json_data())


class Finance(models.Model):
    tuition_accbalance = models.FloatField()
    pce_accbalance = models.FloatField()

    def json_data(self):
        return {'tuition_accbalance': self.tuition_accbalance,
                'pce_accbalance': self.pce_accbalance
                }

    def __str__(self):
        return json.dumps(self.json_data())


class Enrollment(models.Model):
    CLASS_LEVEL_NON_MATRIC = "non_matric"
    is_honors = models.NullBooleanField()
    class_level = models.CharField(max_length=100)
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    is_enroll_src_pce = models.NullBooleanField()
    is_registered = models.NullBooleanField()
    has_pending_major_change = models.NullBooleanField()
    # will have a list of Registrations if verbose is true

    def is_non_matric(self):
        return self.class_level.lower() == Enrollment.CLASS_LEVEL_NON_MATRIC

    def has_unfinished_pce_course(self):
        try:
            return (self.unf_pce_courses and
                    len(self.unf_pce_courses) > 0)
        except AttributeError:
            return False


class Major(models.Model):
    degree_abbr = models.CharField(max_length=50)
    college_abbr = models.CharField(max_length=50)
    college_full_name = models.CharField(max_length=100)
    degree_name = models.CharField(max_length=100)
    degree_level = models.IntegerField()
    full_name = models.CharField(max_length=100)
    major_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    campus = models.CharField(max_length=8)

    def __eq__(self, other):
        return (other is not None and
                type(self) == type(other) and
                self.__key() == other.__key())

    def __key(self):
        return (self.campus, self.college_abbr, self.major_name)

    def __hash__(self):
        return hash(self.__key())

    def json_data(self):
        return {'degree_abbr': self.degree_abbr,
                'college_abbr': self.college_abbr,
                'college_full_name': self.college_abbr,
                'degree_level': self.degree_level,
                'degree_name': self.degree_name,
                'campus': self.campus,
                'name': self.major_name,
                'full_name': self.full_name,
                'short_name': self.short_name
                }

    def __str__(self):
        return json.dumps(self.json_data())


class Minor(models.Model):
    abbr = models.CharField(max_length=50)
    campus = models.CharField(max_length=8)
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)

    def __eq__(self, other):
        return (other is not None and
                type(self) == type(other) and
                self.__key() == other.__key())

    def __key(self):
        return (self.campus, self.full_name)

    def __hash__(self):
        return hash(self.__key())

    def json_data(self):
        return {'abbr': self.abbr,
                'campus': self.campus,
                'name': self.name,
                'full_name': self.full_name,
                'short_name': self.short_name
                }

    def __str__(self):
        return json.dumps(self.json_data())


class Course(models.Model):
    curriculum_abbr = models.CharField(max_length=6,
                                       db_index=True)
    course_number = models.PositiveSmallIntegerField(db_index=True)
    course_title = models.CharField(max_length=20)
    course_title_long = models.CharField(max_length=50)
    course_campus = models.CharField(max_length=7)
    course_description = models.TextField()

    def json_data(self):
        data = {
            'curriculum_abbr': self.curriculum_abbr,
            'course_number': self.course_number,
            'course_title': self.course_title,
            'course_title_long': self.course_title_long,
            'course_campus': self.course_campus,
            'course_description': self.course_description
        }
        return data

    def __str__(self):
        return json.dumps(self.json_data())
