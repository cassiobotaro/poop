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
        (1).to_(100).do(
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
