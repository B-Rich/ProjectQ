# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import BasicMathGate, NotMergeable


class MultiNotGate(BasicMathGate):
    def __init__(self):
        BasicMathGate.__init__(self, lambda x: (~x,))

    def get_merged(self, other):
        raise NotMergeable()

    def __repr__(self):
        return "MultiNot"

    def __str__(self):
        return "MultiNot"

    def ascii_register_labels(self):
        return ['⊕']

    def ascii_borders(self):
        return False

MultiNot = MultiNotGate()
