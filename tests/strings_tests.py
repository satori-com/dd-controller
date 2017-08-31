import unittest

from lib.strings import Strings

class StringsTestCase(unittest.TestCase): # pylint: disable=too-many-public-methods

    def test_get_prefix(self):
        for (expected_result, x) in [
                ("", ["", ""])
                , ("a", ["a"])
                , ("a", ["ab", "ac"])
                , ("ab", ["abc", "abd"])
                , ("a", ["abc", "abd", "ad"])
                , ("", ["abc", "abd", "d"])
        ]:
            self.assertEqual(expected_result, Strings.get_prefix(x))

    def test_empty_list(self):
        self.assertRaises(AssertionError, Strings.get_prefix, [])
