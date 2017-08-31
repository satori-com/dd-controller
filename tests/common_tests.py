import unittest

from lib.common import list2map, list2map_ex, remove_keys, remove_subtree

class CommonTestCase(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_list2map(self):
        for (expected_result, a, k) in [
                ({}, [], "a")
                , ({}, {}, "a")
                , ({'1': {"a": 1}}, [{"a": 1}], "a")
                , ({'1': {"a": 1}, '2': {"a": 2}}, [{"a": 1}, {"a": 2}], "a")
                , ({'1': {"a": 1}}, [{"a": 1}, {"a": 1}], "a")
        ]:
            self.assertEqual(expected_result, list2map(a, k))

    def test_list2map_ex(self):
        for (expected_result, a, arg) in [
                ({}, [], "a")
                , ({}, {}, "a")
                , ({'1': {"a": 1}}, [{"a": 1}], "a")
                , ({'1': {"a": 1}, '2': {"a": 2}}, [{"a": 1}, {"a": 2}], "a")
                , ({'1': {"a": 1}}, [{"a": 1}, {"a": 1}], "a")
                , ({'1': {'t': 'b', 'z': 1}, '5': {'a': 5}},
                   [{"z": 1, "t": "b"}, {"a": 5}], "z")
        ]:
            self.assertEqual(expected_result,
                             list2map_ex(a, self._key_field_fun, arg))

    def test_remove_keys(self):
        for (expected_result, a, keys) in [
                ({"a": 1, "b": 2}, {"a": 1, "b": 2}, [])
                , ({"a": 1, "b": 2}, {"a": 1, "b": 2}, ["c"])
                , ({"b": 2}, {"a": 1, "b": 2}, ["a"])
                , ({"a": 1}, {"a": 1, "b": 2}, ["b"])
                , ({}, {"a": 1, "b": 2}, ["a", "b"])
        ]:
            self.assertEqual(expected_result, remove_keys(a, keys))

    def test_remove_subtree(self):
        for (expected_result, a, subtree) in [
                ({"b": 2}, {"a": 1, "b": 2}, {"a": 1})
                , ({"b": 2}, {"a": 1, "b": 2}, {"a": 2})
                , ({"a": 0, "b": {"ba": 1}},
                   {"a": 0, "b": {"ba": 1, "bb": 2}}, {"b": {"bb": 2}})
                , ({"a": 0},
                   {"a": 0, "b": {"ba": 1, "bb": 2}}, {"b": {"ba": 1, "bb": 2}})
                , ({"a": 0},
                   {"a": 0, "b": {"ba": 1, "bb": 2}}, {"b": {"bb": 1, "ba": 2}})
                , ({}, {"a": 0, "b": {"ba": 1, "bb": 2}},
                   {"a": 0, "b": {"ba": 1, "bb": 2}})
        ]:
            self.assertEqual(expected_result, remove_subtree(a, subtree))

    @staticmethod
    def _key_field_fun(item, arg):
        if "t" in item and item["t"] == "b":
            return arg
        else:
            return "a"
