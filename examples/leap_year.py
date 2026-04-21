"""
Smalltalk:
    Object subclass: #Year
        instanceVariableNames: 'value'
        classVariableNames: ''
        poolDictionaries: ''
        category: ''

    Year class >> on: aNumber
        ^self new init: aNumber

    Year >> init: aNumber
        value := aNumber.
        ^self

    Year >> isLeap
        ^(value \\ 400 = 0)
            or: [ (value \\ 4 = 0)
                    and: [ (value \\ 100) ~= 0 ] ]

    (Year on: 2000) isLeap.  "true  — divisible by 400"
    (Year on: 1900) isLeap.  "false — divisible by 100 but not 400"
    (Year on: 2008) isLeap.  "true  — divisible by 4 but not 100"
    (Year on: 2017) isLeap.  "false — not divisible by 4"
"""


class Year:
    def __init__(self, value):
        self._value = value

    def is_leap(self):
        return (self._value % 400 == 0).or_(
            lambda: (self._value % 4 == 0).and_(lambda: (self._value % 100 == 0).not_())
        )


Transcript.show(Year(2000).is_leap())  # true  — divisible by 400
Transcript.show(Year(1900).is_leap())  # false — divisible by 100 but not 400
Transcript.show(Year(2008).is_leap())  # true  — divisible by 4 but not 100
Transcript.show(Year(2017).is_leap())  # false — not divisible by 4
