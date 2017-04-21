# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import SelfInverseGate, NotMergeable
from ..extensions import BasicMathGate2


class MultiNotGate(BasicMathGate2, SelfInverseGate):
    def do_operation(self, x):
        return ~x,

    def __repr__(self):
        return "MultiNot"

    def __str__(self):
        return "MultiNot"

    def ascii_register_labels(self):
        return ['⊕']

    def ascii_borders(self):
        return False

MultiNot = MultiNotGate()
