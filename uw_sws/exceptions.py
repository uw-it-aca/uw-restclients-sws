from restclients_core.exceptions import DataFailureException


class ThreadedDataError(DataFailureException):
    def __init__(self, url, status, msg):
        super(ThreadedDataError, self).__init__(url, status, msg)


class InvalidCanvasIndependentStudyCourse(Exception):
    """Exception for invalid Canvas course."""
    pass


class InvalidCanvasSection(Exception):
    """Exception for invalid Canvas section."""
    pass


class InvalidSectionID(Exception):
    """Exception for invalid section id."""
    pass


class InvalidSectionURL(Exception):
    """Exception for invalid section url."""
    pass


class InvalidCourseID(Exception):
    """Exception for invalid section id."""
    pass
