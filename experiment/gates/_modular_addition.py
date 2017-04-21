# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..extensions import BasicMathGate2


class ModularAdditionGate(BasicMathGate2):
    def __init__(self, modulus):
        BasicMathGate2.__init__(self)
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return x, (y + x) % self.modulus

    def get_inverse(self):
        return ModularSubtractionGate(self.modulus)

    def __repr__(self):
        return 'ModularAdditionGate(modulus=' + self.modulus + ')'

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '+A (mod {})'.format(self.modulus)]


class ModularSubtractionGate(BasicMathGate2):
    def __init__(self, modulus):
        BasicMathGate2.__init__(self)
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return x, (y - x) % self.modulus

    def get_inverse(self):
        return ModularAdditionGate(self.modulus)

    def __repr__(self):
        return 'ModularSubtractionGate(modulus=' + self.modulus + ')'

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return ['A', '−A (mod {})'.format(self.modulus)]
