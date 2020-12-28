from datetime import datetime, timedelta
from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.models import Term, Curriculum, Person
from restclients_core.exceptions import DataFailureException
from uw_sws.exceptions import (InvalidSectionID, InvalidSectionURL,
                               InvalidCanvasIndependentStudyCourse,
                               InvalidCanvasSection)
from uw_sws import use_v5_resources
from uw_sws.section import (
    get_section_by_label, get_joint_sections, get_linked_sections,
    get_sections_by_instructor_and_term, get_sections_by_curriculum_and_term,
    get_sections_by_building_and_term, get_changed_sections_by_term,
    get_last_section_by_instructor_and_terms, validate_section_label,
    get_sections_by_delegate_and_term, is_a_term, is_b_term,
    is_full_summer_term, is_valid_sln, is_remote)


@fdao_pws_override
@fdao_sws_override
class SWSTestSectionData(TestCase):
    def test_section(self):
        section = get_section_by_label('2012,autumn,B BIO,180/A')
        self.assertTrue(section.is_campus_bothell())
        self.assertTrue(section.is_lecture())
        section = get_section_by_label('2013,summer,MATH,125/G')
        self.assertTrue(section.is_campus_seattle())
        self.assertTrue(section.is_lecture())
        section = get_section_by_label('2013,autumn,T BUS,310/A')
        self.assertTrue(section.is_campus_tacoma())
        self.assertFalse(section.is_lab())
        section = get_section_by_label('2013,winter,RES D,630/A')
        self.assertTrue(section.is_clinic())
        section = get_section_by_label('2013,spring,BIGDATA,230/A')
        self.assertFalse(section.is_ind_study())
        self.assertEqual(str(section.meetings[0].eos_start_date),
                         '2013-04-02')
        self.assertEqual(str(section.meetings[0].eos_end_date),
                         '2013-06-04')
        self.assertTrue(section.is_source_eos())

        section = get_section_by_label('2013,summer,PHIL,495/A')
        self.assertTrue(section.is_ind_study())
        section = get_section_by_label('2013,summer,PHYS,121/AK')
        self.assertTrue(section.is_quiz())
        section = get_section_by_label('2013,summer,PHYS,121/AQ')
        self.assertTrue(section.is_lab())
        self.assertIsNotNone(section.json_data())

    def test_non_credit_certificate_couse_section(self):
        section = get_section_by_label('2013,winter,BIGDATA,220/A')
        self.assertTrue(section.is_campus_pce())
        self.assertEquals(str(section.start_date), "2013-01-09")
        self.assertEquals(str(section.end_date), "2013-03-27")
        self.assertEquals(section.metadata, "SectionSourceKey=EOS;")
        self.assertEquals(section.is_active(), False)
        self.assertEquals(section.is_withdrawn(), False)
        self.assertEquals(section.is_suspended(), True)

        section = get_section_by_label('2013,spring,BIGDATA,230/A')
        self.assertTrue(section.is_campus_pce())
        self.assertEquals(str(section.start_date), "2013-04-03")
        self.assertEquals(str(section.end_date), "2013-06-12")
        self.assertIsNotNone(section.json_data())
        self.assertEquals(section.is_active(), True)
        self.assertEquals(section.is_withdrawn(), False)
        self.assertEquals(section.is_suspended(), False)

    def test_final_exams(self):
        section = get_section_by_label('2013,summer,B BIO,180/A')
        self.assertEquals(section.final_exam, None,
                          "No final exam for B BIO 180")

        section = get_section_by_label('2013,summer,MATH,125/G')
        final_exam = section.final_exam

        self.assertEquals(final_exam.is_confirmed, False,
                          "Final exam for Math 125 isn't confirmed")
        self.assertEquals(final_exam.no_exam_or_nontraditional, False,
                          "Final exam for Math 125 isn't non-traditional")
        section = get_section_by_label('2013,summer,TRAIN,101/A')
        final_exam = section.final_exam

        self.assertEquals(final_exam.is_confirmed, True,
                          "Final exam for Train 101 is confirmed")
        self.assertEquals(final_exam.no_exam_or_nontraditional, False,
                          "Final exam for Train 101 isn't non-traditional")
        self.assertEquals(final_exam.building, "KNE",
                          "Has right final building")
        self.assertEquals(final_exam.room_number, "012",
                          "Has right room #")

        start = final_exam.start_date
        end = final_exam.end_date

        self.assertEquals(start.year, 2013)
        self.assertEquals(start.month, 6)
        self.assertEquals(start.day, 2)
        self.assertEquals(start.hour, 13)
        self.assertEquals(start.minute, 30)

        self.assertEquals(end.year, 2013)
        self.assertEquals(end.month, 6)
        self.assertEquals(end.day, 2)
        self.assertEquals(end.hour, 16)
        self.assertEquals(end.minute, 20)

        section = get_section_by_label('2013,spring,MATH,125/H')
        final_exam = section.final_exam

        self.assertEquals(final_exam.end_date, None,
                          "Bad final exam time for MATH 125 H")

    def test_is_valid_sln(self):
        self.assertFalse(is_valid_sln(None))
        self.assertFalse(is_valid_sln(''))
        self.assertFalse(is_valid_sln('0000'))
        self.assertFalse(is_valid_sln('1000'))
        self.assertFalse(is_valid_sln('00000'))
        self.assertFalse(is_valid_sln('100000'))
        self.assertTrue(is_valid_sln('10000'))

    def test_validate_section_label(self):
        # Valid data, shouldn't throw any exceptions
        validate_section_label('2013,summer,TRAIN,100/A')

        # Invalid data, should throw exceptions
        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          None)

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          ' ')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '2012')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '2012,summer')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '2012,summer,TRAIN')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '2012, summer, TRAIN, 100')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          'summer, TRAIN, 100/A')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '2012,fall,TRAIN,100/A')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '-2012,summer,TRAIN,100/A')

        self.assertRaises(InvalidSectionID,
                          validate_section_label,
                          '0000,summer,TRAIN,100/A')

    def test_get_section_by_label(self):
        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '9999,summer,TRAIN,100/A')

        # Valid section labels, no files for them
        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2012,summer,TRAIN,110/A')

        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2012,summer,TRAIN,100/B')

        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2012,summer,PHYS,121/B')

        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2012,summer,PHYS,121/BB')

        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2010,autumn,G H,201/A')

        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2010,autumn,CS&SS,221/A')

        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2010,autumn,KOREAN,101/A')

        self.assertRaises(DataFailureException,
                          get_section_by_label,
                          '2010,autumn,CM,101/A')

    def test_instructors_in_section(self):
        section = get_section_by_label('2013,winter,ASIAN,203/A')

        self.assertEquals(len(section.get_instructors()), 1,
                          "Correct number of instructors")

        person1 = Person(uwregid="FBB38FE46A7C11D5A4AE0004AC494FFE")
        self.assertEquals(section.is_instructor(person1), False,
                          "Person is not instructor")

        person2 = Person(uwregid="6DF0A9206A7D11D5A4AE0004AC494FFE")
        self.assertEquals(section.is_instructor(person2), True,
                          "Person is instructor")

        section2 = get_section_by_label('2013,summer,TRAIN,101/A')
        self.assertEquals(len(section2.get_instructors()), 2,
                          "Correct number of instructors")

        section3 = get_section_by_label('2013,spring,PHYS,121/A')
        self.assertEquals(len(section3.get_instructors()), 2,
                          "Course with duplicate instructors")

        section3 = get_section_by_label('2013,spring,PHYS,121/A', False)
        self.assertEquals(len(section3.get_instructors()), 1,
                          "Correct number of TSPrinted instructors")

    def test_delegates_in_section(self):
        section = get_section_by_label('2013,winter,ASIAN,203/A')

        self.assertEquals(
            len(section.grade_submission_delegates), 3,
            "Correct number of delegates")

        person1 = Person(uwregid="6DF0A9206A7D11D5A4AE0004AC494FFE")
        self.assertEquals(section.is_grade_submission_delegate(person1),
                          False, "Person is not delegate")

        person2 = Person(uwregid="FBB38FE46A7C11D5A4AE0004AC494FFE")
        self.assertEquals(section.is_grade_submission_delegate(person2),
                          True, "Person is delegate")

    def test_joint_sections(self):
        section = get_section_by_label('2013,winter,ASIAN,203/A')
        joint_sections = get_joint_sections(section)

        self.assertEquals(len(joint_sections), 1)

        section = get_section_by_label('2013,winter,EMBA,503/A')
        joint_sections = get_joint_sections(section)

        self.assertEquals(len(joint_sections), 0)

    # Failing because linked section json files haven't been made
    # (Train 100 AA/AB)
    def test_linked_sections(self):
        # Valid data, shouldn't throw any exceptions
        section = get_section_by_label('2013,summer,TRAIN,100/A')
        get_linked_sections(section)

        # Invalid data, should throw exceptions
        section.linked_section_urls = ['']
        self.assertRaises(InvalidSectionURL,
                          get_linked_sections, section)

        section.linked_section_urls = [' ']
        self.assertRaises(InvalidSectionURL,
                          get_linked_sections, section)

        section.linked_section_urls = ['2012,summer,TRAIN,100/A']
        self.assertRaises(InvalidSectionURL,
                          get_linked_sections, section)

        if use_v5_resources():
            section.linked_section_urls = \
                ['/student/v5/course/2012,summer,PHYS,121/B.json']
        else:
            section.linked_section_urls = \
                ['/student/v4/course/2012,summer,PHYS,121/B.json']
        self.assertRaises(DataFailureException,
                          get_linked_sections, section)

        if use_v5_resources():
            section.linked_section_urls = \
                ['/student/v5/course/2010,autumn,CS&SS,221/A.json']
        else:
            section.linked_section_urls = \
                ['/student/v4/course/2010,autumn,CS&SS,221/A.json']
        self.assertRaises(DataFailureException,
                          get_linked_sections, section)

        if use_v5_resources():
            section.linked_section_urls = \
                ['/student/v5/course/2010,autumn,KOREAN,101/A.json']
        else:
            section.linked_section_urls = \
                ['/student/v4/course/2010,autumn,KOREAN,101/A.json']
        self.assertRaises(DataFailureException,
                          get_linked_sections, section)

        if use_v5_resources():
            section.linked_section_urls = \
                ['/student/v5/course/2010,autumn,G H,201/A.json']
        else:
            section.linked_section_urls = \
                ['/student/v4/course/2010,autumn,G H,201/A.json']
        self.assertRaises(DataFailureException,
                          get_linked_sections, section)

        if use_v5_resources():
            section.linked_section_urls = \
                ['/student/v5/course/2010,autumn,CM,101/A.json']
        else:
            section.linked_section_urls = \
                ['/student/v4/course/2010,autumn,CM,101/A.json']
        self.assertRaises(DataFailureException,
                          get_linked_sections, section)

        if use_v5_resources():
            section.linked_section_urls = [
                '/student/v5/course/2012,autumn,PHYS,121/A.json',
                '/student/v5/course/2012,autumn,PHYS,121/AC.json',
                '/student/v5/course/2012,autumn,PHYS,121/BT.json']
        else:
            section.linked_section_urls = [
                '/student/v4/course/2012,autumn,PHYS,121/A.json',
                '/student/v4/course/2012,autumn,PHYS,121/AC.json',
                '/student/v4/course/2012,autumn,PHYS,121/BT.json']
        self.assertRaises(DataFailureException,
                          get_linked_sections, section)

        if use_v5_resources():
            section.linked_section_urls = [
                '/student/v5/course/2012,autumn,PHYS,121/A.json',
                '/student/v5/course/2012,autumn,PHYS,121/AC.json',
                '/student/v5/course/2012,autumn,PHYS,121/AAA.json']
        else:
            section.linked_section_urls = [
                '/student/v4/course/2012,autumn,PHYS,121/A.json',
                '/student/v4/course/2012,autumn,PHYS,121/AC.json',
                '/student/v4/course/2012,autumn,PHYS,121/AAA.json']
        self.assertRaises(DataFailureException,
                          get_linked_sections, section)

    def test_sections_by_instructor_and_term(self):
        term = Term(quarter="summer", year=2013)
        instructor = Person(uwregid="FBB38FE46A7C11D5A4AE0004AC494FFE")
        sections = get_sections_by_instructor_and_term(instructor, term)
        self.assertEquals(len(sections), 1)

        # test delete_flag
        term = Term(quarter="spring", year=2013)
        sections = get_sections_by_instructor_and_term(
            instructor, term, delete_flag=['active', 'suspended'])
        self.assertEquals(len(sections), 2)

        # test different setting for transcriptable_course
        term = Term(quarter="spring", year=2013)
        instructor = Person(uwregid="260A0DEC95CB11D78BAA000629C31437")
        sections = get_sections_by_instructor_and_term(
            instructor, term, transcriptable_course="all")
        self.assertEquals(len(sections), 3)
        self.assertEquals(sections[1].curriculum_abbr, "BIGDATA")

        term = Term(quarter="autumn", year=2012)
        sections = get_sections_by_instructor_and_term(
            instructor, term, future_terms=4, include_secondaries=False,
            transcriptable_course="all")
        self.assertEquals(len(sections), 5)
        self.assertEquals(sections[0].term.year, 2013)
        self.assertEquals(sections[0].term.quarter, "spring")
        self.assertEquals(sections[-1].term.year, 2013)
        self.assertEquals(sections[-1].term.quarter, "summer")

    def test_get_last_section_by_instructor_and_terms(self):
        instructor = Person(uwregid="260A0DEC95CB11D78BAA000629C31437")
        term = Term(quarter="autumn", year=2012)
        section = get_last_section_by_instructor_and_terms(instructor, term, 4)
        self.assertEquals(section.term.year, 2013)
        self.assertEquals(section.term.quarter, "summer")

        term = Term(quarter="autumn", year=2014)
        section = get_last_section_by_instructor_and_terms(instructor, term, 2)
        self.assertIsNone(section)

    def test_sections_by_delegate_and_term(self):
        term = Term(quarter="summer", year=2013)
        delegate = Person(uwregid="FBB38FE46A7C11D5A4AE0004AC494FFE")

        sections = get_sections_by_delegate_and_term(delegate, term)
        self.assertEquals(len(sections), 2)

        # with delete_flag
        sections = get_sections_by_delegate_and_term(
            delegate, term, delete_flag=['active', 'suspended'])
        self.assertEquals(len(sections), 2)

        # test delete_flag ordering
        sections = get_sections_by_delegate_and_term(
            delegate, term, delete_flag=['suspended', 'active'])
        self.assertEquals(len(sections), 2)

        # incorrect delete_flag
        self.assertRaises(ValueError, get_sections_by_delegate_and_term,
                          delegate, term, delete_flag='active')

    def test_sections_by_curriculum_and_term(self):
        term = Term(quarter="winter", year=2013)
        curriculum = Curriculum(label="ENDO")
        sections = get_sections_by_curriculum_and_term(curriculum, term)

        self.assertEquals(len(sections), 2)

        # Valid curriculum, with no file
        self.assertRaises(DataFailureException,
                          get_sections_by_curriculum_and_term,
                          Curriculum(label="FINN"),
                          term)

    def test_sections_by_building_and_term(self):
        term = Term(quarter="winter", year=2013)
        building = "KNE"
        sections = get_sections_by_building_and_term(building, term)

        self.assertEquals(len(sections), 2)

        # Valid building, with no file
        self.assertRaises(DataFailureException,
                          get_sections_by_building_and_term,
                          "SIG",
                          term)

    def test_changed_sections_by_term(self):
        changed_date = datetime(2013, 12, 12).date()
        term = Term(quarter="winter", year=2013)
        sections = get_changed_sections_by_term(changed_date, term)

        self.assertEquals(len(sections), 2)

    def test_changed_sections_by_term_and_kwargs(self):
        changed_date = datetime(2013, 12, 12).date()
        term = Term(quarter="winter", year=2013)
        sections = get_changed_sections_by_term(
            changed_date, term, curriculum_abbreviation="ENDO",
            transcriptable_course="all")

        self.assertEquals(len(sections), 3)

    def test_instructor_published(self):
        # Published Instructors
        pi_section = get_section_by_label('2013,summer,B BIO,180/A')
        self.assertEquals(
            pi_section.meetings[0].instructors[0].TSPrint, True)

        # Unpublished Instructors
        upi_section = get_section_by_label('2013,summer,MATH,125/G')
        self.assertEquals(
            upi_section.meetings[0].instructors[0].TSPrint, False)

    def test_secondary_grading(self):
        section1 = get_section_by_label('2012,summer,PHYS,121/A')
        self.assertEquals(section1.allows_secondary_grading, True,
                          "Allows secondary grading")

        for linked in get_linked_sections(section1):
            self.assertEquals(linked.allows_secondary_grading, True,
                              "Allows secondary grading")

        section2 = get_section_by_label('2013,winter,EMBA,503/A')
        self.assertEquals(section2.allows_secondary_grading, False,
                          "Does not allow secondary grading")

    def test_grading_period_open(self):
        section = get_section_by_label('2012,summer,PHYS,121/A')

        self.assertEquals(section.is_grading_period_open(), False,
                          "Grading window is not open")

        # Using passed datetimes
        dt = datetime(2012, 8, 20, 0, 0)
        self.assertEquals(section.is_grading_period_open(dt), True,
                          "Grading window is open using passed dt")

        dt = datetime(2012, 8, 22, 0, 0)
        self.assertEquals(section.is_grading_period_open(dt), False,
                          "Grading window is not open using passed dt")

        # Spring 2013 is 'current' term
        section = get_section_by_label('2013,spring,MATH,125/G')

        self.assertEquals(section.is_grading_period_open(), True,
                          "Grading window is open")

    def test_grading_system(self):
        section = get_section_by_label('2012,summer,PHYS,121/A')

        self.assertEquals(section.grading_system, 'standard',
                          "Grading system is not standard")

    def test_canvas_sis_ids(self):
        # Primary section containing linked secondary sections
        section = get_section_by_label('2012,summer,PHYS,121/A')
        self.assertEquals(
            section.canvas_course_sis_id(),
            '2012-summer-PHYS-121-A',
            'Canvas course SIS ID')
        self.assertRaises(InvalidCanvasSection,
                          section.canvas_section_sis_id)

        # Primary section with no linked sections
        section = get_section_by_label('2013,autumn,REHAB,585/A')
        self.assertEquals(
            section.canvas_course_sis_id(),
            '2013-autumn-REHAB-585-A',
            'Canvas course SIS ID')
        self.assertEquals(
            section.canvas_section_sis_id(),
            '2013-autumn-REHAB-585-A--',
            'Canvas section SIS ID')

        # Secondary (linked) section
        section = get_section_by_label('2013,autumn,PHYS,121/AB')
        self.assertEquals(
            section.canvas_course_sis_id(),
            '2013-autumn-PHYS-121-A',
            'Canvas course SIS ID')
        self.assertEquals(
            section.canvas_section_sis_id(),
            '2013-autumn-PHYS-121-AB',
            'Canvas section SIS ID')

        # Independent study section
        section = get_section_by_label('2020,summer,PHIL,600/A')

        # ..missing instructor regid
        self.assertRaises(InvalidCanvasIndependentStudyCourse,
                          section.canvas_course_sis_id)

        section.independent_study_instructor_regid = (
            'A9D2DDFA6A7D11D5A4AE0004AC494FFE')
        self.assertEquals(
            section.canvas_course_sis_id(),
            '2020-summer-PHIL-600-A-A9D2DDFA6A7D11D5A4AE0004AC494FFE',
            'Canvas course SIS ID')
        self.assertEquals(
            section.canvas_section_sis_id(),
            '2020-summer-PHIL-600-A-A9D2DDFA6A7D11D5A4AE0004AC494FFE--',
            'Canvas section SIS ID')

    def test_summer_terms(self):
        section = get_section_by_label('2013,summer,B BIO,180/A')
        self.assertFalse(section.is_summer_a_term())
        self.assertFalse(section.is_summer_b_term())
        self.assertFalse(section.is_half_summer_term())
        self.assertTrue(section.is_full_summer_term())

        self.assertTrue(section.is_same_summer_term("full-term"))
        self.assertFalse(section.is_same_summer_term("a-term"))
        self.assertFalse(section.is_same_summer_term("B-term"))
        self.assertFalse(section.is_same_summer_term(None))

        section = get_section_by_label('2020,summer,EDIT,120/B')
        self.assertFalse(section.for_credit())
        self.assertFalse(section.is_summer_a_term())
        self.assertFalse(section.is_summer_b_term())
        self.assertTrue(section.is_full_summer_term())

    def test_summer_term_statics(self):
        self.assertTrue(is_a_term("A-term"))
        self.assertTrue(is_b_term("B-term"))
        self.assertTrue(is_full_summer_term("Full-term"))
        self.assertFalse(is_full_summer_term("A-term"))
        self.assertFalse(is_full_summer_term("B-term"))

    def test_start_end_dates(self):
        section = get_section_by_label('2013,autumn,MATH,120/ZZ')
        start = section.start_date
        end = section.end_date

        self.assertEquals(start.year, 2013)
        self.assertEquals(start.month, 8)
        self.assertEquals(start.day, 20)

        self.assertEquals(end.year, 2013)
        self.assertEquals(end.month, 9)
        self.assertEquals(end.day, 18)

    def test_pce_course_section(self):
        section = get_section_by_label('2013,autumn,MATH,120/ZZ')
        self.assertFalse(section.is_inst_pce())
        self.assertFalse(section.is_independent_start)
        self.assertIsNone(section.eos_cid)

        section = get_section_by_label('2013,winter,COM,201/A')
        self.assertTrue(section.is_inst_pce())
        self.assertTrue(section.is_independent_start)
        self.assertIsNone(section.eos_cid)
        self.assertTrue(section.is_source_sdb_eos())

        section = get_section_by_label('2018,winter,INFX,543/A')
        self.assertTrue(section.is_inst_pce())
        self.assertEquals(section.eos_cid, '116878')
        self.assertTrue(section.is_source_sdb_eos())

    def test_early_fall_start(self):
        section = get_section_by_label('2013,spring,EFS_FAILT,101/AQ')
        self.assertTrue(section.is_early_fall_start())
        self.assertEqual(str(section.end_date), '2013-09-18')
        json_data = section.json_data()
        self.assertEqual(json_data["start_date"], '2013-08-24')
        self.assertEqual(json_data["end_date"], '2013-09-18')

        section = get_section_by_label('2013,winter,COM,201/A')
        self.assertFalse(section.is_early_fall_start())
        self.assertFalse(section.end_date)

    def test_meetings(self):
        section = get_section_by_label('2013,autumn,MATH,120/ZZ')
        meeting = section.meetings[0]
        jd = section.meetings[0].json_data()
        self.assertFalse(jd['no_meeting'])
        self.assertEqual(jd['start_time'], '11:30')
        self.assertEqual(jd['end_time'], '12:20')
        self.assertEqual(jd['type'], 'lecture')

        section = get_section_by_label('2013,spring,BIGDATA,230/A')
        jd = section.meetings[0].json_data()
        self.assertEqual(jd['start_time'], '18:00')
        self.assertEqual(jd['end_time'], '21:00')
        self.assertFalse(jd['wont_meet'])

        jd = section.meetings[1].json_data()
        self.assertTrue(jd['wont_meet'])
        self.assertEqual(jd['type'], 'NON')

    def test_for_credit_course(self):
        section = get_section_by_label('2013,spring,ESS,107/A')
        self.assertFalse(section.for_credit())
        section = get_section_by_label('2013,winter,COM,201/A')
        self.assertTrue(section.for_credit())
        section = get_section_by_label('2013,spring,ELCBUS,451/A')
        self.assertTrue(section.for_credit())
        section = get_section_by_label('2013,spring,TRAIN,100/A')
        self.assertTrue(section.for_credit())

        self.assertTrue('for_credit' in section.json_data())

    def test_pce_meeting_time(self):
        section = get_section_by_label('2013,winter,JAVA,125/A')
        meetings = section.meetings
        self.assertEqual(len(meetings), 3)
        self.assertEqual(meetings[0].start_time, "18:00")
        self.assertEqual(meetings[0].end_time, "21:00")
        self.assertIsNone(meetings[1].start_time)
        self.assertIsNone(meetings[1].end_time)
        self.assertIsNone(meetings[2].start_time)
        self.assertIsNone(meetings[2].end_time)

        json_data = section.json_data()
        meetings = json_data["meetings"]
        self.assertEqual(len(meetings), 3)
        self.assertEqual(meetings[0]["start_time"], "18:00")
        self.assertEqual(meetings[0]["end_time"], "21:00")
        self.assertIsNone(meetings[1]["start_time"])
        self.assertIsNone(meetings[1]["end_time"])
        self.assertIsNone(meetings[2]["start_time"])
        self.assertIsNone(meetings[2]["end_time"])

    def test_section_instructor(self):
        section = get_section_by_label('2013,spring,ESS,107/A')
        json_data = section.json_data()
        meetings = json_data["meetings"]
        instructors = meetings[0]["instructors"]
        self.assertEqual(len(instructors), 1)
        self.assertEqual(instructors[0]["addresses"], [])
        self.assertEqual(instructors[0]["phones"], [])
        self.assertEqual(instructors[0]["voice_mails"], [])
        self.assertEqual(instructors[0]["positions"], [])
        self.assertIsNone(instructors[0]["publish_in_emp_directory"])

    def test_course_description(self):
        section = get_section_by_label('2012,autumn,CSE,100/W')
        json_data = section.json_data()
        course_description = "Introduction to programming concepts within " \
                             "social, cultural, scientific, mathematical, " \
                             "and technological context. Topics include " \
                             "programming fundamentals (control structures" \
                             ", data types and representation, operations," \
                             " functions and parameters), computer " \
                             "organization, algorithmic thinking, " \
                             "introductory software engineering concepts " \
                             "(specifications, design, testing), and social" \
                             " and professional issues (history, ethics," \
                             " applications). "
        self.assertEqual(course_description, json_data["course_description"])

    def test_section_no_pws(self):
        # Ensure no hard dependency on the PWS
        section = get_section_by_label('2012,autumn,CSE,199/W')
        person = section.grade_submission_delegates[0].person
        self.assertEqual(person.uwregid, '1230A9206A7D11D5A4AE0004AC494123')
        self.assertEqual(person.display_name, 'PWS, FOUR OH FOUR')

    def test_remote_section(self):
        section = get_section_by_label('2020,autumn,E E,233/A')
        self.assertTrue(section.is_remote)
        self.assertTrue(section.json_data()['is_remote'])
        self.assertTrue(section.is_source_sdb())

        self.assertTrue(is_remote({"Text": "OFFERED VIA REMOTE LEARNING"}))
        self.assertTrue(is_remote({"Text": "LECTURES ARE OFFERED VIA REMOTE"}))
        self.assertFalse(is_remote({"Text": "PERSON"}))
