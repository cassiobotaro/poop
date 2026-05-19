from poop.types.block import Block
from poop.types.boolean import false, true
from poop.types.int import Int
from poop.types.none import none


def test_block_is_callable() -> None:
    b = Block(lambda: Int(42))
    assert b() == Int(42)


def test_block_callable_with_args() -> None:
    b = Block(lambda x: x + Int(1))
    assert b(Int(5)) == Int(6)


def test_block_while_true_executes_body() -> None:
    results: list[int] = []
    x = [Int(0)]

    def cond() -> object:
        return x[0] < Int(3)

    def body() -> None:
        results.append(int(x[0]._value))
        x[0] = x[0] + Int(1)  # ty: ignore[invalid-assignment]

    Block(cond).while_true(Block(body))
    assert results == [0, 1, 2]


def test_block_while_true_returns_none() -> None:
    result = Block(lambda: false).while_true(Block(lambda: None))
    assert result is none


def test_block_while_false_executes_body() -> None:
    results: list[int] = []
    x = [Int(0)]

    def cond() -> object:
        return x[0] < Int(3)

    def body() -> None:
        results.append(int(x[0]._value))
        x[0] = x[0] + Int(1)  # ty: ignore[invalid-assignment]

    Block(cond).while_false(Block(body))
    assert results == []


def test_block_while_false_executes_while_condition_false() -> None:
    called: list[int] = []
    x = [false]

    def body() -> None:
        called.append(1)
        x[0] = true

    Block(lambda: x[0]).while_false(Block(body))
    assert called == [1]


def test_block_while_false_returns_none() -> None:
    result = Block(lambda: true).while_false(Block(lambda: None))
    assert result is none


def test_block_str_hides_class_name() -> None:
    b = Block(lambda: None)
    assert str(b) == "<block>"
    assert "Block" not in str(b)
    assert "lambda" not in str(b)
