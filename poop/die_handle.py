from poop.die import Die


class DieHandle:
    def __init__(self):
        self.dice = []

    def add_die(self, a_die):
        self.dice.append(a_die)

    def dice_number(self):
        return len(self.dice)

    def roll(self):
        return sum(die.roll() for die in self.dice)

    def max_value(self):
        return sum(die.faces for die in self.dice)

    def __add__(self, other):
        if not isinstance(other, DieHandle):
            return NotImplemented

        new_handle = DieHandle()
        for die in self.dice:
            new_handle.add_die(die)

        for die in other.dice:
            new_handle.add_die(die)

        return new_handle

    def __mul__(self, other):
        if not isinstance(other, int):
            return NotImplemented

        new_handle = DieHandle()
        for _ in range(other):
            for die in self.dice:
                new_handle.add_die(die)

        return new_handle

    __rmul__ = __mul__


def D(a_number):
    handle = DieHandle()
    handle.add_die(Die.with_faces(a_number))
    return handle


D10 = D(10)
D12 = D(12)
D20 = D(20)
D4 = D(4)
D6 = D(6)
D8 = D(8)


# Amaldiçoando os inteiros para criar DieHandles diretamente
# Seu uso seria algo como: 3.D6 para criar um DieHandle com três D6


# def D10(self):
#     return self.D(10)
#
#
# def D12(self):
#     return self.D(12)
#
#
# def D20(self):
#     return self.D(20)
#
#
# def D4(self):
#     return self.D(4)
#
#
# def D6(self):
#     return self.D(6)
#
#
# def D8(self):
#     return self.D(8)
#
#
# def D(self, a_number):
#     handle = DieHandle()
#     for _ in range(self):
#         handle.add_die(Die.with_faces(a_number))
#     return handle
#
#
# curse(int, "D", D)
# curse(int, "D10", property(D10))
# curse(int, "D12", property(D12))
# curse(int, "D20", property(D20))
# curse(int, "D4", property(D4))
# curse(int, "D6", property(D6))
# curse(int, "D8", property(D8))
