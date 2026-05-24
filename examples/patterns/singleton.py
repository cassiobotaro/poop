"""
Singleton — one shared instance reached through the class itself

`Settings.instance()` always answers the same object. The first call
builds it; later calls find it already there and hand it back. Because
every caller shares one instance, a value written through one
reference is visible through the next.

Compare with the procedural Python version:

    _settings = None
    def settings():
        global _settings
        if _settings is None:
            _settings = Settings()
        return _settings

POOP forbids `global`, `is`, and the `if`. The "build once" decision
becomes `if_none`: a real instance answers it with itself, a `none`
answers it by running the block.

Smalltalk (class-side cached instance):
    Settings class>>instance
        ^Instance ifNil: [Instance := self new]

    Settings>>at: aKey put: aValue
        values at: aKey put: aValue. ^self
"""


class Settings:
    _instance = None

    @classmethod
    def instance(cls):
        cls._instance = cls._instance.if_none(lambda: cls())
        return cls._instance

    def __init__(self):
        self._values = {}

    def set(self, key, value):
        self._values.at_put(key, value)
        return self

    def get(self, key):
        return self._values.get(key)


# One caller writes through the singleton...
Settings.instance().set("theme", "dark")

# ...another caller, reaching the same instance, sees the value.
("theme = " + Settings.instance().get("theme")).print()
