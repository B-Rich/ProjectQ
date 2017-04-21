# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.ops import SelfInverseGate


class ReverseBitsGate(SelfInverseGate):
    def __repr__(self):
        return "ReverseBits"

    def __str__(self):
        return "Reverse"


ReverseBits = ReverseBitsGate()
