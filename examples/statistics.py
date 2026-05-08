"""
Basic Statistics

Computes sum, mean, min, max and median of the squares 1²…10².
Demonstrates a lazy `range.map()` chain materialized into a List
via `list(...)` so List-only methods (`.sorted()`, `.len()`) work.

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
        data = list(range(1, 11).map(lambda i: i * i))

        sorted_data = data.sorted()

        self._label("Sum:    ", data.sum())
        self._label("Mean:   ", data.sum() / data.len())
        self._label("Min:    ", sorted_data.at(0))
        self._label("Max:    ", sorted_data.at(sorted_data.len() - 1))
        self._label("Median: ", sorted_data.at(data.len() // 2))


Statistics().run()
