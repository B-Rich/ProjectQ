# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from fractions import Fraction

from projectq.ops import BasicGate


class PhaseGradientGate(BasicGate):
    def __init__(self, factor):
        BasicGate.__init__(self)
        self.factor = factor

    def phase_angle_in_turns_for(self, register_value, register_size):
        return Fraction(register_value, 1 << register_size) * self.factor

    def get_inverse(self):
        return PhaseGradientGate(-self.factor)

    def __repr__(self):
        if self.factor == 1: return "PhaseGradient"
        return "PhaseGradient**({})".format(repr(self.factor))

    def __str__(self):
        if self.factor == 1: return "PhaseGradient"
        return "PhaseGradient**" + str(self.factor)

    def __pow__(self, power):
        """
        Args:
            power (int|float|fractions.Fraction):
        Returns:
            PhaseGradientGate:
        """
        return PhaseGradientGate(self.factor * power)

    def ascii_register_labels(self):
        if self.factor == 1:
            return ['Grad']
        return ['Grad^' + str(self.factor)]

PhaseGradient = PhaseGradientGate(1)
