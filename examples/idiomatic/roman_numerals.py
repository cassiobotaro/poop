"""
Roman Numerals

Converts integers to Roman numeral strings.

Smalltalk:
    Object subclass: #RomanNumerals

    RomanNumerals >> convert: n
        | remainder result |
        remainder := n.
        result := ''.
        #(
            #(1000 'M') #(900 'CM') #(500 'D') #(400 'CD')
            #(100 'C') #(90 'XC') #(50 'L') #(40 'XL')
            #(10 'X') #(9 'IX') #(5 'V') #(4 'IV') #(1 'I')
        ) do: [:pair |
            | count |
            count := remainder // pair first.
            remainder := remainder \\ pair first.
            result := result , (pair last repeat: count).
        ].
        ^ result
"""


class RomanNumerals:
    def convert(self, number):
        self._remainder = number
        self._result = ""
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
        pairs.do(lambda pair: self._absorb(pair))
        return self._result

    def _absorb(self, pair):
        count = self._remainder // pair.at(0)
        self._remainder = self._remainder % pair.at(0)
        self._result = self._result + pair.at(1) * count


RomanNumerals().convert(1).print()
RomanNumerals().convert(10).print()
RomanNumerals().convert(7).print()
RomanNumerals().convert(1990).print()
RomanNumerals().convert(2008).print()
RomanNumerals().convert(3999).print()
