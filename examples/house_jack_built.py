"""
The House that Jack Built — refactored with composition

The classic nursery rhyme renders best when each "thing" in the
cumulative chain is a small value object and the verses are built
by composing them, rather than by a procedural method with a case
statement (Sandi Metz's go-to teaching refactor of cumulative tales).

Three classes carry the load:

- `Phrase`  — a value object pairing a subject (Str) with the verb
  that links it to the *previous* phrase in the chain.
- `Verse`   — receives a List of Phrases (focus first, then the
  cumulative chain) and renders the verse text.
- `House`   — composes the canonical 12 phrases; knows how to render
  any verse and to recite the first N verses.

`Random.randint(Int(1), Int(12))` picks how many verses to recite
in tonight's performance, demonstrating the Random namespace.

Smalltalk:
    | rng count house |
    rng := Random new.
    count := rng nextIntegerBetween: 1 and: 12.
    house := House canonical.
    1 to: count do: [:i | Transcript showCr: (house verse: i) render].
"""


class Phrase:
    def __init__(self, subject, verb):
        self._subject = subject
        self._verb = verb

    def subject(self):
        return self._subject

    def verb(self):
        return self._verb


class Verse:
    def __init__(self, phrases):
        # phrases[0] is the focus (most recent thing introduced);
        # phrases[1..] are the prior chain in reverse-introduction order.
        self._phrases = phrases

    def render(self):
        focus = self._phrases.at(0)
        head = "This is " + focus.subject()
        rest = self._phrases.slice(1, self._phrases.len()).reduce(
            "",
            lambda acc, phrase: acc + " that " + phrase.verb() + " " + phrase.subject(),
        )
        return head + rest + "."


class House:
    def __init__(self, phrases):
        self._phrases = phrases

    @classmethod
    def canonical(cls):
        return cls(
            list(
                Phrase("the house that Jack built", "lay in"),
                Phrase("the malt", "ate"),
                Phrase("the rat", "killed"),
                Phrase("the cat", "worried"),
                Phrase("the dog", "tossed"),
                Phrase("the cow with the crumpled horn", "milked"),
                Phrase("the maiden all forlorn", "kissed"),
                Phrase("the man all tattered and torn", "married"),
                Phrase("the priest all shaven and shorn", "woke"),
                Phrase("the rooster that crowed in the morn", "kept"),
                Phrase("the farmer sowing his corn", "belonged to"),
                Phrase("the horse and the hound and the horn", "lived in"),
            )
        )

    def size(self):
        return self._phrases.len()

    def verse(self, n):
        # Verse n uses the first n phrases. Focus is the n-th (most
        # recent), chain is verse 1..n-1 in reverse.
        return Verse(self._phrases.slice(0, n).reversed())

    def recite(self, count):
        range(1, count + 1).do(lambda i: self.verse(i).render().print())


count = Random.randint(1, 12)
("Tonight: " + count.repr() + " verses").print()
House.canonical().recite(count)
