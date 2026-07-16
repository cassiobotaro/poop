"""
Prototype — new objects made by cloning a configured example

A `Bestiary` keeps pre-built monsters and answers `spawn` by cloning
one of them. The call site never names a constructor: it asks the
registry for a copy of an existing example. Each `Monster` knows how
to `clone` itself, copying its mutable state so the fresh object and
its prototype never share a list.

Compare with the procedural Python version:

    def spawn(kind):
        if kind == "goblin":
            return Monster("Goblin", 30, ["scratch"])
        elif kind == "dragon":
            return Monster("Dragon", 500, ["bite", "fire breath"])

POOP forbids that branching factory. The examples live in the registry;
new instances come from `clone`, not from re-listing every constructor.

Smalltalk (objects answer `copy` — Prototype is built into the language):
    Object subclass: #Monster
        instanceVariableNames: 'name hp abilities'.
    Monster>>clone
        ^self copy setAbilities: abilities copy

    Bestiary>>spawn: aKey
        ^(prototypes at: aKey) clone
"""


class Monster:
    def __init__(self, name, hp, abilities):
        self._name = name
        self._hp = hp
        self._abilities = abilities

    def clone(self):
        return Monster(self._name, self._hp, self._abilities.copy())

    def rename(self, name):
        self._name = name
        return self

    def learn(self, ability):
        self._abilities.append(ability)
        return self

    def describe(self):
        return (
            self._name + " (" + self._hp.repr() + " hp): " + ", ".join(self._abilities)
        )


class Bestiary:
    def __init__(self):
        self._prototypes = {}

    def register(self, key, prototype):
        self._prototypes.at_put(key, prototype)
        return self

    def spawn(self, key):
        return self._prototypes.get(key).clone()


bestiary = (
    Bestiary()
    .register("goblin", Monster("Goblin", 30, ["scratch"]))
    .register("dragon", Monster("Dragon", 500, ["bite", "fire breath"]))
)

# Spawning clones a prototype — no constructor at the call site.
bestiary.spawn("goblin").describe().print()
bestiary.spawn("dragon").describe().print()

# A clone can be customised without disturbing the prototype it came from.
bestiary.spawn("goblin").rename("Goblin King").learn("summon").describe().print()

# The prototype is untouched — the next goblin is plain again.
bestiary.spawn("goblin").describe().print()
