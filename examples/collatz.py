"""
Collatz Sequence

Starting from a positive integer, repeatedly apply:
  - divide by 2 if even
  - multiply by 3 and add 1 if odd
The sequence always reaches 1 (Collatz conjecture).

Demonstrates while_true with mutable state via instance variables —
the idiomatic POOP substitute for a while loop.

Smalltalk:
    Object subclass: #Collatz
        instanceVariableNames: 'n steps'

    Collatz >> init: start
        n := start.
        steps := 0.
        ^self

    Collatz >> step
        n printNl.
        n := n even
            ifTrue: [ n // 2 ]
            ifFalse: [ n * 3 + 1 ].
        steps := steps + 1

    Collatz >> run
        [ n > 1 ] whileTrue: [ self step ].
        n printNl.
        Transcript showCr: 'Steps: ' , steps printString.
"""


class Collatz:
    def __init__(self, n):
        self._n = n
        self._steps = 0

    def _step(self):
        self._n.print()
        self._n = (self._n % 2 == 0).if_true_if_false(
            lambda: self._n // 2,
            lambda: self._n * 3 + 1,
        )
        self._steps = self._steps + 1

    def run(self):
        (lambda: self._n > 1).while_true(lambda: self._step())
        self._n.print()
        ("Steps: " + self._steps.repr()).print()


Collatz(27).run()
