from poop.types._sentinel import MISSING, NOT_A_COUNT, Sentinel


def test_a_sentinel_names_itself_rather_than_an_address() -> None:
    assert repr(MISSING) == "<missing>"
    assert repr(NOT_A_COUNT) == "<not_a_count>"


def test_every_marker_is_distinct() -> None:
    # One enum, but distinct members: "argument not given" must never be read
    # as "not a repeat count" or "nothing buffered".
    assert len(set(Sentinel)) == len(Sentinel.__members__)
