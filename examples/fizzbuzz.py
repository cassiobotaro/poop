"""
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
        (1).to_do(
            100,
            lambda i: (i % 15 == 0).if_true_if_false(
                lambda: Transcript.show("FizzBuzz"),
                lambda: (i % 3 == 0).if_true_if_false(
                    lambda: Transcript.show("Fizz"),
                    lambda: (i % 5 == 0).if_true_if_false(
                        lambda: Transcript.show("Buzz"),
                        lambda: Transcript.show(i),
                    ),
                ),
            ),
        )


FizzBuzz().run()
