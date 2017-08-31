# vim: ts=4 sts=4 sw=4 et: syntax=python

class CustomException(Exception):
    def __init__(self, message):
        super(CustomException, self).__init__(message)

class ScreenboardNotFoundException(CustomException):
    def __init__(self, title):
        message = "Can't find a screenboard with title '%s'" % (title)
        super(ScreenboardNotFoundException, self).__init__(message)

class CompareException(CustomException):
    def __init__(self, message):
        super(CompareException, self).__init__(message)

class MonitorNotFoundException(CustomException):
    def __init__(self, alert_id):
        message = ("Can't find a monitor with id %s"
                   " in the list of filtered monitors") % (alert_id)
        super(MonitorNotFoundException, self).__init__(message)

class MonitorsFilterRequiredException(CustomException):
    def __init__(self):
        message = ("There is a monitor in the screenboard,"
                   " but the monitors' search filter isn't set")
        super(MonitorsFilterRequiredException, self).__init__(message)

class MonitorsListEmptyException(CustomException):
    def __init__(self):
        message = ("There is a monitor in the screenboard,"
                   " but the monitors' list is empty")
        super(MonitorsListEmptyException, self).__init__(message)

class FilterRequiredException(CustomException):
    def __init__(self):
        message = ("Both a monitors' search filter"
                   " and a screenboard name are empty")
        super(FilterRequiredException, self).__init__(message)

class EmptyKeyFieldException(CustomException):
    def __init__(self, title, key_field, index, item):
        message = "Empty key field '%s' at pos #%d of %s %s" \
                  % (key_field, index, title, item)
        super(EmptyKeyFieldException, self).__init__(message)

class NotUniqueKeyException(CustomException):
    def __init__(self, title, value, index, item):
        message = "Key '%s' at pos #%d of %s %s is not unique" \
                  % (value, index, title, item)
        super(NotUniqueKeyException, self).__init__(message)
