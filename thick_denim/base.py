"""
contains generic implementations used across the codebase. Mainly data-models
"""
import hashlib
import re
import json
import logging
import pendulum
import itertools
from pathlib import Path
from datetime import datetime
from typing import List, Callable
from fnmatch import fnmatch
from ordered_set import OrderedSet

from thick_denim.ui import UserFriendlyObject
from humanfriendly.tables import format_robust_table, format_pretty_table
from thick_denim.errors import ThickDenimModelError, ThickDenimError
from thick_denim.meta import (
    is_builtin_class_except,
    metaclass_declaration_contains_required_attribute,
)
from thick_denim.models import DataBag

ITERABLES = (list, tuple, itertools.chain, set, map, filter, OrderedSet)

logger = logging.getLogger(__name__)


def try_int(s):
    try:
        return int(s)
    except ValueError:
        return s


def slugify(text: str, separator: str = "-"):
    return re.sub(r"[^a-zA-Z0-9-]+", separator, text).strip(separator)


def ensure_datetime(value):
    if isinstance(value, str):
        return pendulum.parse(value)
    if isinstance(value, datetime):
        return pendulum.instance(value)
    if isinstance(value, pendulum.DateTime):
        return value

    raise ThickDenimError(f"cannot convert to datetime: {value!r}")


def is_builtin_model(target: type) -> bool:
    """returns ``True`` if the given type is a model subclass"""

    return is_builtin_class_except(target, ["MetaModel", "Model", "DataBag"])


def validate_model_declaration(cls, name, attrs):
    """validates model class definitions"""
    target = f"{cls}.__visible_atttributes__"

    if not is_builtin_model(cls):
        return

    visible_atttributes = metaclass_declaration_contains_required_attribute(
        cls, name, attrs, "visible_atttributes", str
    )

    if not isinstance(visible_atttributes, (tuple, list)):
        raise TypeError(f"{target} must be a list of strings")

    for index, field in enumerate(visible_atttributes):
        if isinstance(field, str):
            continue

        raise TypeError(
            f"{target}[{index}] should be a string, "
            f"but is {field!r} ({type(field)})"
        )

    id_atttributes = metaclass_declaration_contains_required_attribute(
        cls, name, attrs, "id_atttributes", str
    )

    if not isinstance(id_atttributes, (tuple, list)):
        raise TypeError(f"{target} must be a list of strings")

    for index, field in enumerate(id_atttributes):
        if isinstance(field, str):
            continue

        raise TypeError(
            f"{target}[{index}] should be a string, "
            f"but is {field!r} ({type(field)})"
        )


class MetaModel(type):
    """metaclass for data models
    """

    def __init__(cls, name, bases, attrs):
        if is_builtin_model(cls):
            return

        if not is_builtin_model(cls):
            validate_model_declaration(cls, name, attrs)

        super().__init__(name, bases, attrs)


class Model(DataBag, metaclass=MetaModel):
    """Base model for data in all domains, from boto3 responses to
    command-line output of kubernetes tools such as kubectl, kubectx.
    """

    __visible_atttributes__: List[str] = []
    __id_attributes__: List[str] = []

    def __init__(self, data: dict = None, *args, **kw):
        if isinstance(data, UserFriendlyObject):
            data = data.serialize()

        self.__data__ = data or {}
        self.__args__ = args
        self.__kw__ = kw
        self.initialize(*args, **kw)

    def __lt__(self, e) -> bool:
        return self.sort_key < e.sort_key

    def __lte__(self, e) -> bool:
        return self.sort_key <= e.sort_key

    def __gt__(self, e) -> bool:
        return self.sort_key > e.sort_key

    def __gte__(self, e) -> bool:
        return self.sort_key >= e.sort_key

    def __eq__(self, other):
        criteria = [
            isinstance(other, type(self)),
            other.__ui_attributes__() == self.__ui_attributes__(),
        ]
        return all(criteria)

    def __id__(self):
        return sum(
            filter(
                lambda v: isinstance(v, int),
                [try_int(self.get(k)) for k in self.__id_attributes__],
            )
        )

    def __hash__(self):
        values = dict(
            [(k, try_int(self.get(k))) for k in self.__id_attributes__]
        )
        string = json.dumps(values)
        return int(hashlib.sha1(bytes(string, "ascii")).hexdigest(), 16)

    def initialize(self, *args, **kw):
        pass

    def update(self, data: dict):
        self.__data__.update(data)

    @property
    def sort_key(self):
        return hash(self)

    @property
    def _raw_data(self):
        return self.__data__

    def serialize(self):
        return self.__data__.copy()

    def to_dict(self):
        return self.serialize()

    def to_json(self, *args, **kw):
        kw["default"] = kw.pop("default", str)
        return json.dumps(self.to_dict(), *args, **kw)

    def __getitem__(self, key):
        return self.__data__.get(key, None)

    def get(self, *args, **kw):
        return self.__data__.get(*args, **kw)

    def __ui_attributes__(self):
        return dict(
            [
                (name, getattr(self, name, self.get(name)))
                for name in self.__visible_atttributes__
            ]
        )

    def attribute_matches_glob(
        self, attribute_name: str, fnmatch_pattern: str
    ) -> bool:
        """helper method to filter models by an attribute. This allows for
        :py:class:`~thick_denim.base.ModelList` to
        :py:meth:`~thick_denim.base.ModelList.filter_by`.
        """
        try:
            value = getattr(self, attribute_name, self.get(attribute_name))
        except AttributeError as e:
            raise ThickDenimModelError(
                f"{self} does not have a {attribute_name!r} attribute: {e}"
            )

        if isinstance(fnmatch_pattern, str):
            return fnmatch(value or "", fnmatch_pattern or "")
        else:
            return value == fnmatch_pattern

    @classmethod
    def List(cls, *items):
        return ModelList(cls, *items)

    @classmethod
    def Set(cls, *items):
        return ModelSet(cls, *items)

    def get_table_columns(self):
        return self.__class__.__visible_atttributes__

    def get_table_rows(self):
        return [list(self.__ui_attributes__().values())]

    def get_table_colums_and_rows(self):
        columns = self.get_table_columns()
        rows = self.get_table_rows()
        return columns, rows

    def format_robust_table(self):
        columns, rows = self.get_table_colums_and_rows()
        return format_robust_table(rows, columns)

    def format_pretty_table(self):
        columns, rows = self.get_table_colums_and_rows()
        return format_pretty_table(rows, columns)


