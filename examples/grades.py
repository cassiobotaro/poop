"""
Grade Book

Filters a list of students by passing score (>= 60) and maps
each to a letter grade (A/B/C/D).

Smalltalk:
    students := #(
        #('Alice' 92) #('Bob' 54) #('Carol' 78)
        #('Dave' 65) #('Eve' 41) #('Frank' 88)
    ).

    passing := students select: [:s | s second >= 60].

    passing
        collect: [:s |
            | grade |
            grade := s second >= 90
                ifTrue: ['A']
                ifFalse: [s second >= 80
                    ifTrue: ['B']
                    ifFalse: [s second >= 70
                        ifTrue: ['C']
                        ifFalse: ['D']]].
            s first , ': ' , grade]
        thenDo: [:line | Transcript showCr: line].
"""


class GradeBook:
    def _letter(self, score):
        return (score >= 90).if_true_if_false(
            lambda: "A",
            lambda: (score >= 80).if_true_if_false(
                lambda: "B",
                lambda: (score >= 70).if_true_if_false(
                    lambda: "C",
                    lambda: "D",
                ),
            ),
        )

    def run(self):
        students = [
            ("Alice", 92),
            ("Bob", 54),
            ("Carol", 78),
            ("Dave", 65),
            ("Eve", 41),
            ("Frank", 88),
        ]

        students.filter(lambda s: s.at(1) >= 60).map(
            lambda s: s.at(0) + ": " + self._letter(s.at(1))
        ).do(lambda line: line.print())


GradeBook().run()
