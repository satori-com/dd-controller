import unittest

from lib.templater import Templater

class TemplaterTestCase(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_get_tree_defaults(self):
        for expected_defaults, base, x in [
                ({}, {}, {})
                , ({"a": 1}, {"a": 1}, {"a": 1})
                , ({"a": []}, {"a": []}, {"a": []})
                , ({"a": 1}, {"a": 1}, {"a": 1, "b": 1})
                , ({"a": 1}, {"a": 1, "b": 3}, {"a": 1, "b": 2})
                , ({"a": 1}, {"a": 1, "c": 3}, {"a": 1, "b": 2})
                , ({"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3}, {"a": 1, "b": 2})
                , ({"a": {"aa": 1}}, {"a": {"aa": 1, "ac": 3}},
                   {"a": {"aa": 1, "ab": 2}})
        ]:
            self.assertEqual(expected_defaults,
                             Templater.get_tree_defaults(base, x))

    def test_get_defaults(self):
        templater = Templater([{"a": 1, "b": 2}, {"a": 1, "b": 3}], [])
        self.assertEqual({"a": 1}, templater.get_defaults(""))

    def test_ignored_keys(self):
        templater = Templater([{"a": 1, "b": 2}, {"a": 1, "b": 2}], ["a"])
        self.assertEqual({"b": 2}, templater.get_defaults(""))

    def test_not_enough_items(self):
        templater = Templater([{"a": 1, "b": 2}], [])
        self.assertEqual({}, templater.get_defaults(""))

    def test_get_items(self):
        templater = Templater([{"a": [1], "b": [2]}, {"a": [1], "b": [3]}], [])
        defaults = templater.get_defaults("")
        self.assertEqual({"a": [1]}, defaults)
        self.assertEqual([{'b': [2]}, {'b': [3]}],
                         templater.get_items(defaults))

    def test_update_defaults(self):
        for expected_defaults, x, defaults in [
                ({}, {}, {})
                , ({"a": 2}, {"a": 1}, {"a": 2})
                , ({"a": []}, {"a": []}, {"a": []})
                , ({"a": 1, "b": 1}, {"a": 1}, {"b": 1})
                , ({"a": 2, "b": 1}, {"a": 1}, {"a": 2, "b": 1})
                , ({"a": {"aa": 1, "ab": 2}}, {"a": {"aa": 1}},
                   {"a": {"ab": 2}})
                , ({"a": {"aa": 1, "ab": 3}}, {"a": {"aa": 1, "ab": 2}},
                   {"a": {"ab": 3}})
        ]:
            self.assertEqual(expected_defaults,
                             Templater.update_defaults(x, defaults))
