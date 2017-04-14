# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import BasicMathGate2, NotMergeable


class AdditionGate(BasicMathGate2):
    def do_operation(self, x, y):
        return x, y + x

    def get_inverse(self):
        return SubtractionGate()

    def get_merged(self, other):
        raise NotMergeable()

    def __repr__(self):
        return 'Add'

    def __str__(self):
        return 'Add'

    def ascii_register_labels(self):
        return ['A', '+A']


class SubtractionGate(BasicMathGate2):
    def do_operation(self, x, y):
        return x, y - x

    def get_inverse(self):
        return AdditionGate()

    def get_merged(self, other):
        raise NotMergeable()

    def __repr__(self):
        return 'Subtract'

    def __str__(self):
        return 'Subtract'

    def ascii_register_labels(self):
        return ['A', '−A']


Add = AdditionGate()
Subtract = SubtractionGate()
