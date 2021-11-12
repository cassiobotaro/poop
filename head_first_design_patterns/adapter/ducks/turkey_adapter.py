from head_first_design_patterns.adapter.ducks.turkey import Turkey


class TurkeyAdapter:
    def __init__(self, turkey: Turkey) -> None:
        self.turkey = turkey

    def quack(self) -> None:
        self.turkey.gobble()

    def fly(self) -> None:
        for i in range(5):
            self.turkey.fly()
