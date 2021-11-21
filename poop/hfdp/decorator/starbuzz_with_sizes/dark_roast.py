from poop.hfdp.decorator.starbuzz_with_sizes.beverage import Beverage


class DarkRoast(Beverage):
    def __init__(self) -> None:
        super().__init__()
        self.description = "Dark Roast Coffee"

    def cost(self) -> float:
        return 0.99
