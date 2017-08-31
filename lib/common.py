# vim: ts=4 sts=4 sw=4 et: syntax=python

def list2map(items, key_field):
    items_map = {}
    for item in items:
        items_map[str(item[key_field])] = item

    return items_map

def list2map_ex(items, key_field_fun, arg):
    items_map = {}
    for item in items:
        items_map[str(item[key_field_fun(item, arg)])] = item

    return items_map

def remove_keys(item, keys):
    new_item = item.copy()
    for key in keys:
        if key in new_item:
            del new_item[key]

    return new_item

def remove_subtree(item, subtree):
    return _remove_subtree(item.copy(), subtree)

def _remove_subtree(item, subtree):
    for key, value in subtree.iteritems():
        if isinstance(value, dict):
            item[key] = _remove_subtree(item[key], value)
            if len(item[key]) < 1:
                del item[key]
        else:
            del item[key]

    return item
