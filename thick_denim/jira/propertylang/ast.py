from typing import List


class Node(object):
    def __eq__(self, other):
        return getattr(other, "__dict__", None) == self.__dict__

    def __repr__(self):
        fields = [f"{x[0]}={x[1]!r}" for x in self.__dict__.items()]
        cfields = ", ".join(fields)
        return f"{self.__class__.__name__}({cfields})"


class Key(Node):
    def __init__(self, name: str):
        self.name = name


class Value(Node):
    def __init__(self, value):
        self.value = value


class KeyValue(Node):
    def __init__(self, key: Key, value: Value):
        self.key = key
        self.value = value


class Object(Node):
    def __init__(self, key_values: List[KeyValue]):
        self.key_values = key_values
