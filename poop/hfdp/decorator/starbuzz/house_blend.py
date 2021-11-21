from poop.hfdp.decorator.starbuzz.beverage import Beverage


class HouseBlend(Beverage):
    def __init__(self) -> None:
        super().__init__()
        self.description = "House Blend Coffee"

    def cost(self) -> float:
        return 0.89
