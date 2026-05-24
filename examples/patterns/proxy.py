"""
Proxy — a stand-in that controls access to the real object

Loading an image from disk is expensive, so `ImageProxy` defers it.
It answers the same `.display()` message as `RealImage`, but only
builds the real image the first time it is actually shown — and reuses
it afterwards. The caller talks to the proxy exactly as it would to
the real thing.

Compare with the procedural Python version:

    if self._real is None:
        self._real = RealImage(self._filename)
    return self._real.display()

POOP forbids `is None` for this. The lazy-load becomes `if_none`: the
first call finds `none` and builds the image; later calls find the
real image and return it untouched.

Smalltalk:
    ImageProxy>>display
        real := real ifNil: [RealImage on: filename].
        ^real display
"""


class RealImage:
    def __init__(self, filename):
        self._filename = filename
        ("loaded " + filename + " from disk").print()

    def display(self):
        return "showing " + self._filename


class ImageProxy:
    def __init__(self, filename):
        self._filename = filename
        self._real = None

    def display(self):
        self._real = self._real.if_none(lambda: RealImage(self._filename))
        return self._real.display()


image = ImageProxy("photo.png")
"proxy created — nothing loaded yet".print()

# First display triggers the costly load...
image.display().print()
# ...the second reuses the already-loaded image (no second "loaded" line).
image.display().print()
