"""
Iterating a string, which is a collection like any other.

`for` is banned, so a string answers the same protocol every other
collection does: `do`, `map`, `filter`, `all`, `any`, `enumerate`, `zip`.
`find`, `count` and `index` keep their string meaning — they search for a
substring rather than for a match.

Smalltalk:
    'poop' do: [:each | Transcript show: each; cr].

    ('poop' collect: [:each | each asUppercase]) displayNl.

    ('hello' select: [:each | 'aeiou' includes: each]) displayNl.

    ('poop' allSatisfy: [:each | each isVowel]) displayNl.

    'abc' doWithIndex: [:each :i | Transcript showCr: i printString, each].
"""


class Word:
    def __init__(self, text):
        self.text = text

    def shout(self):
        return self.text.map(lambda letter: letter.upper())

    def vowels(self):
        return self.text.filter(lambda letter: "aeiou".includes(letter))

    def is_all_letters(self):
        return self.text.all(lambda letter: letter.isalpha())

    def numbered(self):
        return self.text.enumerate(1)


word = Word("poop")

word.text.do(lambda letter: letter.print(end=" "))
"".print()

word.shout().do(lambda letter: letter.print(end=" "))
"".print()

word.vowels().do(lambda letter: letter.print(end=" "))
"".print()

word.is_all_letters().print()

word.numbered().do(lambda pair: pair.print(sep=": "))

"poop".zip("word").do(lambda pair: pair.print(sep="-"))
