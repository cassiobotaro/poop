from poop.hfdp.command.diner.cook import Cook


class BurgerAndFriesOrder:
    def __init__(self, cook: Cook) -> None:
        self.cook = cook

    def order_up(self) -> None:
        self.cook.make_burger()
        self.cook.make_fries()
