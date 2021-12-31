from poop.hfdp.observer.simpleobservable.simple_observer import SimpleOberver
from poop.hfdp.observer.simpleobservable.simple_subject import SimpleSubject


def main() -> None:
    simple_subject = SimpleSubject()
    SimpleOberver(simple_subject)
    simple_subject.set_value(80)
