# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from ..gates import Increment, OffsetGate


def do_naive_offset(gate, target_reg, controls):
    """
    Args:
        gate (OffsetGate):
            The gate being applied (contains offset info).
        target_reg (projectq.types.Qureg):
            The destination register, whose value is increased by the offset
            (with wraparound).
        controls (list[Qubit]):
            Control qubits.
    """
    offset = gate.offset % (1 << len(target_reg))
    for i in range(len(target_reg)):
        if (offset >> i) & 1:
            Increment & controls | target_reg[i:]


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=OffsetGate,
        gate_decomposer=lambda cmd: do_naive_offset(
            gate=cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits)),
]
