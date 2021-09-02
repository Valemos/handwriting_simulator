from unittest import TestCase

from handwriting.misc.step_functions import *


class TestCyclicSteps(TestCase):

    def test_cycle_forwards(self):
        desired = [0, 1, 2, 0, 1, 2, 0]

        it = 0
        for i in range(7):
            self.assertEqual(it, desired[i])
            it = step_forwards(it, 2)

    def test_cycle_backwards(self):
        desired = [0, 2, 1, 0, 2, 1, 0]

        it = 0
        for i in range(7):
            self.assertEqual(it, desired[i])
            it = step_backwards(it, 2)
