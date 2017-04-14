# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import BasicMathGate, NotMergeable


class IncrementGate(BasicMathGate):
    def __init__(self):
        BasicMathGate.__init__(self, lambda x: (x + 1,))

    def get_inverse(self):
        return DecrementGate()

    def get_merged(self, other):
        raise NotMergeable()

    def __repr__(self):
        return "Increment"

    def __str__(self):
        return "Increment"

    def ascii_register_labels(self):
        return ['+1']


class DecrementGate(BasicMathGate):
    def __init__(self):
        BasicMathGate.__init__(self, lambda x: (x - 1,))

    def get_inverse(self):
        return IncrementGate()

    def get_merged(self, other):
        raise NotMergeable()

    def __repr__(self):
        return "Decrement"

    def __str__(self):
        return "Decrement"

    def ascii_register_labels(self):
        return ['−1']

Increment = IncrementGate()
Decrement = DecrementGate()
