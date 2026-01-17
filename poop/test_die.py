import unittest

from die import Die


class TestDie(unittest.TestCase):
    def test_creation_is_ok(self):
        d = Die.with_faces(20)
        self.assertEqual(d.faces, 20)

    def test_initialization_is_ok(self):
        d = Die()
        self.assertEqual(d.faces, 6)

    def test_rolling(self):
        d = Die()
        for _ in range(100):
            self.assertIn(d.roll(), range(1, 7))
