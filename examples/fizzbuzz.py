"""
FizzBuzz

Prints numbers 1–100, replacing multiples of 3 with Fizz, multiples of
5 with Buzz, and multiples of both with FizzBuzz.
Demonstrates range().do() and nested if_true_if_false.

Smalltalk:
    1 to: 100 do: [:i |
        (i \\ 15 = 0)
            ifTrue: [ Transcript show: 'FizzBuzz' ]
            ifFalse: [
                (i \\ 3 = 0)
                    ifTrue: [ Transcript show: 'Fizz' ]
                    ifFalse: [
                        (i \\ 5 = 0)
                            ifTrue: [ Transcript show: 'Buzz' ]
                            ifFalse: [ Transcript show: i printString ]
                    ]
            ]
    ].
"""


class FizzBuzz:
    def run(self) -> None:
        range(1, 101).do(
            lambda i: (i % 15 == 0).if_true_if_false(
                lambda: "FizzBuzz".print(),
                lambda: (i % 3 == 0).if_true_if_false(
                    lambda: "Fizz".print(),
                    lambda: (i % 5 == 0).if_true_if_false(
                        lambda: "Buzz".print(),
                        lambda: i.print(),
                    ),
                ),
            ),
        )


FizzBuzz().run()
