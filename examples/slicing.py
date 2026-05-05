"""
Demonstrates Slice as a reusable value object.

Build a Slice once, apply it to any collection via obj.slice(s).
Use indices(length) to inspect the normalized start/stop/step for a given length.
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
