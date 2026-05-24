"""
Flyweight — share the heavy, intrinsic state across many objects

A forest holds thousands of trees, but a tree's *type* (its name and
colour) repeats endlessly. `TreeType` is the flyweight: the shared,
unchanging part. `TreeFactory` hands out one `TreeType` per unique
combination, so four trees of two kinds reference only two type
objects. Each `Tree` keeps just its own position — the extrinsic
state.

Compare with the procedural Python version, where every tree carries a
full copy of its type:

    trees.append({"name": "oak", "color": "green", "x": 1, "y": 1})
    trees.append({"name": "oak", "color": "green", "x": 2, "y": 3})

POOP shares the repeated part through the factory's cache. `if_none`
turns "create it only the first time" into a message, not a branch.

Smalltalk:
    TreeFactory class>>name: aName color: aColor
        ^Types at: aName , '/' , aColor
            ifAbsentPut: [TreeType name: aName color: aColor]
"""


class TreeType:
    def __init__(self, name, color):
        self._name = name
        self._color = color

    def draw(self, x, y):
        return (
            self._color + " " + self._name + " at (" + x.repr() + ", " + y.repr() + ")"
        )


class TreeFactory:
    _types = {}

    @classmethod
    def of(cls, name, color):
        key = name + "/" + color
        return cls._types.get(key).if_none(lambda: cls._store(key, name, color))

    @classmethod
    def _store(cls, key, name, color):
        created = TreeType(name, color)
        cls._types.at_put(key, created)
        return created

    @classmethod
    def kinds(cls):
        return cls._types.len()


class Tree:
    def __init__(self, x, y, tree_type):
        self._x = x
        self._y = y
        self._type = tree_type

    def draw(self):
        return self._type.draw(self._x, self._y)


forest = [
    Tree(1, 1, TreeFactory.of("oak", "green")),
    Tree(2, 3, TreeFactory.of("oak", "green")),
    Tree(5, 2, TreeFactory.of("pine", "dark green")),
    Tree(8, 8, TreeFactory.of("oak", "green")),
]

forest.do(lambda tree: tree.draw().print())

# Four trees, but only the distinct types were ever built.
("shared TreeType objects: " + TreeFactory.kinds().repr()).print()
