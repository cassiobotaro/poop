"""
Deadline

`Async.timeout(delay)` is a deadline, entered with `AsyncWith`: a body that
outlasts it fails with `TimeoutError`. The failure is raised at the await,
so the guard around it is a `Try` that is awaited itself rather than run;
its block answers the coroutine, and its handler answers the fallback.

The connection is an asynchronous context manager of the program's own,
with `async def __aenter__` and `__aexit__`. `AsyncWith` closes it whether
the query finished or the deadline cut it short, and `__aexit__` is told
which: `none` when the query finished, `CancelledError` when the deadline
cancelled it. The timeout then raises its `TimeoutError` from that
cancellation, outside the connection.

Smalltalk:
    | connection |
    connection := Connection open: 'reports'.
    [[connection query: 'SELECT 1']
        valueWithin: 50 milliSeconds
        onTimeout: ['cached']]
            ensure: [connection close].
"""


class Connection(Object):
    def __init__(self, name):
        self.name = name

    async def __aenter__(self):
        ("opening " + self.name).print()
        return self

    async def __aexit__(self, kind, error, traceback):
        kind.is_none().if_true_if_false(
            lambda: ("closing " + self.name).print(),
            lambda: ("closing " + self.name + " after " + kind.name()).print(),
        )

    async def query(self, sql, delay):
        Async.sleep(delay).await_()
        return sql + " -> 1 row"


class Report(Object):
    async def run(self, delay):
        deadline = AsyncWith(lambda: Async.timeout(0.05)).do(
            lambda t: self.queried(delay)
        )
        return Try(lambda: deadline).except_(TimeoutError, lambda e: "cached").await_()

    async def queried(self, delay):
        return (
            AsyncWith(lambda: Connection("reports"))
            .do(lambda connection: connection.query("SELECT 1", delay))
            .await_()
        )


Async.run(Report().run(0.01)).print()
Async.run(Report().run(1)).print()
