"""
Basic Statistics

Computes sum, mean, min, max and median of the squares 1²…10².
Demonstrates Interval.map() producing a List, then List operations.

Smalltalk:
    data := (1 to: 10) collect: [:i | i * i].

    Transcript showCr: 'Sum:    ' , data sum printString.
    Transcript showCr: 'Mean:   ' , (data sum / data size) printString.
    Transcript showCr: 'Min:    ' , data min printString.
    Transcript showCr: 'Max:    ' , data max printString.
    | sorted mid |
    sorted := data asSortedCollection.
    mid := data size // 2.
    Transcript showCr: 'Median: ' , (sorted at: mid) printString.
"""


class Statistics:
    def _label(self, text, value):
        (text + value.repr()).print()

    def run(self):
        data = (1).to_(10).map(lambda i: i * i)

        sorted_data = data.sorted()

        self._label("Sum:    ", data.sum())
        self._label("Mean:   ", data.sum() / data.len())
        self._label("Min:    ", sorted_data.first())
        self._label("Max:    ", sorted_data.last())
        self._label("Median: ", sorted_data.at(data.len() // 2))


Statistics().run()
