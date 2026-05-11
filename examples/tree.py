"""
Binary Tree — polymorphism replacing isinstance

Two node shapes — Leaf and Branch — answer the same messages (`sum`,
`depth`, `count_leaves`). The caller never asks "what kind of node is
this?"; it sends the message and the receiver decides. Recursion
cascades naturally: Branch dispatches to its children, which dispatch
to theirs, until Leaves bottom out.

Compare with the procedural Python version:

    def sum(node):
        if isinstance(node, Leaf):
            return node.value
        return sum(node.left) + sum(node.right)

POOP forbids `isinstance` because the node already knows what it is.

Smalltalk:
    Object subclass: #Leaf
        instanceVariableNames: 'value'.

    Leaf>>sum
        ^value

    Leaf>>depth
        ^0

    Leaf>>countLeaves
        ^1

    Object subclass: #Branch
        instanceVariableNames: 'left right'.

    Branch>>sum
        ^left sum + right sum

    Branch>>depth
        ^1 + ((left depth) max: (right depth))

    Branch>>countLeaves
        ^left countLeaves + right countLeaves
"""


class Leaf:
    def __init__(self, value):
        self._value = value

    def sum(self):
        return self._value

    def depth(self):
        return 0

    def count_leaves(self):
        return 1


class Branch:
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def sum(self):
        return self._left.sum() + self._right.sum()

    def depth(self):
        return self._left.depth().max(self._right.depth()) + 1

    def count_leaves(self):
        return self._left.count_leaves() + self._right.count_leaves()


tree = Branch(
    Leaf(1),
    Branch(
        Leaf(2),
        Branch(Leaf(3), Leaf(4)),
    ),
)

("sum:    " + tree.sum().repr()).print()
("depth:  " + tree.depth().repr()).print()
("leaves: " + tree.count_leaves().repr()).print()
