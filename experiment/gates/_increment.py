# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..extensions import BasicMathGate2


class IncrementGate(BasicMathGate2):
    def do_operation(self, x):
        return x + 1,

    def get_inverse(self):
        return DecrementGate()

    def __repr__(self):
        return "Increment"

    def __str__(self):
        return "Increment"

    def ascii_register_labels(self):
        return ['+1']


class DecrementGate(BasicMathGate2):
    def do_operation(self, x):
        return x - 1,

    def get_inverse(self):
        return IncrementGate()

    def __repr__(self):
        return "Decrement"

    def __str__(self):
        return "Decrement"

    def ascii_register_labels(self):
        return ['−1']


Increment = IncrementGate()
Decrement = DecrementGate()
