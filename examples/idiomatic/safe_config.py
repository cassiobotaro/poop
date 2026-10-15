"""
Safe config lookup — the paired null test, and a chained fallback

`Dict.get(missing_key)` returns `none` (Smalltalk's `nil`), not a
KeyError. `if_not_none_if_none(present_block, none_block)` branches on
it in one message — the present block receives the value, the other
runs when it is absent — and `if_none(block)` alone gives a fallback to
whatever a block answered. Each step keeps the same shape: object
responds to messages, even when "object" is `none`.

Compare with the procedural Python version:

    db = config.get("database")
    if db is None:
        return "localhost"
    host = db.get("host")
    if host is None:
        return "localhost"
    return host

POOP forbids `is None` against polymorphic types — `none` is itself a
NoneClass instance answering `if_none`/`if_not_none` like any other
object. No branch, no special case.

Smalltalk (nil-aware ifNotNil: / ifNil:):
    | host |
    host := (config at: 'database')
        ifNotNil: [:db | db at: 'host']
        ifNil:    ['localhost'].
"""


class ConfigReader:
    def __init__(self, config):
        self._config = config

    def database_host(self, default):
        return self._config.get("database").if_not_none_if_none(
            lambda db: db.get("host").if_none(lambda: default),
            lambda: default,
        )


full = {"database": {"host": "db.example.com", "port": 5432}}
missing_host = {"database": {"port": 5432}}
missing_db = {"server": {"workers": 4}}

ConfigReader(full).database_host("localhost").print()
ConfigReader(missing_host).database_host("localhost").print()
ConfigReader(missing_db).database_host("localhost").print()
