# vim: ts=4 sts=4 sw=4 et: syntax=python

from lib.exceptions import ScreenboardNotFoundException
from lib.strings import Strings

from datadog import initialize, api

class DatadogApi(object):
    DEFAULT_CHARSET = 'utf-8'

    API_CALLS = 0

    def __init__(self, api_key, app_key):
        options = {
            'api_key': api_key,
            'app_key': app_key,
        }
        initialize(**options)

    @classmethod
    def search_monitors(cls, filter_string):
        monitors = cls._get_api().Monitor.get_all(name=filter_string)
        return cls._remove_unicode(monitors)

    @classmethod
    def search_screenboard(cls, title):
        normalized_title = cls.gnmn(title)
        result = cls._get_api().Screenboard.get_all()
        for screenboard in result["screenboards"]:
            if cls.gnmn(screenboard["title"]) == normalized_title:
                screenboard = cls._get_api().Screenboard.get(screenboard["id"])
                return cls._remove_unicode(screenboard)

        raise ScreenboardNotFoundException(title)

    @classmethod
    def get_existing_monitors(cls, monitors):
        names_map = {}
        for monitor in monitors:
            names_map[cls.gnmn(monitor["name"])] = 1

        prefix = Strings.get_prefix(names_map.keys())
        prefixed_monitors = cls.search_monitors(prefix)
        if len(prefixed_monitors) < 1:
            return {}

        existing_monitors = {}
        for monitor in prefixed_monitors:
            name = cls.gnmn(monitor["name"])
            if name in names_map:
                existing_monitors[name] = monitor

        return existing_monitors

    @classmethod
    def update_screenboard(cls, board_id, data):
        cls._get_api().Screenboard.update(board_id, **data)

    @classmethod
    def create_screenboard(cls, data):
        screenboard = cls._get_api().Screenboard.create(**data)
        return screenboard["id"]

    @classmethod
    def update_monitor(cls, board_id, data):
        cls._get_api().Monitor.update(board_id, **data)

    @classmethod
    def create_monitor(cls, data):
        monitor = cls._get_api().Monitor.create(**data)
        return monitor["id"]

    @classmethod
    def get_api_calls(cls):
        return cls.API_CALLS

    @staticmethod
    # get normalized monitor name
    def gnmn(name):
        return name.lower()

    @classmethod
    def _remove_unicode(cls, data):
        if isinstance(data, unicode):
            data = data.encode(cls.DEFAULT_CHARSET)
        elif isinstance(data, list):
            for i in xrange(len(data)):
                data[i] = cls._remove_unicode(data[i])
        elif isinstance(data, dict):
            for key, value in data.iteritems():
                data[key] = cls._remove_unicode(value)

        return data

    @classmethod
    def _get_api(cls):
        cls.API_CALLS += 1
        return api
