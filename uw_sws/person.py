"""
Interfacing with the Student Web Service, Person resource
"""
import logging
from dateutil.parser import parse
from uw_sws.models import SwsPerson, StudentAddress, LastEnrolled
from uw_sws import get_resource


logger = logging.getLogger(__name__)
sws_url_prefix = "/student/v5/person/"
sws_url_suffix = ".json"


def get_person_by_regid(regid):
    """
    Returns a uw_sws.models.SwsPerson object
    """
    url = sws_url_prefix + regid + sws_url_suffix
    return _process_json_data(get_resource(url))


def _process_json_data(person_data):
    """
    Returns a uw_sws.models.SwsPerson object
    """
    person = SwsPerson()
    if person_data["BirthDate"]:
        person.birth_date = parse(person_data["BirthDate"]).date()
    person.directory_release = person_data["DirectoryRelease"]
    person.email = person_data["Email"]
    person.employee_id = person_data["EmployeeID"]
    person.first_name = person_data["FirstName"]
    person.gender = person_data["Gender"]
    person.last_name = person_data["LastName"]
    person.pronouns = person_data["Pronouns"]
    person.student_name = person_data["StudentName"]

    if person_data["LastEnrolled"] is not None:
        last_enrolled = LastEnrolled()
        last_enrolled.href = person_data["LastEnrolled"]["Href"]
        last_enrolled.quarter = person_data["LastEnrolled"]["Quarter"]
        last_enrolled.year = person_data["LastEnrolled"]["Year"]
        person.last_enrolled = last_enrolled

    if person_data["LocalAddress"] is not None:
        address_data = person_data["LocalAddress"]
        local_address = StudentAddress()
        local_address.city = address_data["City"]
        local_address.country = address_data["Country"]
        local_address.street_line1 = address_data["Line1"]
        local_address.street_line2 = address_data["Line2"]
        local_address.postal_code = address_data["PostalCode"]
        local_address.state = address_data["State"]
        local_address.zip_code = address_data["Zip"]
        person.local_address = local_address

    person.local_phone = person_data["LocalPhone"]

    if person_data["PermanentAddress"] is not None:
        perm_address_data = person_data["PermanentAddress"]
        permanent_address = StudentAddress()
        permanent_address.city = perm_address_data["City"]
        permanent_address.country = perm_address_data["Country"]
        permanent_address.street_line1 = perm_address_data["Line1"]
        permanent_address.street_line2 = perm_address_data["Line2"]
        permanent_address.postal_code = perm_address_data["PostalCode"]
        permanent_address.state = perm_address_data["State"]
        permanent_address.zip_code = perm_address_data["Zip"]
        person.permanent_address = permanent_address

    person.permanent_phone = person_data["PermanentPhone"]
    person.uwregid = person_data["RegID"]
    person.student_number = person_data["StudentNumber"]
    person.student_system_key = person_data["StudentSystemKey"]
    person.uwnetid = person_data["UWNetID"]
    person.visa_type = person_data["VisaType"]

    return person
