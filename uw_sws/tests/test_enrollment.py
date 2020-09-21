from unittest import TestCase
from uw_sws.util import fdao_sws_override
from uw_pws.util import fdao_pws_override
from uw_sws.models import Term
from uw_sws.term import get_current_term, get_next_term,\
    get_term_by_year_and_quarter, get_term_after, get_term_before
from uw_sws.enrollment import get_grades_by_regid_and_term,\
    is_src_location_pce, ENROLLMENT_SOURCE_PCE, has_start_end_dates,\
    get_enrollment_by_regid_and_term, enrollment_search_by_regid,\
    get_enrollment_history_by_regid
from restclients_core.exceptions import DataFailureException


@fdao_pws_override
@fdao_sws_override
class SWSTestEnrollments(TestCase):
    def test_javerage_grades(self):
        term = get_current_term()
        grades = get_grades_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)

        self.assertEquals(grades.term.year, 2013)
        self.assertEquals(grades.term.quarter, "spring")
        self.assertEquals(grades.user.uwnetid, "javerage")
        self.assertEquals(grades.grade_points, 30)
        self.assertEquals(grades.credits_attempted, 10)
        self.assertEquals(grades.non_grade_credits, 2)

        self.assertEquals(grades.grades[0].grade, 'CR')
        self.assertEquals(grades.grades[2].grade, '3.1')
        self.assertEquals(grades.grades[2].credits, '3.0')
        self.assertEquals(grades.grades[2].section.course_number, '121')

    def test_javerage_major(self):
        term = get_current_term()
        enrollment = get_enrollment_by_regid_and_term(
            '9136CCB8F66711D5BE060004AC494FFE', term)
        self.assertEquals(enrollment.class_level, "SENIOR")
        self.assertEquals(enrollment.is_honors, False)
        self.assertEquals(len(enrollment.majors), 1)
        self.assertEquals(enrollment.majors[0].campus, "Seattle")
        self.assertEquals(
            enrollment.majors[0].degree_name,
            "BACHELOR OF SCIENCE (APPLIED & COMPUTATIONAL MATH SCIENCES)")
        self.assertEquals(enrollment.minors[0].campus, "Seattle")
        self.assertEquals(enrollment.minors[0].name, "AMERICAN SIGN LANGUAGE")
        self.assertFalse(enrollment.is_non_matric())
        self.assertFalse(enrollment.has_unfinished_pce_course())
        self.assertFalse(enrollment.is_enroll_src_pce)
        self.assertFalse(enrollment.has_pending_major_change)

    def test_is_src_location_pce(self):
        self.assertFalse(is_src_location_pce(
                {'Metadata': ''},
                ENROLLMENT_SOURCE_PCE))
        self.assertFalse(is_src_location_pce(
                {'Metadata': "EnrollmentSourceLocation=SDB;"},
                ENROLLMENT_SOURCE_PCE))
        self.assertTrue(is_src_location_pce(
                {'Metadata': "EnrollmentSourceLocation=SDB_EOS"},
                ENROLLMENT_SOURCE_PCE))
        self.assertTrue(is_src_location_pce(
                {'Metadata': "EnrollmentSourceLocation=EOS"},
                ENROLLMENT_SOURCE_PCE))

    def test_offterm_enrolled_courses(self):
        term = get_term_by_year_and_quarter(2013, 'winter')
        enrollment = get_enrollment_by_regid_and_term(
            'AABBCCDDEEFFAABBCCDDEEFFAABBCCDC', term)
        self.assertEquals(enrollment.class_level, u'NON_MATRIC')
        self.assertTrue(enrollment.is_enroll_src_pce)
        self.assertTrue(enrollment.is_non_matric())
        self.assertTrue(enrollment.is_registered)
        self.assertEqual(len(enrollment.registrations), 2)
        self.assertEqual(
            enrollment.registrations[0].section_ref.section_label(),
            "2013,winter,COM,201/A")
        self.assertEqual(
            enrollment.registrations[1].section_ref.section_label(),
            "2013,winter,PSYCH,203/A")
        self.assertTrue(enrollment.has_unfinished_pce_course())
        self.assertEqual(len(enrollment.unf_pce_courses), 2)
        self.assertTrue(
            enrollment.unf_pce_courses.get("2013,winter,COM,201/A"))
        reg1 = enrollment.unf_pce_courses["2013,winter,COM,201/A"]
        self.assertTrue(reg1.is_fee_based())
        self.assertEqual(str(reg1.end_date), '2013-04-29')
        self.assertEqual(str(reg1.start_date), '2013-01-28')
        self.assertTrue(reg1.is_credit)
        self.assertEqual(reg1.request_status, "ADDED TO CLASS")
        self.assertEqual(reg1.meta_data,
                         "RegistrationSourceLocation=SDB_EOS;")
        self.assertFalse(reg1.eos_only())
        self.assertFalse(reg1.is_standby_status())
        self.assertFalse(reg1.is_dropped_status())
        self.assertFalse(reg1.is_pending_status())
        self.assertTrue(len(reg1.json_data()) > 0)
        self.assertEqual(
            reg1.section_ref.json_data(),
            {'course_number': u'201',
             'curriculum_abbr': u'COM',
             'quarter': u'winter',
             'section_id': u'A',
             'section_label': u'2013,winter,COM,201/A',
             'url': u'/student/v5/course/2013,winter,COM,201/A.json',
             'year': 2013})

        self.assertTrue(
            enrollment.unf_pce_courses.get("2013,winter,PSYCH,203/A"))
        reg2 = enrollment.unf_pce_courses["2013,winter,PSYCH,203/A"]
        self.assertTrue(reg2.is_fee_based())
        self.assertEqual(str(reg2.end_date), '2013-06-22')
        self.assertEqual(str(reg2.start_date), '2013-01-29')
        self.assertEqual(reg2.meta_data,
                         "RegistrationSourceLocation=SDB_EOS;")
        self.assertEqual(
            reg2.section_ref.json_data(),
            {'course_number': u'203',
             'curriculum_abbr': u'PSYCH',
             'quarter': u'winter',
             'section_id': u'A',
             'section_label': u'2013,winter,PSYCH,203/A',
             'url': u'/student/v5/course/2013,winter,PSYCH,203/A.json',
             'year': 2013})

        self.assertFalse(
            enrollment.unf_pce_courses.get("2014,winter,PSYCH,203/A"))

    def test_enrollment_search(self):
        # pce course enrollments
        result_dict = enrollment_search_by_regid(
            'AABBCCDDEEFFAABBCCDDEEFFAABBCCDC')
        self.assertEqual(len(result_dict), 2)

        term = get_current_term()
        self.assertTrue(term in result_dict)
        enrollment = result_dict.get(term)
        self.assertTrue(enrollment.is_registered)
        self.assertTrue(enrollment.is_non_matric())
        self.assertEquals(enrollment.majors[0].college_abbr, "INDUG")
        self.assertEquals(enrollment.majors[0].college_full_name,
                          "INTERDISCIPLINARY UNDERGRADUATE PROGRAMS")
        self.assertEquals(enrollment.majors[0].degree_level, 0)
        self.assertEqual(len(enrollment.unf_pce_courses), 3)
        self.assertTrue(
            "2013,spring,AAES,150/A" in enrollment.unf_pce_courses)
        self.assertTrue(
            "2013,spring,ACCTG,508/A" in enrollment.unf_pce_courses)
        self.assertTrue(
            "2013,spring,CPROGRM,712/A" in enrollment.unf_pce_courses)

        section1 = enrollment.unf_pce_courses["2013,spring,ACCTG,508/A"]
        self.assertEqual(str(section1.end_date), '2013-06-19')
        self.assertEqual(str(section1.start_date), '2013-04-01')
        self.assertTrue(section1.is_credit)
        self.assertFalse(section1.is_standby_status())
        self.assertFalse(section1.is_dropped_status())

        term0 = get_term_before(term)
        self.assertTrue(term0 in result_dict)
        enrollment0 = result_dict.get(term0)
        self.assertEquals(enrollment.majors[0], enrollment0.majors[0])
        self.assertEqual(len(enrollment0.unf_pce_courses), 1)

        # regular course
        result_dict = enrollment_search_by_regid(
            '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(len(result_dict), 7)
        term = get_current_term()
        self.assertTrue(term in result_dict)
        self.assertIsNotNone(result_dict.get(term))
        enrollment = result_dict.get(term)
        self.assertEquals(enrollment.class_level, "SENIOR")
        self.assertEquals(len(enrollment.majors), 1)
        self.assertEquals(len(enrollment.minors), 1)
        enroll_major = enrollment.majors[0]
        self.assertEquals(enroll_major.college_abbr, "")
        self.assertEquals(enroll_major.college_full_name, "")
        self.assertEquals(enroll_major.degree_level, 1)
        self.assertEquals(len(enrollment.minors), 1)
        enroll_minor = enrollment.minors[0]

        term1 = get_term_by_year_and_quarter(2013, 'summer')
        self.assertTrue(term1 in result_dict)
        enroll1 = result_dict.get(term1)
        self.assertIsNotNone(enroll1)
        self.assertTrue(enroll1.has_pending_major_change)
        enroll1_major = enroll1.majors[0]
        self.assertFalse(enroll_major == enroll1_major)

        term2 = get_term_by_year_and_quarter(2014, 'winter')
        self.assertIsNone(result_dict.get(term2))

        term3 = get_term_by_year_and_quarter(2012, 'spring')
        self.assertTrue(term3 in result_dict)
        self.assertIsNotNone(result_dict.get(term3))
        enroll3 = result_dict.get(term3)
        self.assertTrue(enroll3.is_registered)
        self.assertEquals(len(enroll3.minors), 1)
        enroll3_minor = enroll3.minors[0]
        self.assertTrue(enroll3_minor != enroll_minor)

        term4 = Term(year=1996, quarter='autumn')
        self.assertTrue(term4 in result_dict)
        self.assertIsNotNone(result_dict.get(term4))

        term5 = get_term_by_year_and_quarter(2013, 'autumn')
        enroll5 = result_dict.get(term5)
        self.assertFalse(enroll5.is_registered)

        # regid of none
        result_dict = enrollment_search_by_regid(
            '00000000000000000000000000000001')
        self.assertEqual(len(result_dict), 0)

    def test_status_standby(self):
        # non-credit
        result_dict = enrollment_search_by_regid(
            'FE36CCB8F66711D5BE060004AC494F31')
        self.assertEqual(len(result_dict), 4)
        term = get_term_by_year_and_quarter(2013, 'summer')
        enroll = result_dict.get(term)
        self.assertTrue(enroll.has_unfinished_pce_course())
        self.assertEqual(len(enroll.unf_pce_courses), 1)
        registartion = enroll.unf_pce_courses.get("2013,summer,LIS,498/C")
        self.assertTrue(registartion.eos_only())
        self.assertTrue(registartion.is_standby_status())
        self.assertFalse(registartion.is_dropped_status())
        self.assertFalse(registartion.is_pending_status())

        term1 = get_term_by_year_and_quarter(2013, 'autumn')
        self.assertTrue(term in result_dict)
        enroll1 = result_dict.get(term1)
        self.assertTrue(enroll1.has_unfinished_pce_course())
        self.assertEqual(len(enroll1.unf_pce_courses), 1)
        registartion1 = enroll1.unf_pce_courses.get("2013,autumn,MUSEUM,700/A")
        self.assertTrue(registartion1.eos_only())
        self.assertTrue(registartion1.is_pending_status())
        self.assertFalse(registartion1.is_dropped_status())
        self.assertFalse(registartion1.is_standby_status())

    def test_has_start_end_dates(self):
        json_data = {u'StartDate': u'01/29/2013',
                     u'EndDate': u'06/22/2013'}
        self.assertTrue(has_start_end_dates(json_data))
        json_data = {"FeeBaseType": ""}
        self.assertFalse(has_start_end_dates(json_data))
        json_data = {"FeeBaseType": "", "StartDate": "", "EndDate": ""}
        self.assertFalse(has_start_end_dates(json_data))

    def test_comparing_majors_minors(self):
        result_dict = enrollment_search_by_regid(
            '9136CCB8F66711D5BE060004AC494FFE')

        enroll = result_dict.get(get_current_term())
        self.assertTrue(enroll.majors[0] in enroll.majors)
        self.assertTrue(enroll.minors[0] in enroll.minors)

        enroll1 = result_dict.get(get_term_by_year_and_quarter(2013, 'summer'))
        self.assertFalse(enroll.majors[0] in enroll1.majors)

        enroll3 = result_dict.get(
            get_term_by_year_and_quarter(2012, 'spring'))
        self.assertFalse(enroll3.minors[0] in enroll.minors)

    def test_get_enrollment_history_by_regid(self):
        result_list = get_enrollment_history_by_regid(
            '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(len(result_list), 7)
        self.assertEqual(result_list[0].term.year, 1996)
        self.assertEqual(result_list[0].term.quarter, "autumn")
        self.assertEqual(result_list[0].majors[0].major_name,
                         "PRE MAJOR (A&S)")

        self.assertEqual(result_list[-2].term.year, 2013)
        self.assertEqual(result_list[-2].term.quarter, "summer")
        self.assertEqual(result_list[-2].majors[0].major_name, "ENGLISH")
