from poop.hfdp.adapter.ducks.turkey import Turkey


class TurkeyAdapter:
    def __init__(self, turkey: Turkey) -> None:
        self.__turkey = turkey

    def quack(self) -> None:
        self.__turkey.gobble()

    def fly(self) -> None:
        for i in range(5):
            self.__turkey.fly()
