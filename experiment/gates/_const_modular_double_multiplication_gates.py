# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import BasicMathGate2, NotMergeable


class ConstModularDoubleMultiplicationGate(BasicMathGate2):
    def __init__(self, factor, modulus):
        inverse_factor = _multiplicative_inverse(factor, modulus)
        if inverse_factor is None:
            raise ValueError("Irreversible.")

        BasicMathGate2.__init__(self)
        self.factor = factor
        self.inverse_factor = inverse_factor
        self.modulus = modulus

    def do_operation(self, x, y):
        if x >= self.modulus or y >= self.modulus:
            return x, y
        return ((x * self.factor) % self.modulus,
                (y * -self.inverse_factor) % self.modulus)

    def get_inverse(self):
        return ConstModularDoubleMultiplicationGate(
            self.inverse_factor,
            self.modulus)

    def get_merged(self, other):
        raise NotMergeable()

    def __repr__(self):
        return 'ConstModularDoubleMultiplication({}, modulus={})'.format(
            self.factor, self.modulus)

    def __str__(self):
        return repr(self)

    def ascii_register_labels(self):
        return [
            '×{} (mod {})'.format(self.factor, self.modulus),
            '×{} (mod {})'.format(self.inverse_factor, self.modulus)
        ]


def _extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = _extended_gcd(b % a, a)
    return g, x - (b // a) * y, y


def _multiplicative_inverse(a, m):
    g, x, y = _extended_gcd(a, m)
    return None if g != 1 else x % m
