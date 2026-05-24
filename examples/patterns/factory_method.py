"""
Factory Method — subclasses decide which product to instantiate

A `Dialog` knows how to render itself, but defers *which* button to
build to its subclasses. `WindowsDialog` makes a `WindowsButton`,
`WebDialog` makes an `HTMLButton`. The base class calls
`self.create_button()` without ever naming a concrete product.

Compare with the procedural Python version:

    def make_button(kind):
        if kind == "windows":
            return WindowsButton()
        elif kind == "web":
            return HTMLButton()

POOP forbids that branching. Each Creator subclass owns the choice of
product; the caller picks a Creator and the right product follows by
dispatch.

Smalltalk:
    Dialog>>render
        ^'Dialog: ', self createButton render

    WindowsDialog>>createButton ^WindowsButton new
    WebDialog>>createButton    ^HTMLButton new
"""


class WindowsButton:
    def render(self):
        return "[ Windows OK ]"


class HTMLButton:
    def render(self):
        return "<button>OK</button>"


class Dialog:
    def render(self):
        return "Dialog: " + self.create_button().render()


class WindowsDialog(Dialog):
    def create_button(self):
        return WindowsButton()


class WebDialog(Dialog):
    def create_button(self):
        return HTMLButton()


[WindowsDialog(), WebDialog()].do(lambda dialog: dialog.render().print())
