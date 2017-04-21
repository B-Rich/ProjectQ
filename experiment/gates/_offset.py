# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..extensions import BasicMathGate2


class OffsetGate(BasicMathGate2):
    def __init__(self, offset):
        BasicMathGate2.__init__(self)
        self.offset = offset

    def do_operation(self, x):
        return x + self.offset,

    def get_inverse(self):
        return OffsetGate(-self.offset)

    def __repr__(self):
        return 'OffsetGate({})'.format(self.offset)

    def __str__(self):
        return '{}{}'.format('+' if self.offset >= 0 else '', self.offset)
