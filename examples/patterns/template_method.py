"""
Template Method — the superclass orchestrates, subclasses fill the blanks

`Report.render()` is the skeleton: build header, body, footer, join.
Subclasses (`MarkdownReport`, `HTMLReport`, `PlainReport`) override
only the formatting hooks. The caller asks for `.render()` and never
has to know which flavour answered.

Compare with the procedural Python version:

    def render(kind, title, rows):
        match kind:
            case "markdown":
                return f"# {title}\n" + "\n".join(f"- {r}" for r in rows)
            case "html":
                return f"<h1>{title}</h1>\n<ul>...</ul>"
            case "plain":
                return title.upper() + "\n" + "\n".join(rows)

POOP forbids `match` and `for`-comprehensions. The shape lives in the
abstract class; each concrete report supplies its own pieces. The
caller dispatches on the receiver, not on a tag.

Smalltalk:
    Object subclass: #Report
        instanceVariableNames: 'title rows'.
    Report>>render
        ^String streamContents: [:s |
            s nextPutAll: self header; cr.
            s nextPutAll: self body; cr.
            s nextPutAll: self footer]
    Report>>header
        ^self subclassResponsibility
    Report>>body
        ^self subclassResponsibility
    Report>>footer
        ^self subclassResponsibility

    Report subclass: #MarkdownReport.
    MarkdownReport>>header ^'# ', title
    MarkdownReport>>body ^...
"""


class Report:
    def __init__(self, title, rows):
        self._title = title
        self._rows = rows

    def render(self):
        return "\n".join([self.header(), self.body(), self.footer()])

    def header(self):
        return self.subclass_responsibility()

    def body(self):
        return self.subclass_responsibility()

    def footer(self):
        return self.subclass_responsibility()


class MarkdownReport(Report):
    def header(self):
        return "# " + self._title

    def body(self):
        return "\n".join(self._rows.map(lambda r: "- " + r))

    def footer(self):
        return "_rendered by POOP_"


class HTMLReport(Report):
    def header(self):
        return "<h1>" + self._title + "</h1>"

    def body(self):
        items = "\n".join(self._rows.map(lambda r: "  <li>" + r + "</li>"))
        return "<ul>\n" + items + "\n</ul>"

    def footer(self):
        return "<p>rendered by POOP</p>"


class PlainReport(Report):
    def header(self):
        return self._title.upper()

    def body(self):
        return "\n".join(self._rows.map(lambda r: "  * " + r))

    def footer(self):
        return "--"


rows = ["apples", "oranges", "bananas"]

[
    MarkdownReport("Shopping list", rows),
    HTMLReport("Shopping list", rows),
    PlainReport("Shopping list", rows),
].do(lambda report: (report.render() + "\n").print())
