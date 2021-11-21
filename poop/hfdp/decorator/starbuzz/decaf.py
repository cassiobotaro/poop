from poop.hfdp.decorator.starbuzz.beverage import Beverage


class Decaf(Beverage):
    def __init__(self) -> None:
        super().__init__()
        self.description = "Decaf Coffee"

    def cost(self) -> float:
        return 1.05
