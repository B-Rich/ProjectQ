# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ._modular_bimultiplication import multiplicative_inverse
from ..extensions import BasicMathGate2


class ModularDoubleGate(BasicMathGate2):
    def __init__(self, modulus):
        if modulus % 2 == 0:
            raise ValueError(
                'Doubling is irreversible modulo {}.'.format(modulus))
        BasicMathGate2.__init__(self)
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return x * 2 % self.modulus,

    def get_inverse(self):
        return ModularUndoubleGate(self.modulus)

    def __repr__(self):
        return 'ModularDoubleGate({})'.format(repr(self.modulus))

    def __str__(self):
        return '×2 % {}'.format(self.modulus)


class ModularUndoubleGate(BasicMathGate2):
    def __init__(self, modulus):
        if modulus % 2 == 0:
            raise ValueError("Undoubling is irreversible modulo even values.")
        BasicMathGate2.__init__(self)
        self.modulus = modulus

    def do_operation(self, x):
        if x >= self.modulus:
            return x,
        return x * multiplicative_inverse(2, self.modulus) % self.modulus,

    def get_inverse(self):
        return ModularDoubleGate(self.modulus)

    def __repr__(self):
        return 'ModularUndoubleGate({})'.format(repr(self.modulus))

    def __str__(self):
        return '÷2 % {}'.format(self.modulus)
