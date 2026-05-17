"""
Visitor — adding operations without modifying the nodes

Each tree node (`Leaf`, `Branch`) exposes a single `.accept(visitor)`
method. Different operations are different Visitor subclasses; the
nodes themselves never change. A `SumVisitor`, `MaxVisitor`, and
`PrintVisitor` walk the same tree without a single `isinstance`
check.

Compare with the procedural Python version:

    def max_value(node):
        if isinstance(node, Leaf):
            return node.value
        return max(max_value(node.left), max_value(node.right))

POOP forbids `isinstance`. Double dispatch carries the type
information without inspection: `node.accept(visitor)` lets the node
pick `visit_leaf` vs `visit_branch`, then the visitor runs. Want a
new operation? Just add a new Visitor — Leaf and Branch don't move.

Smalltalk:
    Object subclass: #Leaf
        instanceVariableNames: 'value'.
    Leaf>>accept: visitor ^visitor visitLeaf: self

    Object subclass: #Branch
        instanceVariableNames: 'left right'.
    Branch>>accept: visitor ^visitor visitBranch: self

    Object subclass: #SumVisitor.
    SumVisitor>>visitLeaf: leaf ^leaf value
    SumVisitor>>visitBranch: branch
        ^(branch left accept: self) + (branch right accept: self)
"""


class Leaf:
    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value

    def accept(self, visitor):
        return visitor.visit_leaf(self)


class Branch:
    def __init__(self, left, right):
        self._left = left
        self._right = right

    def left(self):
        return self._left

    def right(self):
        return self._right

    def accept(self, visitor):
        return visitor.visit_branch(self)


class SumVisitor:
    def visit_leaf(self, leaf):
        return leaf.value()

    def visit_branch(self, branch):
        return branch.left().accept(self) + branch.right().accept(self)


class MaxVisitor:
    def visit_leaf(self, leaf):
        return leaf.value()

    def visit_branch(self, branch):
        return branch.left().accept(self).max(branch.right().accept(self))


class PrintVisitor:
    def __init__(self):
        self._depth = 0

    def _pad(self):
        return "  " * self._depth

    def visit_leaf(self, leaf):
        return self._pad() + "Leaf(" + leaf.value().repr() + ")"

    def visit_branch(self, branch):
        head = self._pad() + "Branch"
        self._depth = self._depth + 1
        left = branch.left().accept(self)
        right = branch.right().accept(self)
        self._depth = self._depth - 1
        return head + "\n" + left + "\n" + right


tree = Branch(
    Leaf(1),
    Branch(
        Leaf(2),
        Branch(Leaf(3), Leaf(4)),
    ),
)

("sum: " + tree.accept(SumVisitor()).repr()).print()
("max: " + tree.accept(MaxVisitor()).repr()).print()
"---".print()
tree.accept(PrintVisitor()).print()
