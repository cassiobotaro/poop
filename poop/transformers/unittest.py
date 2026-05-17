from poop.types.unittest import (
    TestCase,
    TestResult,
    TestRunner,
    TestSuite,
    UnitTest,
)

NAMESPACE: dict[str, object] = {
    "unittest": UnitTest,
    "TestCase": TestCase,
    "TestSuite": TestSuite,
    "TestRunner": TestRunner,
    "TestResult": TestResult,
}
