import random


class Die:
    def __init__(self, faces=6):
        super().__init__()
        self.faces = faces

    def roll(self):
        return random.randint(1, self.faces)

    @classmethod
    def with_faces(cls, an_integer):
        return cls(an_integer)

    def __repr__(self):
        return f"Die({self.faces})"
