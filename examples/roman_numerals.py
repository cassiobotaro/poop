"""
Roman Numerals

Converts integers to Roman numeral strings.

Smalltalk:
    Object subclass: #RomanNumerals

    RomanNumerals >> convert: n
        | pairs |
        pairs := OrderedCollection withAll: #(
            #(1000 'M') #(900 'CM') #(500 'D') #(400 'CD')
            #(100 'C') #(90 'XC') #(50 'L') #(40 'XL')
            #(10 'X') #(9 'IX') #(5 'V') #(4 'IV') #(1 'I')
        ).
        ^ (pairs
            inject: (Association key: n value: '')
            into: [:acc :pair |
                | count |
                count := acc key // pair first.
                Association
                    key: acc key \\ pair first
                    value: acc value , (pair last repeat: count)
            ]) value
"""


class RomanNumerals:
    def _step(self, acc, pair):
        count = acc.at(0) // pair.at(0)
        return (acc.at(0) % pair.at(0), acc.at(1) + pair.at(1) * count)

    def convert(self, number):
        pairs = [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I"),
        ]
        return pairs.reduce((number, ""), self._step).at(1)


RomanNumerals().convert(1).print()
RomanNumerals().convert(10).print()
RomanNumerals().convert(7).print()
RomanNumerals().convert(1990).print()
RomanNumerals().convert(2008).print()
RomanNumerals().convert(3999).print()
