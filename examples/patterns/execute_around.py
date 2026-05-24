"""
Execute Around Method — sandwich a block between guaranteed setup and teardown

`Transaction.perform(block)` always prints BEGIN first and END last;
in between it runs your block and ends with COMMIT, unless the block
raises, in which case it ROLLBACKs instead. The caller supplies only
the middle — the bracketing is handled once, so it can never be
forgotten or mis-paired.

Compare with the procedural Python version, where every call site
copies the same try/finally scaffolding:

    print("BEGIN")
    try:
        do_work()
        print("COMMIT")
    except ValueError:
        print("ROLLBACK")
    finally:
        print("END")

POOP forbids bare `try`/`finally` (it uses `Try`), and Kent Beck's
Execute Around Method captures that scaffolding in one place. The work
is just a block passed in; the guarantees live in the method around it.

Smalltalk:
    Transaction class>>perform: aBlock
        Transcript showCr: 'BEGIN'.
        [aBlock value. Transcript showCr: 'COMMIT']
            on: Error do: [:e | Transcript showCr: 'ROLLBACK ', e messageText]
            ensure: [Transcript showCr: 'END']
"""


class Account:
    def __init__(self, balance):
        self._balance = balance

    def withdraw(self, amount):
        (amount > self._balance).if_true(
            lambda: ValueError.raise_("insufficient funds")
        )
        self._balance = self._balance - amount
        ("withdrew " + amount.repr() + ", balance " + self._balance.repr()).print()


class Transaction:
    @staticmethod
    def perform(block):
        "BEGIN".print()
        # `finally_` runs the Try and is the end of the chain — calling
        # `.run()` after it would re-execute and raise.
        Try(lambda: Transaction._commit(block)).except_(
            ValueError,
            lambda e: ("ROLLBACK — " + e.message()).print(),
        ).finally_(lambda: "END".print())

    @staticmethod
    def _commit(block):
        block()
        "COMMIT".print()


account = Account(100)

# Happy path: BEGIN, work, COMMIT, END.
Transaction.perform(lambda: account.withdraw(60))

"---".print()

# Failure path: the raise skips COMMIT, ROLLBACK runs, END still fires.
Transaction.perform(lambda: account.withdraw(999))
