# vim: ts=4 sts=4 sw=4 et: syntax=python

from lib.exceptions import CompareException

class Comparator(object):
    _PATH_SEPARATOR = "."

    @classmethod
    def compare(cls, title1, item1, title2, item2):
        return cls._compare("", title1, item1, title2, item2)

    @classmethod
    def join_paths(cls, path1, path2):
        if path1 == "":
            return path2
        else:
            return path1 + cls._PATH_SEPARATOR + path2

    @staticmethod
    def diff_keys(map1, map2):
        return list(set(map1.keys()) - set(map2.keys()))

    @classmethod
    def _compare(cls, path, title1, item1, title2, item2): # pylint: disable=too-many-arguments
        if type(item1) != type(item2):
            error = ("Types of key '%s' are different:\n"
                     "%s: %s\n"
                     "%s: %s") \
                    % (path, title1, type(item1), title2, type(item2))
            raise CompareException(error)

        if isinstance(item1, dict):
            left_keys = cls.diff_keys(item1, item2)
            if len(left_keys) > 0:
                error = "Map '%s' of %s does not contain some keys of %s: %s" \
                        % (path, title2, title1, ", ".join(left_keys))
                raise CompareException(error)

            right_keys = cls.diff_keys(item2, item1)
            if len(right_keys) > 0:
                error = "Map '%s' of %s does not contain some keys of %s: %s" \
                        % (path, title1, title2, ", ".join(right_keys))
                raise CompareException(error)

            for key, value in item1.iteritems():
                cls._compare(cls.join_paths(path, key),
                             title1, value, title2, item2[key])

        elif item1 != item2:
            error = ("Values of key '%s' are different:\n"
                     "%s: %s\n"
                     "%s: %s") \
                    % (path, title1, item1, title2, item2)
            raise CompareException(error)

        return True
