"""
Demonstrates Slice as a reusable value object.

Build a Slice once, apply it to any collection via obj.slice(s).
Use indices(length) to inspect the normalized start/stop/step for a given length.

Smalltalk:
    "Smalltalk has no reusable Slice value object; copyFrom:to: is used inline.
     An Interval (a to: b by: c) is the closest analog. Indices are 1-based."

    #(10 20 30 40 50) copyFrom: 2 to: 4.   "#(20 30 40)"
    'POOP language' copyFrom: 2 to: 4.     "'OOP'"

    (1 to: 6 by: 2) collect:
        [:i | #(0 1 2 3 4 5) at: i].       "#(0 2 4)"
"""


class SliceDemo:
    def run(self):
        window = Slice(1, 4)

        [10, 20, 30, 40, 50].slice(window).print()  # 20 30 40
        "POOP language".slice(window).print()  # OOP

        every_other = Slice(0, 6, 2)
        [0, 1, 2, 3, 4, 5].slice(every_other).print()  # 0 2 4

        window.indices(10).print()  # (1, 4, 1)


SliceDemo().run()
