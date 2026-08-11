import pytest

from poop.types.block import Block
from poop.types.boolean import false, true
from poop.types.exceptions import MIRRORS
from poop.types.int import Int
from poop.types.none import none
from poop.types.string import Str


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


def test_block_on_a_class_binds_to_the_receiver() -> None:
    # `set_attr` on a class is sanctioned so a program can extend the classes
    # it defines, and the one thing a reader reaches for it with did not work:
    # the block was stored as a plain class attribute and read back untouched,
    # so a one-argument block was told it got none.
    from poop.types.object import Object
    from poop.types.string import Str

    class C(Object):
        __slots__ = ()

    C.set_attr(Str("greet"), Block(lambda self: Str("hi")))
    assert C().greet() == Str("hi")  # ty: ignore[unresolved-attribute]


def test_block_on_a_class_passes_further_arguments_after_the_receiver() -> None:
    from poop.types.object import Object
    from poop.types.string import Str

    class C(Object):
        __slots__ = ()

    C.set_attr(Str("add"), Block(lambda self, n: n + Int(1)))
    assert C().add(Int(4)) == Int(5)  # ty: ignore[unresolved-attribute]


def test_block_read_off_the_class_is_unbound() -> None:
    # As a function is: `C.greet` answers the block itself, `C().greet` binds.
    from poop.types.object import Object
    from poop.types.string import Str

    class C(Object):
        __slots__ = ()

    block = Block(lambda self: Str("hi"))
    C.set_attr(Str("greet"), block)
    assert C.greet is block  # ty: ignore[unresolved-attribute]


def test_block_held_as_instance_state_is_not_bound() -> None:
    # Only `__get__` is defined, which makes this a *non-data* descriptor —
    # Python's own split, so a block found in the instance's `__dict__` is
    # handed back as itself. That half already worked and must keep working.
    from poop.types.object import Object
    from poop.types.string import Str

    class C(Object):
        pass

    c = C()
    c.set_attr(Str("callback"), Block(lambda: Str("state")))
    assert c.callback() == Str("state")  # ty: ignore[unresolved-attribute]


def test_a_zero_argument_block_on_a_class_is_told_it_got_the_receiver() -> None:
    # Binding is Python's rule, so this now fails — and it must fail in the
    # block's own words, counting the receiver it was handed rather than
    # degrading to "does not accept 0 arguments" about a call that passed none.
    from poop.types.object import Object
    from poop.types.string import Str

    class C(Object):
        __slots__ = ()

    C.set_attr(Str("greet"), Block(lambda: Str("hi")))
    with pytest.raises(TypeError, match=r"block expects 0 arguments, got 1"):
        C().greet()  # ty: ignore[unresolved-attribute]


def test_a_bound_block_does_not_reword_a_type_error_from_its_body() -> None:
    from poop.types.object import Object
    from poop.types.string import Str

    class C(Object):
        __slots__ = ()

    C.set_attr(Str("boom"), Block(lambda self: "a" + 1))  # ty: ignore[unsupported-operator]
    with pytest.raises(TypeError, match=r"can only concatenate str"):
        C().boom()  # ty: ignore[unresolved-attribute]


def test_a_method_read_off_an_object_is_a_block() -> None:
    # `_as_block` was wired into `get_attr`, the spelling almost nobody
    # writes; the one everybody writes stayed native, so `"abc".upper.print()`
    # answered `'function' object has no attribute 'print'` — CPython's word
    # for a message, naming the value `function`, which is `Block`'s own
    # cloak. Same object, same message, two answers.
    from poop.types.string import Str

    assert repr(Str("abc").upper) == "<block>"
    assert Str("abc").upper.callable() is true  # ty: ignore[unresolved-attribute]
    assert Str("abc").upper() == Str("ABC")


def test_a_method_read_by_name_and_by_writing_it_agree() -> None:
    from poop.types.string import Str

    assert repr(Str("abc").get_attr(Str("upper"))) == repr(Str("abc").upper)


def test_a_bound_method_still_works_as_a_block_value() -> None:
    from poop.types.list import List
    from poop.types.object import Object

    class C(Object):
        __slots__ = ()

        def double(self, v: Int) -> Int:
            return v * Int(2)  # ty: ignore[invalid-return-type]

    assert list(List(Int(1), Int(2)).map(C().double)) == [Int(2), Int(4)]


def test_a_method_keeps_cpythons_arity_wording_not_the_blocks() -> None:
    # `cloak` has already worded a method's wrong-arity failure for a
    # *message*; rewording it as a block's would replace `str.upper` with the
    # word `block`, and would drag `inspect.signature` — which evaluates a
    # wrapper's `TYPE_CHECKING`-only annotations — into every failed call.
    from poop.types.string import Str

    with pytest.raises(TypeError, match=r"str\.upper\(\) takes 1 positional"):
        Str("abc").upper(Int(1))  # ty: ignore[too-many-positional-arguments]


def test_a_private_name_is_not_wrapped() -> None:
    # `is_message` already calls `_` the boundary of the message surface, and
    # `Block` holds its callable in `_fn` — wrapping that read would hand
    # `__call__` a fresh block to unwrap on every call, forever.
    from types import MethodType

    from poop.types.string import Str

    assert type(Str("abc")._value) is str
    assert type(Block(lambda: none)._fn) is not MethodType


# Proposal 43. `Object` compares by identity and `__getattribute__` builds a
# fresh wrapper on every read, so the same method on the same receiver was not
# equal to itself. CPython's bound method compares by `__self__` and `__func__`
# precisely so a program can ask "is this the same callback?".
def test_a_method_read_twice_is_equal_to_itself() -> None:
    text = Str("abc")
    assert text.upper == text.upper


def test_a_method_read_twice_hashes_the_same() -> None:
    text = Str("abc")
    assert text.upper.hash() == text.upper.hash()  # ty: ignore[unresolved-attribute]
    assert hash(text.upper) == hash(text.upper)


def test_two_different_methods_on_one_receiver_are_not_equal() -> None:
    text = Str("abc")
    assert not bool(text.upper == text.lower)


def test_one_method_on_two_receivers_is_not_equal() -> None:
    assert not bool(Str("abc").upper == Str("abd").upper)


def test_a_method_is_not_equal_to_a_non_block() -> None:
    assert not bool(Str("abc").upper == Int(5))


def test_not_equal_is_the_negation() -> None:
    text = Str("abc")
    assert not bool(text.upper != text.upper)
    assert bool(text.upper != text.lower)


def test_a_registry_stops_registering_the_same_method_twice() -> None:
    # The shape a reader actually hits: storing `obj.on_change` and later
    # asking whether it is already registered answered no, every time.
    text = Str("abc")
    registry = {text.upper}
    registry.add(text.upper)
    assert len(registry) == 1


def test_is_identical_still_answers_false() -> None:
    # Unchanged and honest: those really are two objects, which INFECTIONS.md
    # already documents as a deliberate disagreement for classes.
    text = Str("abc")
    assert text.upper.is_identical(text.upper) is false  # ty: ignore[unresolved-attribute]


def test_a_block_literal_keeps_identity_equality() -> None:
    # `Block` wraps a lambda, and two lambdas with the same body are different
    # blocks in Smalltalk as in Python — so the change is on `_MethodBlock`.
    one = Block(lambda: 1)
    assert one == one
    assert not bool(one == Block(lambda: 1))
