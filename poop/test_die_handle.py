import unittest

from poop.die import Die
from poop.die_handle import DieHandle


class TestDieHandle(unittest.TestCase):
    def test_creating_and_adding(self):
        handle = DieHandle()
        handle.add_die(Die.with_faces(6))
        handle.add_die(Die.with_faces(10))
        self.assertEqual(handle.dice_number(), 2)

    def test_creating_with_the_same_dice(self):
        handle = DieHandle()
        handle.add_die(Die.with_faces(6))
        self.assertEqual(handle.dice_number(), 1)
        handle.add_die(Die.with_faces(6))
        self.assertEqual(handle.dice_number(), 2)

    def test_max_value(self):
        handle = DieHandle()
        handle.add_die(Die.with_faces(6))
        handle.add_die(Die.with_faces(10))
        self.assertEqual(handle.max_value(), 16)

    def test_roll(self):
        handle = DieHandle()
        handle.add_die(Die.with_faces(6))
        handle.add_die(Die.with_faces(10))

        for _ in range(10):
            res = handle.roll()
            self.assertTrue(handle.dice_number() <= res <= handle.max_value())

    def test_sample_handle(self):
        self.assertEqual((2).D20.dice_number(), 2)

    def test_summing(self):
        self.assertEqual(((3).D4 + (2).D6).dice_number(), 5)
