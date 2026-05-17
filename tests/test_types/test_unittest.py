import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.none import none
from poop.types.string import Str
from poop.types.unittest import (
    TestCase,
    TestResult,
    TestRunner,
    TestSuite,
    UnitTest,
)


def test_unittest_class_refs() -> None:
    assert UnitTest.TestCase is TestCase
    assert UnitTest.TestSuite is TestSuite
    assert UnitTest.TestRunner is TestRunner
    assert UnitTest.TestResult is TestResult


# --- TestCase assertions ---


def test_assertEqual_pass() -> None:
    TestCase().assertEqual(Int(1), Int(1))


def test_assertEqual_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertEqual(Int(1), Int(2))


def test_assertEqual_with_msg() -> None:
    with pytest.raises(AssertionError, match="custom"):
        TestCase().assertEqual(Int(1), Int(2), Str("custom"))


def test_assertNotEqual_pass() -> None:
    TestCase().assertNotEqual(Int(1), Int(2))


def test_assertNotEqual_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertNotEqual(Int(1), Int(1))


def test_assertNotEqual_with_msg() -> None:
    with pytest.raises(AssertionError, match="custom"):
        TestCase().assertNotEqual(Int(1), Int(1), Str("custom"))


def test_assertTrue_pass() -> None:
    TestCase().assertTrue(true)


def test_assertTrue_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertTrue(false)


def test_assertTrue_with_msg() -> None:
    with pytest.raises(AssertionError, match="reason"):
        TestCase().assertTrue(false, Str("reason"))


def test_assertFalse_pass() -> None:
    TestCase().assertFalse(false)


def test_assertFalse_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertFalse(true)


def test_assertFalse_with_msg() -> None:
    with pytest.raises(AssertionError, match="reason"):
        TestCase().assertFalse(true, Str("reason"))


def test_assertIs_pass() -> None:
    TestCase().assertIs(none, none)


def test_assertIs_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertIs(Int(1), Int(1))


def test_assertIs_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertIs(Int(1), Int(1), Str("hint"))


def test_assertIsNot_pass() -> None:
    TestCase().assertIsNot(Int(1), Int(1))


def test_assertIsNot_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertIsNot(none, none)


def test_assertIsNot_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertIsNot(none, none, Str("hint"))


def test_assertIsNone_pass() -> None:
    TestCase().assertIsNone(none)


def test_assertIsNone_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertIsNone(Int(1))


def test_assertIsNone_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertIsNone(Int(1), Str("hint"))


def test_assertIsNotNone_pass() -> None:
    TestCase().assertIsNotNone(Int(1))


def test_assertIsNotNone_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertIsNotNone(none)


def test_assertIsNotNone_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertIsNotNone(none, Str("hint"))


def test_assertIsInstance_pass() -> None:
    TestCase().assertIsInstance(Int(1), Int)


def test_assertIsInstance_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertIsInstance(Int(1), Str)


def test_assertIsInstance_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertIsInstance(Int(1), Str, Str("hint"))


def test_assertNotIsInstance_pass() -> None:
    TestCase().assertNotIsInstance(Int(1), Str)


def test_assertNotIsInstance_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertNotIsInstance(Int(1), Int)


def test_assertNotIsInstance_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertNotIsInstance(Int(1), Int, Str("hint"))


def test_assertGreater_pass() -> None:
    TestCase().assertGreater(Int(2), Int(1))


def test_assertGreater_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertGreater(Int(1), Int(2))


def test_assertGreater_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertGreater(Int(1), Int(2), Str("hint"))


def test_assertGreaterEqual_pass() -> None:
    TestCase().assertGreaterEqual(Int(1), Int(1))


def test_assertGreaterEqual_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertGreaterEqual(Int(1), Int(2))


def test_assertGreaterEqual_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertGreaterEqual(Int(1), Int(2), Str("hint"))


def test_assertLess_pass() -> None:
    TestCase().assertLess(Int(1), Int(2))


def test_assertLess_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertLess(Int(2), Int(1))


def test_assertLess_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertLess(Int(2), Int(1), Str("hint"))


def test_assertLessEqual_pass() -> None:
    TestCase().assertLessEqual(Int(1), Int(1))


def test_assertLessEqual_fail_raises() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertLessEqual(Int(2), Int(1))


def test_assertLessEqual_with_msg() -> None:
    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertLessEqual(Int(2), Int(1), Str("hint"))


def test_assertAlmostEqual_pass() -> None:
    from poop.types.float import Float

    TestCase().assertAlmostEqual(Float(1.0), Float(1.00000001))


