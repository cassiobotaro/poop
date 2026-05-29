import fnmatch as _fnmatch
from typing import Any

from poop.types.boolean import Boolean, to_boolean
from poop.types.list import List
from poop.types.string import Str


class Fnmatch:
    """Namespace mirroring Python's `fnmatch` module — Unix shell
    pattern matching against filenames.
    """

    @staticmethod
    def fnmatch(name: Str, pat: Str) -> Boolean:
        return to_boolean(_fnmatch.fnmatch(name._value, pat._value))

    @staticmethod
    def fnmatchcase(name: Str, pat: Str) -> Boolean:
        return to_boolean(_fnmatch.fnmatchcase(name._value, pat._value))

    @staticmethod
    def filter(names: Any, pat: Str) -> List:
        # fnmatch.filter wants an iterable of str; unwrap each POOP Str.
        # `names` is typed Any because POOP `List` iteration yields
        # generic `Object`; the contract is "iterable of Str" at runtime.
        python_names = [n._value for n in names]
        kept = _fnmatch.filter(python_names, pat._value)
        return List(*(Str(s) for s in kept))

    @staticmethod
    def translate(pat: Str) -> Str:
        return Str(_fnmatch.translate(pat._value))
