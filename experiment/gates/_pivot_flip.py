# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import SelfInverseGate
from ..extensions import BasicMathGate2


class PivotFlipGate(BasicMathGate2, SelfInverseGate):
    def __init__(self):
        SelfInverseGate.__init__(self)
        BasicMathGate2.__init__(self)

    def do_operation(self, pivot, x):
        if x >= pivot:
            return pivot, x
        return pivot, pivot - x - 1

    def __repr__(self):
        return 'PivotFlip'

    def __str__(self):
        return 'Flip<A'

    def ascii_register_labels(self):
        return ['A', 'Flip<A']


class ConstPivotFlipGate(BasicMathGate2, SelfInverseGate):
    def __init__(self, pivot):
        SelfInverseGate.__init__(self)
        BasicMathGate2.__init__(self)
        self.pivot = pivot

    def do_operation(self, x):
        if x >= self.pivot:
            return x,
        return self.pivot - x - 1,

    def __repr__(self):
        return 'ConstPivotFlipGate({})'.format(self.pivot)

    def __str__(self):
        return 'Flip<{}'.format(self.pivot)

PivotFlip = PivotFlipGate()
