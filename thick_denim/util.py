from functools import reduce


def traverse_dict_children(data, *keys, fallback=None):
    """attempts to retrieve the config value under the given nested keys
    """
    value = reduce(lambda d, l: d.get(l, {}), keys, data)
    return value or fallback
