# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import BasicMathGate2, NotMergeable


class MultiNotGate(BasicMathGate2):
    def do_operation(self, x):
        return ~x,

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
