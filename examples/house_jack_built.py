"""
The House that Jack Built — Sandi Metz refactor

Port of Sandi Metz's canonical refactor of the cumulative tale.
The procedural verse-building method becomes a `House` with two
injected strategies: an *orderer* that decides the sequence of
phrases, and a *formatter* that decides how each verse's parts are
rendered. The default strategies reproduce the standard nursery
rhyme; swapping in alternates produces other performances without
touching House itself.

  - DefaultOrder      / RandomOrder      — sequence strategies
  - DefaultFormatter  / EchoFormatter    — rendering strategies

`RandomOrder` uses `Random.sample(coll, coll.len())` — the Python
idiom for a non-mutating shuffle.

Smalltalk:
    | house |
    house := House new
        orderer:   RandomOrder new;
        formatter: EchoFormatter new;
        yourself.
    Transcript show: house recite.
"""


class DefaultFormatter:
    def format(self, parts):
        return parts


class EchoFormatter:
    def format(self, parts):
        # parts.zip(parts).flatten — each part appears twice
        return parts.map(lambda p: [p, p]).reduce([], lambda acc, pair: acc + pair)


class DefaultOrder:
    def order(self, data):
        return data


class RandomOrder:
    def order(self, data):
        # Non-mutating shuffle: Random.sample(coll, k=len(coll)) is the
        # Python idiom (Random.shuffle mutates in-place).
        return Random.sample(data, data.len())


class House:
    DATA = [
        "the horse and the hound and the horn that belonged to",
        "the farmer sowing his corn that kept",
        "the rooster that crowed in the morn that woke",
        "the priest all shaven and shorn that married",
        "the man all tattered and torn that kissed",
        "the maiden all forlorn that milked",
        "the cow with the crumpled horn that tossed",
        "the dog that worried",
        "the cat that killed",
        "the rat that ate",
        "the malt that lay in",
        "the house that Jack built",
    ]

    def __init__(self, orderer=DefaultOrder(), formatter=DefaultFormatter()):
        self._formatter = formatter
        self._data = orderer.order(House.DATA)

    def recite(self):
        verses = list(range(1, self._data.len() + 1).map(lambda i: self.line(i)))
        return "\n".join(verses)

    def line(self, number):
        return "This is " + " ".join(self.parts(number)) + ".\n"

    def parts(self, number):
        # Ruby's data.last(number) — the last N entries of the data list.
        return self._formatter.format(
            self._data.slice(self._data.len() - number, self._data.len())
        )


House().recite().print()
