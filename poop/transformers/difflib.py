from poop.types.difflib import Differ, Difflib, HtmlDiff, SequenceMatcher

NAMESPACE: dict[str, object] = {
    "difflib": Difflib,
    "SequenceMatcher": SequenceMatcher,
    "Differ": Differ,
    "HtmlDiff": HtmlDiff,
}
