"""
Bank Account

A BankAccount raises ValueError when a withdrawal exceeds the balance.
The caller handles the error gracefully using on_error, reading the
wrapped Error object's message and kind.

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

Note: in POOP, on_error is a method on any POOP object (Object subclass).
Since BankAccount is a plain Python class, True (transformed to the POOP
Boolean singleton) is used as a neutral receiver.
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

True.on_error(
    lambda: account.withdraw(150),
    ValueError,
    lambda e: ("Error [" + e.kind() + "]: " + e.message()).print(),
)

account.balance().print()

account.deposit(200)
account.withdraw(50)
account.balance().print()
