"""
Abstract Factory — families of products that belong together

A `Theme` factory produces a matching `Button` and `Checkbox`.
`LightTheme` yields light widgets, `DarkTheme` yields dark ones. The
`Form` asks its theme for parts and gets a coherent set — it never
mixes a light button with a dark checkbox, because it never names a
concrete widget class.

Compare with the procedural Python version:

    if theme == "dark":
        button = DarkButton()
        checkbox = DarkCheckbox()
    else:
        button = LightButton()
        checkbox = LightCheckbox()

POOP forbids that branching. The factory object encapsulates the whole
family; swap the factory and every part changes together.

Smalltalk:
    LightTheme>>button   ^LightButton new
    LightTheme>>checkbox ^LightCheckbox new

    DarkTheme>>button    ^DarkButton new
    DarkTheme>>checkbox  ^DarkCheckbox new

    Form>>render
        ^{ theme button render. theme checkbox render }
"""


class LightButton:
    def render(self):
        return "[ OK ] (light)"


class DarkButton:
    def render(self):
        return "[ OK ] (dark)"


class LightCheckbox:
    def render(self):
        return "[x] (light)"


class DarkCheckbox:
    def render(self):
        return "[x] (dark)"


class LightTheme:
    def button(self):
        return LightButton()

    def checkbox(self):
        return LightCheckbox()


class DarkTheme:
    def button(self):
        return DarkButton()

    def checkbox(self):
        return DarkCheckbox()


class Form:
    def __init__(self, theme):
        self._theme = theme

    def render(self):
        return [self._theme.button().render(), self._theme.checkbox().render()]


[LightTheme(), DarkTheme()].do(
    lambda theme: Form(theme).render().do(lambda part: part.print())
)
