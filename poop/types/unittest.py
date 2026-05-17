from __future__ import annotations

import unittest as _unittest
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str


def _unwrap(x: Any) -> Any:
    """Recursively unwrap POOP values to Python primitives for equality assertions."""
    if hasattr(x, "_value"):
        return x._value
    return x


class TestResult(Object):
    """Wraps Python's `unittest.TestResult` — counts and failures from a test run."""

    __slots__ = ("_impl",)
    __test__ = False  # pytest: not a test class

    def __init__(self, impl: Any = None) -> None:
        self._impl = _unittest.TestResult() if impl is None else impl

    @property
    def testsRun(self) -> Int:
        return Int(self._impl.testsRun)

    def wasSuccessful(self) -> Boolean:
        return true if self._impl.wasSuccessful() else false

    def failure_count(self) -> Int:
        return Int(len(self._impl.failures))

    def error_count(self) -> Int:
        return Int(len(self._impl.errors))

    def skipped_count(self) -> Int:
        return Int(len(self._impl.skipped))


class TestCase(Object):
    """POOP-flavoured `unittest.TestCase` base class.

    Subclasses can define `test_*` methods. `setUp` / `tearDown` /
    `setUpClass` / `tearDownClass` hooks behave the same as Python's
    `unittest.TestCase`. Assertion methods accept POOP values.
    """

    __slots__ = ()
    __test__ = False  # pytest: not a test class

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    def assertEqual(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if _unwrap(a) != _unwrap(b):
            text = f"{a!r} != {b!r}" if msg is None else f"{a!r} != {b!r}: {msg._value}"
            raise AssertionError(text)

    def assertNotEqual(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if _unwrap(a) == _unwrap(b):
            text = f"{a!r} == {b!r}" if msg is None else f"{a!r} == {b!r}: {msg._value}"
            raise AssertionError(text)

    def assertTrue(self, x: Any, msg: Str | None = None) -> None:
        if not bool(x):
            text = (
                f"{x!r} is not truthy"
                if msg is None
                else f"{x!r} is not truthy: {msg._value}"
            )
            raise AssertionError(text)

    def assertFalse(self, x: Any, msg: Str | None = None) -> None:
        if bool(x):
            text = (
                f"{x!r} is not falsy"
                if msg is None
                else f"{x!r} is not falsy: {msg._value}"
            )
            raise AssertionError(text)

    def assertIs(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if a is not b:
            text = (
                f"{a!r} is not {b!r}"
                if msg is None
                else f"{a!r} is not {b!r}: {msg._value}"
            )
            raise AssertionError(text)

    def assertIsNot(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if a is b:
            text = f"{a!r} is {b!r}" if msg is None else f"{a!r} is {b!r}: {msg._value}"
            raise AssertionError(text)

    def assertIsNone(self, x: Any, msg: Str | None = None) -> None:
        from poop.types.none import NoneClass as _NoneClass

        if x is not None and not isinstance(x, _NoneClass):
            text = (
                f"{x!r} is not None"
                if msg is None
                else f"{x!r} is not None: {msg._value}"
            )
            raise AssertionError(text)

    def assertIsNotNone(self, x: Any, msg: Str | None = None) -> None:
        from poop.types.none import NoneClass as _NoneClass

        if x is None or isinstance(x, _NoneClass):
            text = "is None" if msg is None else f"is None: {msg._value}"
            raise AssertionError(text)

    def assertIsInstance(self, x: Any, cls: type, msg: Str | None = None) -> None:
        if not isinstance(x, cls):
            text = (
                f"{x!r} not isinstance {cls.__name__}"
                if msg is None
                else f"{x!r} not isinstance {cls.__name__}: {msg._value}"
            )
            raise AssertionError(text)

    def assertNotIsInstance(self, x: Any, cls: type, msg: Str | None = None) -> None:
        if isinstance(x, cls):
            text = (
                f"{x!r} isinstance {cls.__name__}"
                if msg is None
                else f"{x!r} isinstance {cls.__name__}: {msg._value}"
            )
            raise AssertionError(text)

    def assertGreater(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if not (_unwrap(a) > _unwrap(b)):
            text = (
                f"{a!r} not > {b!r}"
                if msg is None
                else f"{a!r} not > {b!r}: {msg._value}"
            )
            raise AssertionError(text)

    def assertGreaterEqual(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if not (_unwrap(a) >= _unwrap(b)):
            text = (
                f"{a!r} not >= {b!r}"
                if msg is None
                else f"{a!r} not >= {b!r}: {msg._value}"
            )
            raise AssertionError(text)

    def assertLess(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if not (_unwrap(a) < _unwrap(b)):
            text = (
                f"{a!r} not < {b!r}"
                if msg is None
                else f"{a!r} not < {b!r}: {msg._value}"
            )
            raise AssertionError(text)

    def assertLessEqual(self, a: Any, b: Any, msg: Str | None = None) -> None:
        if not (_unwrap(a) <= _unwrap(b)):
            text = (
                f"{a!r} not <= {b!r}"
                if msg is None
                else f"{a!r} not <= {b!r}: {msg._value}"
            )
            raise AssertionError(text)

    def assertAlmostEqual(
        self, a: Any, b: Any, places: Int | None = None, msg: Str | None = None
    ) -> None:
        p = 7 if places is None else places._value
        if round(abs(_unwrap(a) - _unwrap(b)), p) != 0:
            text = (
                f"{a!r} != {b!r} within {p} places"
                if msg is None
                else f"{a!r} != {b!r} within {p} places: {msg._value}"
            )
            raise AssertionError(text)

    def assertRaises(
        self,
        exc: type[BaseException],
        callable_: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            callable_(*args, **kwargs)
        except exc:
            return
        raise AssertionError(f"{exc.__name__} not raised")

    def fail(self, msg: Str | None = None) -> None:
        raise AssertionError("fail" if msg is None else msg._value)

    def skipTest(self, reason: Str) -> None:
        raise _unittest.SkipTest(reason._value)

    def run_method(self, method_name: Str) -> TestResult:
        """Run the named `test_*` method and return a POOP TestResult."""
        # Build a TestCase wrapping `self`'s subclass method into a real
        # unittest.TestCase so we can leverage Python's runner.
        outer = self

        class _Wrapper(_unittest.TestCase):
            def setUp(self) -> None:
                outer.setUp()

            def tearDown(self) -> None:
                outer.tearDown()

            def runTest(self) -> None:
                getattr(outer, method_name._value)()

        result = _unittest.TestResult()
        _Wrapper("runTest").run(result)
        return TestResult(result)


class TestSuite(Object):
    """Wraps Python's `unittest.TestSuite`."""

    __slots__ = ("_tests",)
    __test__ = False  # pytest: not a test class

    def __init__(self) -> None:
        self._tests: list[tuple[TestCase, Str]] = []

    def addTest(self, test: TestCase, method_name: Str) -> NoneClass:
        self._tests.append((test, method_name))
        return none

    def countTestCases(self) -> Int:
        return Int(len(self._tests))

    def run(self) -> TestResult:
        result = _unittest.TestResult()
        for case, name in self._tests:
            outer = case
            method_name = name

            class _Wrapper(_unittest.TestCase):
                def setUp(self) -> None:
                    outer.setUp()

                def tearDown(self) -> None:
                    outer.tearDown()

                def runTest(self) -> None:
                    getattr(outer, method_name._value)()

            _Wrapper("runTest").run(result)
        return TestResult(result)


class TestRunner(Object):
    """A POOP-friendly wrapper around `unittest.TextTestRunner` (silent)."""

    __slots__ = ()
    __test__ = False  # pytest: not a test class

    def run(self, suite: TestSuite) -> TestResult:
        return suite.run()


class UnitTest:
    """Namespace mirroring Python's `unittest` module."""

    TestCase: ClassVar[type[TestCase]] = TestCase
    TestSuite: ClassVar[type[TestSuite]] = TestSuite
    TestRunner: ClassVar[type[TestRunner]] = TestRunner
    TestResult: ClassVar[type[TestResult]] = TestResult
    SkipTest: ClassVar[type[BaseException]] = _unittest.SkipTest

    @staticmethod
    def skip(reason: Str) -> Any:
        return _unittest.skip(reason._value)

    @staticmethod
    def skipIf(condition: Any, reason: Str) -> Any:
        return _unittest.skipIf(bool(condition), reason._value)

    @staticmethod
    def skipUnless(condition: Any, reason: Str) -> Any:
        return _unittest.skipUnless(bool(condition), reason._value)

    @staticmethod
    def expectedFailure(test_item: Any) -> Any:
        return _unittest.expectedFailure(test_item)
