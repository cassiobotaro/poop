import pytest

from poop.types.block import Block
from poop.types.boolean import false, true
from poop.types.exceptions import MIRRORS
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


def test_block_class_answers_function() -> None:
    # A block is a wrapped lambda; CPython's class for a lambda is `function`,
    # so class_name() must answer that, not the internal wrapper name `Block`.
    b = Block(lambda: None)
    assert str(b.class_name()) == "function"
    assert Block.__module__ == "builtins"
    assert repr(Block) == repr(type(lambda: 0))


def test_block_arity_mismatch_speaks_block_vocabulary() -> None:
    # CPython reported this against the raw lambda: `<lambda>() takes 1
    # positional argument but 2 were given` — the Python name of an object
    # POOP cloaks as `function`, and a calling convention a block has not.
    with pytest.raises(TypeError, match=r"^block expects 1 argument, got 2$"):
        Block(lambda x: x)(Int(1), Int(2))


def test_block_arity_message_pluralises_the_expected_count() -> None:
    with pytest.raises(TypeError, match=r"^block expects 0 arguments, got 1$"):
        Block(lambda: none)(Int(1))


def test_block_arity_message_states_a_range_for_optional_arguments() -> None:
    with pytest.raises(TypeError, match=r"^block expects 1 to 2 arguments, got 3$"):
        Block(lambda a, b=none: a)(Int(1), Int(2), Int(3))


def test_block_arity_message_states_a_floor_for_a_variadic_block() -> None:
    with pytest.raises(TypeError, match=r"^block expects at least 1 argument, got 0$"):
        Block(lambda a, *rest: a)()


def test_block_arity_message_counts_keyword_arguments_too() -> None:
    with pytest.raises(TypeError, match=r"^block expects 1 argument, got 2$"):
        Block(lambda x: x)(Int(1), y=Int(2))


def test_block_arity_message_without_a_signature_states_no_count() -> None:
    # A few CPython builtins carry no signature at all, and `get_attr` wraps
    # whatever it is handed; the message must still be a block's.
    with pytest.raises(TypeError, match=r"^block does not accept 3 arguments$"):
        Block({}.update)(Int(1), Int(2), Int(3))


def test_block_does_not_reword_a_type_error_from_its_body() -> None:
    # The body's failure belongs to whatever the body was doing. Distinguished
    # by the traceback: a signature mismatch never enters the block.
    with pytest.raises(TypeError, match="unsupported operand"):
        Block(lambda x: x + "a")(Int(1))


def test_block_error_is_a_poop_exception_class() -> None:
    with pytest.raises(MIRRORS["TypeError"]):
        Block(lambda x: x)()


def test_while_true_rewords_a_wrong_arity_condition() -> None:
    with pytest.raises(TypeError, match=r"^block expects 1 argument, got 0$"):
        Block(lambda x: x).while_true(Block(lambda: none))


def test_while_false_rewords_a_wrong_arity_condition() -> None:
    with pytest.raises(TypeError, match=r"^block expects 1 argument, got 0$"):
        Block(lambda x: x).while_false(Block(lambda: none))
