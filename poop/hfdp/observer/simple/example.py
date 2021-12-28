from poop.hfdp.observer.simple.simple_observer import SimpleObserver
from poop.hfdp.observer.simple.simple_subject import SimpleSubject


def main() -> None:
    simple_subject = SimpleSubject()
    simple_observer = SimpleObserver(simple_subject)
    simple_subject.set_value(80)
    simple_subject.remove_observer(simple_observer)
