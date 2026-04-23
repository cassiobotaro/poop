"""
An RPN calculator computes expressions written in Reverse Polish Notation.

An RPN expression is either:
  - a number X, whose value is X
  - a sequence E1 E2 OP, where E1 and E2 are RPN expressions and OP is +, -, * or /

Examples:
  20 5 /        =>  20/5   = 4
  4 2 + 3 -     =>  (4+2)-3 = 3
  3 5 8 * 7 + * =>  ((5*8)+7)*3 = 141

Smalltalk:
    | ops rpn |
    ops := Dictionary new.
    ops at: '+' put: [:a :b | a + b].
    ops at: '-' put: [:a :b | a - b].
    ops at: '*' put: [:a :b | a * b].
    ops at: '/' put: [:a :b | a / b].

    rpn := [:expression |
        | stack |
        stack := OrderedCollection new.
        expression substrings do: [:token |
            (ops includesKey: token)
                ifTrue: [
                    | b a |
                    b := stack removeLast.
                    a := stack removeLast.
                    stack addLast: ((ops at: token) value: a value: b)]
                ifFalse: [
                    stack addLast: token asInteger]].
        stack last].

    Transcript showCr: (rpn value: '20 5 /') printString.
    Transcript showCr: (rpn value: '4 2 + 3 -') printString.
    Transcript showCr: (rpn value: '3 5 8 * 7 + *') printString.
"""


class RPN:
    def evaluate(self, expression):
        ops = {
            "+": lambda a, b: a + b,
            "-": lambda a, b: a - b,
            "*": lambda a, b: a * b,
            "/": lambda a, b: a / b,
        }
        stack = []
        expression.split().do(
            lambda token: ops.includes_key(token).if_true_if_false(
                lambda: self._apply(ops, token, stack),
                lambda: stack.add(int(token)),
            )
        )
        return stack.last()

    def _apply(self, ops, operator, stack):
        b = stack.pop()
        a = stack.pop()
        stack.add(ops.at(operator)(a, b))


RPN().evaluate("20 5 /").print()
RPN().evaluate("4 2 + 3 -").print()
RPN().evaluate("3 5 8 * 7 + *").print()
