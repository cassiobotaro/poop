"""
Bank Account

A BankAccount raises ValueError when a withdrawal exceeds the balance.
Try(block).except_(ExcType, handler).run() replaces try/except.
Error.message() and Error.kind() inspect the wrapped exception.

Smalltalk:
    | account |
    account := BankAccount new.
    account deposit: 100.

    [account withdraw: 150]
        on: ValueError
        do: [:e | Transcript showCr: 'Error [', e class name, ']: ', e messageText].

    Transcript showCr: account balance printString.

    account deposit: 200.
    account withdraw: 50.

    Transcript showCr: account balance printString.
"""


class BankAccount:
    def __init__(self):
        self._balance = 0

    def deposit(self, amount):
        self._balance = self._balance + amount
        return self

    def withdraw(self, amount):
        (self._balance >= amount).if_false(
            lambda: ValueError.raise_("Insufficient funds")
        )
        self._balance = self._balance - amount
        return self

    def balance(self):
        return self._balance


account = BankAccount()
account.deposit(100)

Try(lambda: account.withdraw(150)).except_(
    ValueError,
    lambda e: ("Error [" + e.kind() + "]: " + e.message()).print(),
).run()

account.balance().print()

account.deposit(200)
account.withdraw(50)
account.balance().print()