class IterableCollection:
    def initialize(self, model_class: type):
        if not isinstance(model_class, type) or not issubclass(
            model_class, Model
        ):
            raise TypeError(
                f"ModelList requires the 'model_class' attribute to be "
                "a Model subclass, got {model_class!r} instead"
            )

        self.model_class = model_class

    def New(self, items, **kw):
        return self.__class__(self.model_class, sorted(items, **kw))

    def sorted(self, **kw):
        return self.New(sorted(self, **kw))

    def sorted_by(self, attribute: str, **kw):
        return self.sorted(
            key=lambda model: getattr(model, attribute, model.get(attribute)),
            **kw,
        )

    def filter_by(
        self, attribute_name: str, fnmatch_pattern: str
    ) -> List[Model]:
        return self.filter(
            lambda model: model.attribute_matches_glob(
                attribute_name, fnmatch_pattern
            )
        )

    def filter(self, check: Callable[[Model], bool]) -> List[Model]:
        for index, model in enumerate(self):
            if not isinstance(model, self.model_class):
                raise ValueError(
                    f"{self}[{index}] is not an instance of {self.model_class}"
                )

        return self.New(list(filter(check, self)))

    def get_table_columns(self):
        return self.model_class.__visible_atttributes__

    def get_table_rows(self):
        return [model.__ui_attributes__().values() for model in self]

    def get_table_colums_and_rows(self):
        columns = self.get_table_columns()
        rows = self.get_table_rows()
        return columns, rows

    def format_robust_table(self):
        columns, rows = self.get_table_colums_and_rows()
        return format_robust_table(rows, columns)

    def format_pretty_table(self):
        columns, rows = self.get_table_colums_and_rows()
        return format_pretty_table(rows, columns)

    def to_dict(self) -> List[dict]:
        return [m.to_dict() for m in self]


class ModelList(list, IterableCollection):
    """Special list subclass that only supports
    :py:class:`~thick_denim.base.Model` as children and
    supports filtering by instance attributes by calling
    :py:meth:`~thick_denim.base.Model.attribute_matches_glob`.
    """

    def __init__(self, model_class: type, children: List[Model]):
        self.initialize(model_class)
        if not isinstance(children, ITERABLES):
            raise TypeError(
                f"ModelList requires the 'children' attribute to be "
                f"a list, got {children!r} {type(children)} instead"
            )

        super().__init__(map(model_class, children))


class ModelSet(OrderedSet, IterableCollection):
    """Special OrderedSet subclass that only supports
    :py:class:`~thick_denim.base.Model` as children and
    supports filtering by instance attributes by calling
    :py:meth:`~thick_denim.base.Model.attribute_matches_glob`.
    """

    def __init__(self, model_class: type, children: List[Model]):
        self.initialize(model_class)
        if not isinstance(children, ITERABLES):
            raise TypeError(
                f"ModelList requires the 'children' attribute to be "
                f"a list, got {children!r} {type(children)} instead"
            )

        super().__init__(map(model_class, children))


def store_models(items: List[Model], filename: str) -> bool:
    path = Path(".td_cache").joinpath(filename)

    path.parent.mkdir(exist_ok=True, parents=True)
    with path.open("w") as fd:
        json.dump(items.to_dict(), fd, indent=2)
        return True


def load_models(filename: str, model_class: Model) -> List[Model]:
    path = Path(".td_cache").joinpath(filename)

    path.parent.mkdir(exist_ok=True, parents=True)
    if not path.exists():
        return None

    with path.open() as fd:
        try:
            items = json.load(fd)
        except json.decoder.JSONDecodeError as e:
            logger.warning(f"could not parse json from {filename}: {e}")
            return

        return model_class.List(items)
