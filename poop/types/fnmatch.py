import fnmatch as _fnmatch
from typing import Any

from poop.types.boolean import Boolean, false, true
from poop.types.list import List
from poop.types.string import Str


class Fnmatch:
    """Namespace mirroring Python's `fnmatch` module — Unix shell
    pattern matching against filenames.
    """

    @staticmethod
    def fnmatch(filename: Str, pattern: Str) -> Boolean:
        return true if _fnmatch.fnmatch(filename._value, pattern._value) else false

    @staticmethod
    def fnmatchcase(filename: Str, pattern: Str) -> Boolean:
        return true if _fnmatch.fnmatchcase(filename._value, pattern._value) else false

    @staticmethod
    def filter(names: Any, pattern: Str) -> List:
        # fnmatch.filter wants an iterable of str; unwrap each POOP Str.
        # `names` is typed Any because POOP `List` iteration yields
        # generic `Object`; the contract is "iterable of Str" at runtime.
        python_names = [n._value for n in names]
        kept = _fnmatch.filter(python_names, pattern._value)
        return List(*(Str(s) for s in kept))

    @staticmethod
    def translate(pattern: Str) -> Str:
        return Str(_fnmatch.translate(pattern._value))
