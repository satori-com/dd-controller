import unittest

from lib.comparator import Comparator
from lib.exceptions import CompareException

class ComparatorTestCase(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_join_paths(self):
        for (expected_result, x, y) in [
                ("", "", "")
                , ("a", "", "a")
                , ("a.b", "a", "b")
                , ("a.", "a", "")
        ]:
            self.assertEqual(expected_result, Comparator.join_paths(x, y))

    def test_diff_keys(self):
        for (expected_result, x, y) in [
                ([], {"a": 1}, {"a": 1})
                , (["a"], {"a": 1}, {"b": 1})
                , (["a"], {"a": 1, "b": 2}, {"b": 1})
                , (["b"], {"a": 1, "b": 2}, {"a": 1})
        ]:
            self.assertEqual(expected_result, Comparator.diff_keys(x, y))

    def test_different_type(self):
        self.assertRaises(CompareException, self.cmp, 1, "str")

    def test_equal_type(self):
        self.assertTrue(self.cmp(1, 1))

    def test_different_value(self):
        self.assertRaises(CompareException, self.cmp, 1, 2)

    def test_small_left_part(self):
        self.assertRaises(CompareException, self.cmp,
                          {"a": 1}, {"a": 1, "b": 2})

    def test_small_right_part(self):
        self.assertRaises(CompareException, self.cmp,
                          {"a": 1, "b": 2}, {"a": 1})

    def test_equal_maps(self):
        self.assertTrue(self.cmp({"a": 1, "b": 2}, {"a": 1, "b": 2}))

    def test_different_subkey(self):
        self.assertRaises(CompareException, self.cmp,
                          {"a": {"b": 2}}, {"a": {"b": 3}})

    @staticmethod
    def cmp(item1, item2):
        return Comparator.compare("left part", item1, "right part", item2)
