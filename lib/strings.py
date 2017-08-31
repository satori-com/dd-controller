# vim: ts=4 sts=4 sw=4 et: syntax=python

class Strings(object):

    @classmethod
    def get_prefix(cls, strings):
        assert len(strings) > 0, \
            "Empty string list"

        if len(strings) == 1:
            return strings[0]

        prefix = strings[0]
        for string in strings[1:]:
            prefix = cls._get_prefix(prefix, string)

        return prefix

    @staticmethod
    def _get_prefix(string1, string2):
        max_length = min(len(string1), len(string2))
        i = 0
        while (i < max_length) and (string1[i] == string2[i]):
            i += 1

        return string1[0:i]
