# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from ..gates import (
    ModularScaledAdditionGate,
    ModularDoubleGate,
    ModularUndoubleGate,
    ModularOffsetGate,
    ModularAdditionGate,
    ConstPivotFlipGate,
    PivotFlip,
    MultiNot,
    Increment,
    OffsetGate
)


def do_modular_offset(gate, target_reg, controls):
    """
    Reversibly adds one register, times a constant, into another of the same
    size.

    N: len(input_reg) + len(target_reg)
    C: len(controls)
    Size: O(N² lg N + NC????????????????????????????????????????)
    Depth: O(N² + NC)
    Diagram:
    Args:
        gate (ModularOffsetGate):
            The gate being decomposed (contains factor/modulus info).
        target_reg (projectq.types.Qureg):
            The register to scaled-add into.
        controls (list[Qubit]):
            Control qubits.
    """
    assert 1 << (len(target_reg) - 1) < gate.modulus <= 1 << len(target_reg)
    for pivot in [gate.modulus - gate.offset,
                  gate.modulus,
                  gate.offset]:
        ConstPivotFlipGate(pivot) & controls | target_reg


def do_modular_addition(gate, input_reg, target_reg, controls):
    """
    Reversibly adds one register, times a constant, into another of the same
    size.

    N: len(input_reg) + len(target_reg)
    C: len(controls)
    Size: O(N² lg N + NC????????????????????????????????????????)
    Depth: O(N² + NC)
    Diagram:
    Args:
        gate (ModularAdditionGate):
            The gate being decomposed (contains factor/modulus info).
        input_reg (projectq.types.Qureg):
            The register to scaled-add from.
        target_reg (projectq.types.Qureg):
            The register to scaled-add into.
        controls (list[Qubit]):
            Control qubits.
    """
    assert len(input_reg) == len(target_reg)
    assert 1 << (len(input_reg) - 1) < gate.modulus <= 1 << len(input_reg)

    MultiNot & controls | input_reg
    OffsetGate(gate.modulus + 1) & controls | input_reg
    PivotFlip | (input_reg, target_reg)

    ConstPivotFlipGate(gate.modulus) | target_reg

    MultiNot & controls | input_reg
    OffsetGate(gate.modulus + 1) & controls | input_reg
    PivotFlip | (input_reg, target_reg)


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=ModularOffsetGate,
        gate_decomposer=lambda cmd: do_modular_offset(
            cmd.gate,
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits)),

    DecompositionRule(
        gate_class=ModularAdditionGate,
        gate_decomposer=lambda cmd: do_modular_addition(
            cmd.gate,
            input_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1],
            controls=cmd.control_qubits)),
]
