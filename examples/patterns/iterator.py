"""
Iterator — walk a collection without exposing how it is stored

A `Playlist` keeps its songs privately and hands out a
`PlaylistIterator` that exposes only `has_next` and `next`. The caller
walks the songs through that cursor and never touches the underlying
list — swap the storage and the traversal code is unchanged.

Compare with the procedural Python version, which reaches straight
into the structure with an index:

    i = 0
    while i < len(playlist.songs):
        play(playlist.songs[i])
        i += 1

POOP forbids `while`, `len`, and `[]` indexing. The iterator object
holds the cursor; a `while_true` block drives it by sending
`has_next`/`next`, so the loop variable lives inside the iterator, not
the caller.

Smalltalk:
    PlaylistIterator>>hasNext ^position < songs size
    PlaylistIterator>>next
        | song | song := songs at: position.
        position := position + 1. ^song

    [iterator hasNext] whileTrue: [Transcript showCr: iterator next]

The pattern is about a *custom* cursor over storage a caller must not
see. POOP's own iterators answer the same two messages, so the same
loop drives `["a", "b"].iter()` directly:

    it = ["Imagine", "Hey Jude"].iter()
    (lambda: it.has_next()).while_true(lambda: it.next().print())

Write `PlaylistIterator` when the traversal is yours to define — a
tree walk, a filtered view, a paged fetch — not to re-implement `iter`.
"""


class Playlist:
    def __init__(self, songs):
        self._songs = songs

    def iterator(self):
        return PlaylistIterator(self._songs)


class PlaylistIterator:
    def __init__(self, songs):
        self._songs = songs
        self._position = 0

    def has_next(self):
        return self._position < self._songs.len()

    def next(self):
        song = self._songs.at(self._position)
        self._position = self._position + 1
        return song


playlist = Playlist(["Imagine", "Hey Jude", "Yesterday"])
cursor = playlist.iterator()

(lambda: cursor.has_next()).while_true(lambda: cursor.next().print())

# The same loop, driven by a built-in iterator: `iter()` answers the very
# protocol `PlaylistIterator` implements by hand.
"---".print()
songs = ["Come Together", "Something"].iter()
(lambda: songs.has_next()).while_true(lambda: songs.next().print())