def test_assertAlmostEqual_fail_raises() -> None:
    from poop.types.float import Float

    with pytest.raises(AssertionError):
        TestCase().assertAlmostEqual(Float(1.0), Float(1.5), Int(2))


def test_assertAlmostEqual_with_msg() -> None:
    from poop.types.float import Float

    with pytest.raises(AssertionError, match="hint"):
        TestCase().assertAlmostEqual(Float(1.0), Float(1.5), Int(2), Str("hint"))


def test_assertRaises_pass() -> None:
    def boom() -> None:
        raise ValueError("hi")

    TestCase().assertRaises(ValueError, boom)


def test_assertRaises_fail_raises_assertion() -> None:
    with pytest.raises(AssertionError):
        TestCase().assertRaises(ValueError, lambda: None)


def test_fail_raises_assertion() -> None:
    with pytest.raises(AssertionError):
        TestCase().fail()


def test_fail_with_msg() -> None:
    with pytest.raises(AssertionError, match="custom"):
        TestCase().fail(Str("custom"))


def test_skipTest_raises_skip() -> None:
    with pytest.raises(UnitTest.SkipTest):
        TestCase().skipTest(Str("nope"))


# --- TestSuite + TestRunner + TestResult ---


class _Sample(TestCase):
    def test_ok(self) -> None:
        self.assertEqual(Int(1), Int(1))

    def test_bad(self) -> None:
        self.assertEqual(Int(1), Int(2))


def test_testcase_run_method_ok() -> None:
    result = _Sample().run_method(Str("test_ok"))
    assert isinstance(result, TestResult)
    assert result.wasSuccessful() is true
    assert result.testsRun == Int(1)


def test_testcase_run_method_failure() -> None:
    result = _Sample().run_method(Str("test_bad"))
    assert result.wasSuccessful() is false
    assert result.failure_count() == Int(1)


def test_testsuite_addtest_and_count() -> None:
    s = TestSuite()
    case = _Sample()
    assert s.addTest(case, Str("test_ok")) is none
    assert s.countTestCases() == Int(1)


def test_testsuite_run_all_ok() -> None:
    s = TestSuite()
    s.addTest(_Sample(), Str("test_ok"))
    s.addTest(_Sample(), Str("test_ok"))
    result = s.run()
    assert result.testsRun == Int(2)
    assert result.wasSuccessful() is true


def test_testsuite_run_mixed() -> None:
    s = TestSuite()
    s.addTest(_Sample(), Str("test_ok"))
    s.addTest(_Sample(), Str("test_bad"))
    result = s.run()
    assert result.testsRun == Int(2)
    assert result.wasSuccessful() is false
    assert result.failure_count() == Int(1)


def test_testrunner_runs_suite() -> None:
    runner = TestRunner()
    s = TestSuite()
    s.addTest(_Sample(), Str("test_ok"))
    result = runner.run(s)
    assert isinstance(result, TestResult)


def test_testresult_error_count() -> None:
    class _Boom(TestCase):
        def test_boom(self) -> None:
            raise RuntimeError("boom")

    result = _Boom().run_method(Str("test_boom"))
    assert result.error_count() == Int(1)
    assert result.failure_count() == Int(0)


def test_testresult_skipped_count() -> None:
    class _Skip(TestCase):
        def test_skip(self) -> None:
            self.skipTest(Str("nope"))

    result = _Skip().run_method(Str("test_skip"))
    assert result.skipped_count() == Int(1)


def test_setup_teardown_run() -> None:
    counters: list[str] = []

    class _Hooks(TestCase):
        def setUp(self) -> None:
            counters.append("setup")

        def tearDown(self) -> None:
            counters.append("teardown")

        def test_x(self) -> None:
            counters.append("test")

    _Hooks().run_method(Str("test_x"))
    assert counters == ["setup", "test", "teardown"]


# --- Decorators ---


def test_skip_decorator() -> None:
    skip_dec = UnitTest.skip(Str("not now"))
    assert callable(skip_dec)


def test_skipIf_decorator_truthy() -> None:
    dec = UnitTest.skipIf(true, Str("always"))
    assert callable(dec)


def test_skipUnless_decorator_falsy() -> None:
    dec = UnitTest.skipUnless(false, Str("disabled"))
    assert callable(dec)


def test_expectedFailure_passes_through() -> None:
    def f() -> None:
        pass

    decorated = UnitTest.expectedFailure(f)
    assert callable(decorated)


# --- Interpreter integration ---


def test_unittest_via_interpreter() -> None:
    Interpreter().run_source(
        "class Mine(TestCase):\n"
        "    def test_x(self):\n"
        "        self.assertEqual(1, 1)\n"
        "result = Mine().run_method('test_x')\n"
        "result.wasSuccessful().print()"
    )
