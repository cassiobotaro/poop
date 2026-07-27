"""`has_next` — the cursor protocol POOP teaches, on POOP's own iterators.

`examples/patterns/iterator.py` holds up `has_next` / `next` driven by
`while_true` as idiomatic, but its cursor was a hand-written class: no built-in
iterator answered the selector, so the protocol the example taught was the one
thing `[1, 2].iter()` could not do, and driving a built-in with `while_true` ran
it off the end.
"""

from typing import Any

import pytest

from poop.types._peek import _PeekMixin
from poop.types.boolean import false, true
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.string import Str


def _view(name: str) -> Any:
    """One lazy view per shape, all reached the way a program would."""
    xs = List(Int(1), Int(2))
    d = Dict()
    d._data[Str("a")] = Int(1)
    return {
        "iterator": xs.iter(),
        "map": xs.map(lambda v: v),
        "filter": xs.filter(lambda v: true),
        "zip": xs.zip(xs),
        "enumerate": xs.enumerate(),
        "dict_items": d.items().iter(),
    }[name]


_SHAPES = ["iterator", "map", "filter", "zip", "enumerate", "dict_items"]


@pytest.mark.parametrize("shape", _SHAPES)
def test_every_lazy_view_answers_has_next(shape: str) -> None:
    # Uniform on purpose: a protocol only half the iterators answer is the
    # opposite of having one.
    assert _view(shape).has_next() is true


@pytest.mark.parametrize("shape", _SHAPES)
def test_has_next_is_false_once_drained(shape: str) -> None:
    view = _view(shape)
    list(view)
    assert view.has_next() is false


@pytest.mark.parametrize("shape", _SHAPES)
def test_asking_does_not_consume(shape: str) -> None:
    # The buffered element must still arrive: `has_next` is a question.
    view = _view(shape)
    before = len(list(_view(shape)))
    view.has_next()
    assert len(list(view)) == before


@pytest.mark.parametrize("shape", _SHAPES)
def test_next_after_asking_answers_the_buffered_element(shape: str) -> None:
    view = _view(shape)
    expected = _view(shape).next()
    view.has_next()
    assert view.next() == expected


def test_asking_twice_buffers_once() -> None:
    it = List(Int(1), Int(2)).iter()
    assert it.has_next() is true
    assert it.has_next() is true
    assert list(it) == [Int(1), Int(2)]


def test_a_buffered_none_is_not_read_as_an_empty_buffer() -> None:
    # `_UNPEEKED` is its own sentinel rather than `none` for this reason.
    from poop.types.none import none

    it = List(none).iter()
    assert it.has_next() is true
    assert it.next() is none
    assert it.has_next() is false


def test_a_dict_item_iterator_wraps_a_buffered_pair() -> None:
    # It re-wraps raw (k, v) pairs, and must do it after the buffer — a peeked
    # pair delivered raw would be a naked Python tuple in user code.
    d = Dict()
    d._data[Str("a")] = Int(1)
    it = d.items().iter()
    it.has_next()
    assert it.next() == d.items().iter().next()


def test_exhaustion_carries_a_sentence_naming_the_iterator() -> None:
    it = List().iter()
    with pytest.raises(StopIteration, match=r"^list_iterator is exhausted — send"):
        it.next()


def test_the_message_names_has_next_now_that_it_exists() -> None:
    with pytest.raises(StopIteration, match="or ask #has_next"):
        List().iter().next()


def test_the_materialize_hook_is_a_subclass_contract() -> None:
    class _Bare(_PeekMixin):
        __slots__ = ()

    with pytest.raises(NotImplementedError):
        _Bare()._materialize()


def test_a_block_running_off_an_iterator_names_no_generator() -> None:
    # PEP 479 rewrote this into `generator raised StopIteration` — a report
    # about a construct POOP does not have and no_yield bans. The protection
    # PEP 479 provides is kept: the view refuses rather than truncating.
    source = List(Int(1)).iter()
    with pytest.raises(RuntimeError, match=r"^a block ran off the end of an iterator"):
        list(List(Int(1), Int(2)).map(lambda v: source.next()))


def test_a_filter_block_running_off_an_iterator_is_refused_too() -> None:
    source = List(Int(1)).iter()
    with pytest.raises(RuntimeError, match="ask #has_next before #next"):
        list(List(Int(1), Int(2)).filter(lambda v: source.next()))
