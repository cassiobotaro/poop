"""
Chain of Responsibility — pass the request along until someone handles it

An expense report climbs a chain of approvers. Each `Approver` either
signs off (if the amount is within its limit) or forwards the request
to its successor. The sender just hands the amount to the front of the
chain and never learns who ultimately approved it.

Compare with the procedural Python version:

    if amount <= 500:
        return "Team Lead"
    elif amount <= 5000:
        return "Manager"
    else:
        return "Director"

POOP forbids that `elif` ladder. Each link owns one threshold and a
reference to the next link; the decision walks the chain by message,
not by a table the caller has to maintain.

Smalltalk:
    Approver>>approve: amount
        ^amount <= limit
            ifTrue:  [title , ' approves $' , amount printString]
            ifFalse: [successor approve: amount]
"""


class Approver:
    def __init__(self, title, limit, successor):
        self._title = title
        self._limit = limit
        self._successor = successor

    def approve(self, amount):
        return (amount <= self._limit).if_true_if_false(
            lambda: self._title + " approves $" + amount.repr(),
            lambda: self._successor.approve(amount),
        )


# Build the chain from the top down; the Director's limit is high
# enough that it never has to delegate.
director = Approver("Director", 100000, None)
manager = Approver("Manager", 5000, director)
lead = Approver("Team Lead", 500, manager)

[100, 2500, 40000].do(lambda amount: lead.approve(amount).print())
