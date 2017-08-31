# vim: ts=4 sts=4 sw=4 et: syntax=python

from lib.common import remove_subtree, remove_keys
from lib.messages import warning

class Templater(object):
    def __init__(self, items, ignored_keys):
        self._items = []
        for item in items:
            self._items.append(remove_keys(item, ignored_keys))

    def get_defaults(self, title):
        if len(self._items) < 2:
            warning("Not enough %s (%d) to calculate defaults" \
                    % (title, len(self._items)))
            return {}

        defaults = self._items[0].copy()
        for item in self._items[1:]:
            defaults = self.get_tree_defaults(defaults, item)

        return defaults

    def get_items(self, defaults):
        items = []
        for item in self._items:
            new_item = remove_subtree(item, defaults)
            items.append(new_item)

        return items

    @classmethod
    def get_tree_defaults(cls, defaults, item):
        new_defaults = {}
        for key, value in item.iteritems():
            if key in defaults:
                if isinstance(value, dict):
                    new_value = cls.get_tree_defaults(defaults[key], value)
                    new_defaults[key] = new_value
                elif defaults[key] == value:
                    new_defaults[key] = value

        return new_defaults

    @classmethod
    def update_defaults(cls, item, defaults):
        for key, value in defaults.iteritems():
            if isinstance(value, dict):
                if key not in item:
                    item[key] = value
                else:
                    item[key] = cls.update_defaults(item[key], value)
            else:
                item[key] = value

        return item
