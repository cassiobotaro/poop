"""
Prototype — create new objects by cloning a configured instance

Two `Shape` prototypes are configured once. New shapes are made by
cloning a prototype and tweaking only what differs, instead of
re-running a constructor with every attribute spelled out again. The
clone is independent: re-colouring it leaves the prototype untouched.

Compare with the procedural Python version:

    red_square = Shape("square", "red", corners=4)
    blue_square = Shape("square", "blue", corners=4)

POOP leans on `copy.copy`, the same `copy` message Smalltalk sends to
any object. The prototype carries the shared shape; the clone carries
the difference.

Smalltalk:
    Shape>>color: aColor
        color := aColor. ^self

    | square redSquare |
    square := Shape name: 'square' color: 'black' corners: 4.
    redSquare := square copy color: 'red'.
"""


class Shape:
    def __init__(self, name, color, corners):
        self._name = name
        self._color = color
        self._corners = corners

    def color(self, color):
        self._color = color
        return self

    def describe(self):
        return (
            self._color + " " + self._name + " (" + self._corners.repr() + " corners)"
        )


# Prototypes built once, then reused as templates.
square = Shape("square", "black", 4)
triangle = Shape("triangle", "black", 3)

# Clone and customise — corners come for free from the prototype.
copy.copy(square).color("red").describe().print()
copy.copy(triangle).color("blue").describe().print()

# The original prototype is untouched by the clones.
square.describe().print()
