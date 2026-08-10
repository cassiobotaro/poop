"""
Managed Resource

`With(lambda: manager).do(block)` is POOP's substitute for `with ... as`.
The manager answers `__enter__` and `__exit__` — the one protocol a POOP
program implements with dunders — and `__exit__` receives POOP values:
the exception's class, an error that answers `message()`, and `none` where
Python would pass a traceback. Answering `True` from `__exit__` swallows
the failure, which is how the second run below survives its own division.

Smalltalk:
    | connection |
    connection := Connection open: 'reports'.
    [connection query: 'SELECT 1'] ensure: [connection close].
"""


class Connection:
    def __init__(self, name):
        self.name = name
        self.forgive = False

    def open(self):
        ("opening " + self.name).print()
        return self

    def __enter__(self):
        return self.open()

    def __exit__(self, kind, error, traceback):
        kind.is_none().if_true_if_false(
            lambda: ("closing " + self.name).print(),
            lambda: (
                "closing "
                + self.name
                + " after "
                + kind.name()
                + ": "
                + error.message()
            ).print(),
        )
        return self.forgive

    def query(self, sql):
        return sql + " -> 1 row"

    def forgiving(self):
        self.forgive = True
        return self


With(lambda: Connection("reports")).do(lambda c: c.query("SELECT 1").print())

With(lambda: Connection("ledger").forgiving()).do(lambda c: 1 / 0)

"still running".print()
