# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from ._const_modular_double_multiplication_gates import (
    ConstModularDoubleMultiplicationGate
)
from ._modular_addition_gates import (
    ModularAdditionGate, ModularSubtractionGate
)
from ._modular_scaled_addition_gates import ModularScaledAdditionGate


def do_double_multiplication(gate, forward_reg, inverse_reg, controls):
    """
    Reversibly adds one register into another of the same size.

    N: len(input_reg) + len(target_ref)
    Size: O(N lg N)
    Depth: O(N)

    Sources:
        Craig Gidney 2017

    Diagram:
        c                  c
       ━/━━━━━●━━━━       ━/━━━━━●━━━━━━━●━━━━━━━●━━━━━━━━●━━━━━●━━━━━●━━━
        n ┌───┴──┐         n  ┌──┴──┐┌───┴───┐┌──┴──┐  ┌──┴─┐┌──┴─┐┌──┴─┐
       ━/━┥ ×K%R ┝━   =   ━/━━┥  A  ┝┥-AK⁻¹%R┝┥  A  ┝━━┥  A ┝┥-A%R┝┥  A ┝━
        n ├──────┤         n  ├─────┤├───────┤├─────┤  ├────┤├────┤├────┤
       ━/━┥×K⁻¹%R┝━       ━/━━┥+AK%R┝┥   A   ┝┥+AK%R┝━━┥+A%R┝┥  A ┝┥+A%R┝━
          └──────┘            └─────┘└───────┘└─────┘  └────┘└────┘└────┘
    Args:
        gate (ConstModularDoubleMultiplicationGate):
            The gate being decomposed.
        forward_reg (projectq.types.Qureg):
            The register to mod-multiply by the forward factor.
        inverse_reg (projectq.types.Qureg):
            The register to mod-multiply by the inverse factor.
        controls (list[Qubit]):
            Control qubits.
    """
    assert len(forward_reg) == len(inverse_reg)
    assert 1 << len(forward_reg) >= gate.modulus

    def f(x):
        return ModularScaledAdditionGate(x, gate.modulus)
    scale_add = ModularScaledAdditionGate(gate.factor, gate.modulus)
    scale_sub = ModularScaledAdditionGate(-gate.inverse_factor, gate.modulus)
    add = ModularAdditionGate(gate.modulus)
    sub = ModularSubtractionGate(gate.modulus)

    scale_add & controls | (forward_reg, inverse_reg)
    scale_sub & controls | (inverse_reg, forward_reg)
    scale_add & controls | (forward_reg, inverse_reg)

    add & controls | (inverse_reg, forward_reg)
    sub & controls | (forward_reg, inverse_reg)
    add & controls | (inverse_reg, forward_reg)


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=ConstModularDoubleMultiplicationGate,
        gate_decomposer=lambda cmd: do_double_multiplication(
            cmd.gate,
            forward_reg=cmd.qubits[0],
            inverse_reg=cmd.qubits[1],
            controls=cmd.control_qubits)),
]
