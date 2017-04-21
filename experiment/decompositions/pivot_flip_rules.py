# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.ops import X
from ..gates import (
    ConstPivotFlipGate,
    PivotFlipGate,
    OffsetGate,
    Add,
    Subtract,
    MultiNot,
)


def do_pivot_flip(pivot_reg, target_reg, controls, dirty_qubit):
    """
    Args:
        pivot_reg (projectq.types.Qureg):
            The register that determines which target stats get reversed.
        target_reg (projectq.types.Qureg):
            The register where states are reversed up to the pivot.
        controls (list[Qubit]):
            Control qubits.
    """
    for _ in range(2):
        # Compare.
        Subtract | (pivot_reg, target_reg + [dirty_qubit])
        Add | (pivot_reg, target_reg)

        # Conditioned double flip.
        Subtract & dirty_qubit & controls | (pivot_reg, target_reg)
        MultiNot & dirty_qubit & controls | target_reg


def do_const_pivot_flip(gate, target_reg, controls, dirty_qubit):
    """
    Args:
        gate (ConstPivotFlipGate):
            The gate being decomposed (contains pivot info).
        target_reg (projectq.types.Qureg):
            The register where states are reversed up to the pivot.
        controls (list[Qubit]):
            Control qubits.
    """
    for _ in range(2):
        # Compare.
        OffsetGate(-gate.pivot) | target_reg + [dirty_qubit]
        OffsetGate(gate.pivot) | target_reg

        # Conditioned double flip.
        OffsetGate(-gate.pivot) & dirty_qubit & controls | target_reg
        MultiNot & dirty_qubit & controls | target_reg


all_defined_decomposition_rules = [
    DecompositionRule(
        min_workspace=1,
        gate_class=ConstPivotFlipGate,
        gate_decomposer=lambda cmd: do_const_pivot_flip(
            cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits,
            dirty_qubit=cmd.untouched_qubits()[0])),

    DecompositionRule(
        min_workspace=1,
        gate_class=PivotFlipGate,
        gate_decomposer=lambda cmd: do_pivot_flip(
            pivot_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1],
            controls=cmd.control_qubits,
            dirty_qubit=cmd.untouched_qubits()[0])),
]
