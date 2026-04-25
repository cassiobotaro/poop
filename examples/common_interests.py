"""
Common Interests

Compares two people's interest sets using set operations.
Demonstrates union / intersection / difference / issubset on Set.

Smalltalk:
    alice := Set withAll: #(python music hiking coffee).
    bob   := Set withAll: #(rust music gaming coffee).

    Transcript showCr: 'Common:'.
    (alice intersection: bob) do: [:x | Transcript showCr: x].

    Transcript showCr: 'Alice only:'.
    (alice difference: bob) do: [:x | Transcript showCr: x].

    Transcript showCr: 'All interests:'.
    (alice union: bob) do: [:x | Transcript showCr: x].
"""


class SocialGraph:
    def _section(self, label, items):
        label.print()
        items.map(lambda x: "  " + x).do(lambda line: line.print())

    def run(self):
        alice = {"python", "music", "hiking", "coffee"}
        bob = {"rust", "music", "gaming", "coffee"}

        self._section("Common interests:", alice.intersection(bob))
        self._section("Alice only:", alice.difference(bob))
        self._section("Bob only:", bob.difference(alice))
        self._section("All interests:", alice.union(bob))

        "Alice is subset of all interests: ".print()
        alice.issubset(alice.union(bob)).print()


SocialGraph().run()
