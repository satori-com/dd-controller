# vim: ts=4 sts=4 sw=4 et: syntax=python

from lib.templater import Templater
from lib.datadog_api import DatadogApi
from lib.exceptions import EmptyKeyFieldException, \
                           FilterRequiredException, \
                           MonitorNotFoundException, \
                           MonitorsFilterRequiredException, \
                           MonitorsListEmptyException, \
                           NotUniqueKeyException, \
                           ScreenboardNotFoundException
from lib.common import list2map, remove_keys
from lib.messages import error, warning

class RemoteConfig(object):
    MONITORS_IGNORED_KEYS = ["created",
                             "created_at",
                             "creator",
                             "deleted",
                             "id",
                             "modified",
                             "org_id",
                             "overall_state",
                             "overall_state_modified"]

    SCREENBOARD_IGNORED_KEYS = ["created",
                                "created_by",
                                "id",
                                "original_title",
                                "title_edited",
                                "modified"]

    SCREENBOARD_URL_TPL = "<screenboard-id>"

    WIDGETS_IGNORED_KEYS = ["board_id"]

    def __init__(self, api_key, app_key):
        self._datadog_api = DatadogApi(api_key=api_key, app_key=app_key)

    def get(self, monitors_filter, screenboard_name): # pylint: disable=too-many-branches
        if monitors_filter is None and screenboard_name is None:
            raise FilterRequiredException()

        if screenboard_name is not None:
            screenboard = self._datadog_api.search_screenboard(screenboard_name)

        if monitors_filter is not None:
            monitors = self._datadog_api.search_monitors(monitors_filter)

        # Convert alert_id to alert_name
        if screenboard_name is not None:
            _monitors = monitors if monitors_filter is not None else None
            self._alert_id_to_alert_name(_monitors,
                                         screenboard["widgets"])

        # Defaults format
        if screenboard_name is not None:
            screenboard["widgets"] = self._to_defaults_format(
                title="widgets",
                items=screenboard["widgets"],
                ignored_keys=self.WIDGETS_IGNORED_KEYS)

        # Hide screenbord name
        if screenboard_name is not None and monitors_filter is not None:
            for monitor in monitors:
                self._replace_monitor_desc(monitor,
                                           self._screenboard_url(screenboard),
                                           self.SCREENBOARD_URL_TPL)

        # Defaults format
        if monitors_filter is not None:
            monitors = self._to_defaults_format(
                title="monitors",
                items=monitors,
                ignored_keys=self.MONITORS_IGNORED_KEYS)

        # Create config
        config = {}
        if screenboard_name is not None:
            config["screenboard"] = \
                remove_keys(screenboard, self.SCREENBOARD_IGNORED_KEYS)
        if monitors_filter is not None:
            config["monitors"] = monitors

        return config

    def update(self, config, update_only): # pylint: disable=too-many-branches
        self.check_config_static(config)
        update = error if update_only else warning

        # Search for screenboard id
        if "screenboard" in config:
            board_title = config["screenboard"]["board_title"]
            try:
                screenboard = self._datadog_api.search_screenboard(board_title)
                config["screenboard"]["id"] = screenboard["id"]
            except ScreenboardNotFoundException:
                update("Screenboard '%s' does not exist" % (board_title))

        # Search for monitors ids
        if "monitors" in config:
            existing_monitors = \
                self._datadog_api.get_existing_monitors( \
                    config["monitors"]["items"])

            for monitor in config["monitors"]["items"]:
                name = self._datadog_api.gnmn(monitor["name"])
                if name in existing_monitors:
                    monitor["id"] = existing_monitors[name]["id"]
                else:
                    update("Monitor '%s' does not exist" % (monitor["name"]))

        # Create or update monitors
        delayed_update_monitors_screenboard = False
        if "monitors" in config:
            config["monitors"] = self._update_defaults(config["monitors"])
            if "id" in config["screenboard"]:
                self._update_monitors_screenboard(config["monitors"],
                                                  config["screenboard"])
            else:
                delayed_update_monitors_screenboard = True

            for monitor in config["monitors"]:
                self._create_or_update_monitor(monitor)

        # Create or update screenboard
        if "screenboard" in config:
            screenboard = config["screenboard"]

            screenboard["widgets"] \
                = self._update_defaults(screenboard["widgets"])

            # Convert alert_name to alert_id
            _monitors = config["monitors"] if "monitors" in config else None
            self._alert_name_to_alert_id(_monitors, screenboard["widgets"])

            self._create_or_update_screenboard(screenboard)

        # Resolve cyclic link: monitors>screen>monitors
        if delayed_update_monitors_screenboard:
            self._update_monitors_screenboard(config["monitors"],
                                              config["screenboard"])

            for monitor in config["monitors"]:
                self._create_or_update_monitor(monitor)

    @staticmethod
    def get_widget_key_field(widget, defaults):
        if "type" not in widget:
            widget["type"] = defaults["type"]

        if widget["type"] == "note":
            return "html"
        else:
            return "title_text"

    @staticmethod
    def get_monitor_key_field(_x, _y): # pylint: disable=unused-argument
        return "name"

    @classmethod
    def check_config_static(cls, config):
        if "screenboard" in config:
            cls._check_keys("screenboard's widget",
                            config["screenboard"]["widgets"]["items"],
                            cls.get_widget_key_field,
                            config["screenboard"]["widgets"]["defaults"])
        if "monitors" in config:
            cls._check_keys("monitor",
                            config["monitors"]["items"],
                            cls.get_monitor_key_field,
                            config["monitors"]["defaults"])

    @classmethod
    def _alert_id_to_alert_name(cls, monitors, widgets):
        cls._vise_versa_keys(monitors, widgets,
                             "id", "name",
                             "alert_id", "alert_name",
                             MonitorsFilterRequiredException)

    @classmethod
    def _alert_name_to_alert_id(cls, monitors, widgets):
        cls._vise_versa_keys(monitors, widgets,
                             "name", "id",
                             "alert_name", "alert_id",
                             MonitorsListEmptyException)

    @staticmethod
    def _vise_versa_keys(monitors, widgets, # pylint: disable=too-many-arguments
                         monitors_key_field1, monitors_key_field2,
                         widget_key_field1, widget_key_field2,
                         exception_class):
        if monitors is not None:
            monitors_map = list2map(monitors, monitors_key_field1)

        for widget in widgets:
            if widget["type"] == "alert_value":
                if monitors is None:
                    raise exception_class()

                widget_value = str(widget[widget_key_field1])
                if widget_value not in monitors_map:
                    raise MonitorNotFoundException(widget_value)

                widget[widget_key_field2] \
                    = monitors_map[widget_value][monitors_key_field2]
                del widget[widget_key_field1]

    def _update_monitors_screenboard(self, monitors, screenboard):
        for monitor in monitors:
            self._replace_monitor_desc(monitor,
                                       self.SCREENBOARD_URL_TPL,
                                       self._screenboard_url(screenboard))

    def _create_or_update_monitor(self, monitor):
        self._create_or_update_item(monitor,
                                    self._datadog_api.update_monitor,
                                    self._datadog_api.create_monitor)

    def _create_or_update_screenboard(self, screenboard):
        self._create_or_update_item(screenboard,
                                    self._datadog_api.update_screenboard,
                                    self._datadog_api.create_screenboard)

    @staticmethod
    def _create_or_update_item(item, update_method, create_method):
        if "id" in item:
            item_data = item.copy()
            del item_data["id"]
            update_method(item["id"], item_data)
        else:
            item["id"] = create_method(item)

    @staticmethod
    def _check_keys(title, items, key_field_fun, defaults):
        keys = set()
        index = 0
        for item in items:
            key_field = key_field_fun(item, defaults)
            value = str(item[key_field])
            if len(value) < 1:
                raise EmptyKeyFieldException(title, key_field, index, item)
            elif value in keys:
                raise NotUniqueKeyException(title, value, index, item)

            keys.add(value)
            index += 1

    @staticmethod
    def _screenboard_url(screenboard):
        safe_board_title = screenboard["board_title"].lower().replace(" ", "-")
        return "%d/%s" % (screenboard["id"], safe_board_title)

    @staticmethod
    def _replace_monitor_desc(monitor, f, t):
        replaced = monitor["message"].find(f) != -1
        monitor["message"] = monitor["message"].replace(f, t)
        if "escalation_message" in monitor["options"] \
            and isinstance(monitor["options"]["escalation_message"],
                           basestring):
            monitor["options"]["escalation_message"] = \
                monitor["options"]["escalation_message"].replace(f, t)
            if not replaced \
                and monitor["options"]["escalation_message"].find(f) != -1:
                replaced = True

        if not replaced:
            warning(("Monitor '%s' does not contain"
                     " a link to its screenboard") \
                     % (monitor["name"]))

    @staticmethod
    def _to_defaults_format(items, title, ignored_keys):
        templater = Templater(items=items, ignored_keys=ignored_keys)
        defaults = templater.get_defaults(title)
        return {
            "defaults": defaults,
            "items": templater.get_items(defaults)
        }

    @staticmethod
    def _update_defaults(data):
        items = data["items"]
        for item in items:
            item = Templater.update_defaults(item, data["defaults"])

        return items

    @staticmethod
    def _filter_keys(item, keys):
        new_item = {}
        for key in keys:
            new_item[key] = item[key]

        return new_item
