# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.ops import X, XGate, H
from .gates import Increment, Decrement, PhaseGradient, Z, IncrementGate


def do_bootstrap_ancilla_out_of_big_cnot(target, controls):
    """
    Reduces a C*NOT without workspace into operations that do have workspace.

    N: len(controls)
    Size: O(N)
    Depth: O(N)
    Diagram:
                                           ┌─────┐   ┌──┐          ┌──┐
        ────●─        ─────●─────────────●─┤Z^2⁻ⁿ├───┤  ├──────────┤  ├─
        n-2 │         n-2  │             │ ├─────┤   │  │ ┌──────┐ │  │
        ━/━━●━        ━/━━━●━━━━━━━━━━━━━●━┥    ¼┝━━━┥+1┝━┥    -¼┝━┥−1┝━
            │              │             │ │Grad │   │  │ │Grad  │ │  │
        ────●─        ─────┼───────●─────┼─┤     ├─●─┤  ├─┤      ├─┤  ├─
            │              │       │     │ └─────┘ │ └──┘ └──────┘ └──┘
            │          ┌─┐ │ ┌───┐ │ ┌─┐ │  ┌───┐  │ ┌─┐  ┌─┐
        ────⊕─        ─┤H├─⊕─┤T⁻¹├─⊕─┤T├─⊕──┤T⁻¹├──⊕─┤T├──┤H├───────────
                       └─┘   └───┘   └─┘    └───┘    └─┘  └─┘
    Args:
        target (projectq.types.Qubit):
            The qubit to toggle if the controls are all satisfied.
        controls (projectq.types.Qureg):
            The qubits to condition the toggling on.
    """
    cs = controls[:-1]
    c = controls[-1]
    T = Z**(1/4)

    # Toggle target.
    H | target
    X & cs | target
    T**-1 | target
    X & c | target
    T | target
    X & cs | target
    T**-1 | target
    X & c | target
    T | target
    H | target

    # Phase correction.
    Z**(2**-len(controls)) | controls[0]
    PhaseGradient**(1/4) | controls[1:]
    Increment | controls
    PhaseGradient**(-1/4) | controls[1:]
    Decrement | controls


def do_bootstrap_ancilla_out_of_big_increment(target_reg, controls):
    """
    Reduces a controlled increment without workspace into simpler operations.

    N: len(target_reg) + len(controls)
    Size: O(N)
    Depth: O(N)
    Diagram:
         c                c
        ━/━━●━━━         ━/━━●━━●━━━
        n-1┌┴─┐          n-1 │ ┌┴─┐
        ━/━┥  ┝━    =    ━/━━●━┥+1┝━
           │+1│              │ └──┘
        ───┤  ├─         ────⊕──────
           └──┘
    Args:
        target_reg (projectq.types.Qureg):
            The qubit register to increment.
        controls (projectq.types.Qureg):
            The qubits to condition the toggling on.
    """
    low = target_reg[:-1]

    X & controls & low | target_reg[-1]
    Increment & controls | low


all_defined_decomposition_rules = [
    # Reduce a C*NOT without workspace into operations with workspace.
    DecompositionRule(
        gate_class=XGate,
        min_controls=2,
        max_workspace=0,
        gate_decomposer=lambda cmd: do_bootstrap_ancilla_out_of_big_cnot(
            target=cmd.qubits[0],
            controls=cmd.control_qubits)),

    # Simplify an increment without workspace by extracting a C*NOT from it.
    DecompositionRule(
        gate_class=IncrementGate,
        max_workspace=0,
        gate_decomposer=lambda cmd: do_bootstrap_ancilla_out_of_big_increment(
            target_reg=cmd.qubits[0],
            controls=cmd.control_qubits)),
]
