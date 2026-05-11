"""
The House That Jack Built — recursive composition (Sandi Metz)

From Sandi Metz's RailsConf 2015 talk *Nothing Is Something*. The
nursery rhyme has a natural recursive shape: every line is the same
template (`This is the X.`), where X grows by chaining onto the
previous line's phrase. Sandi's refactor: each line is an object that
knows its own subject and its predecessor — `text` is dispatched
polymorphically between the base case and the recursive case.

Compare with the procedural Python version:

    DATA = ["house that Jack built", "malt that lay in", ...]
    for i in range(len(DATA)):
        parts = DATA[: i + 1][::-1]
        print("This is the " + " the ".join(parts) + ".")

POOP forbids loops, comprehensions, and subscripts — and even if it
didn't, the procedural shape ties indices to data. Two classes and one
recursive call replace the whole machine.

Smalltalk:
    BaseLine>>text
        ^phrase

    Line>>text
        ^phrase , ' the ' , predecessor text

    BaseLine>>recite
        ^'This is the ' , self text , '.'

    Line>>recite
        ^'This is the ' , self text , '.'
"""


class BaseLine:
    def __init__(self, phrase):
        self._phrase = phrase

    def text(self):
        return self._phrase

    def recite(self):
        return "This is the " + self.text() + "."


class Line:
    def __init__(self, phrase, predecessor):
        self._phrase = phrase
        self._predecessor = predecessor

    def text(self):
        return self._phrase + " the " + self._predecessor.text()

    def recite(self):
        return "This is the " + self.text() + "."


house = BaseLine("house that Jack built")
malt = Line("malt that lay in", house)
rat = Line("rat that ate", malt)
cat = Line("cat that killed", rat)
dog = Line("dog that worried", cat)
cow = Line("cow with the crumpled horn that tossed", dog)

[house, malt, rat, cat, dog, cow].do(lambda line: line.recite().print())
