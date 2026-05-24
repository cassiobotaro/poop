"""
Interpreter — model a grammar as a tree of objects that evaluate themselves

A tiny arithmetic language: a `Num` is a leaf, `Add`/`Sub`/`Mul` are
nodes holding two sub-expressions. Each node answers `interpret` by
combining the results of its children. Building the tree is writing the
program; sending `interpret` is running it.

Compare with the procedural Python version, a single function
switching on a tag:

    def interpret(node):
        if node["op"] == "num":
            return node["value"]
        elif node["op"] == "add":
            return interpret(node["left"]) + interpret(node["right"])
        ...

POOP forbids that switch. Every grammar rule is its own class and
knows how to evaluate itself; the tree dispatches recursively with no
central dispatcher.

Smalltalk:
    Num>>interpret ^value
    Add>>interpret ^left interpret + right interpret
    Sub>>interpret ^left interpret - right interpret
    Mul>>interpret ^left interpret * right interpret
"""


class Num:
    def __init__(self, value):
        self._value = value

    def interpret(self):
        return self._value


class Add:
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def interpret(self):
        return self._left.interpret() + self._right.interpret()


class Sub:
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def interpret(self):
        return self._left.interpret() - self._right.interpret()


class Mul:
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def interpret(self):
        return self._left.interpret() * self._right.interpret()


# (1 + 2) * (10 - 4)  ==  18
expression = Mul(Add(Num(1), Num(2)), Sub(Num(10), Num(4)))
("(1 + 2) * (10 - 4) = " + expression.interpret().repr()).print()
