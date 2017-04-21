# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.ops import X, XGate
from ..gates import MultiNotGate


def do_multi_not_with_one_big_not_and_friends(targets, controls):
    """
    N: len(targets) + len(controls)
    Size: O(N)
    Depth: O(N)
    Diagram:
          ⋮                    ⋮
        ──●──      ─────────────●─────────────
          │                     │
        ──●──      ─────────────●─────────────
          │                     │
        ──●──      ─────────────●─────────────
          │    =                │
        ──⊕──      ───────────●─⊕─●───────────
          │                   │   │
        ──⊕──      ─────────●─⊕───⊕─●─────────
          │                 │       │
        ──⊕──      ───────●─⊕───────⊕─●───────
          │               │           │
        ──⊕──      ───────⊕───────────⊕───────
          ⋮             ⋰             ⋱
    Args:
        targets (projectq.types.Qureg):
            The qubits to toggle if the controls are all satisfied.
        controls (projectq.types.Qureg):
            The qubits to condition toggling on.
    """
    if len(targets) == 0:
        return

    # Don't bother with anything fancy if you can just use Toffolis.
    if len(controls) <= 2:
        for target in targets:
            X & controls | target
        return

    for i in reversed(range(len(targets) - 1)):
        X & targets[i] | targets[i + 1]

    X & controls | targets[0]

    for i in range(len(targets) - 1):
        X & targets[i] | targets[i + 1]


def cut_not_max_controls_in_half(target, controls, dirty):
    """
    Uses a bit of workspace to build a C*NOT out of C*NOTs with half as many
    controls. A NOT with C controls is reduced to four NOTs with at most
    floor(C/2)+1 controls and at least floor(C/2) workspace.

    N: len(controls)
    Size: O(N)
    Depth: O(N)
    Diagram:
         n            n
        ━/━●━━       ━/━●━━━━●━━━
         m │          m │    │
        ━/━●━━       ━/━┿━●━━┿━●━
           │     =      │ │  │ │
        ───⊕──       ───┼─⊕──┼─⊕─
                        │ │  │ │
        ──────       ───⊕─●──⊕─●─
    Args:
        target (projectq.types.Qubit):
            The qubit to toggle if the controls are all satisfied.
        controls (projectq.types.Qureg):
            The qubits to condition toggling on.
        dirty (projectq.types.Qubit):
            Extra workspace.
    """
    assert len(controls) > 2

    h = len(controls) // 2
    a = controls[h:]
    b = controls[:h] + [dirty]
    for _ in range(2):
        X & a | dirty
        X & b | target


def cut_not_max_controls_into_toffolis(target, controls, dirty_reg):
    """
    Uses C-2 workspace to build a C*NOT with C controls out of Toffoli gates.

    N: len(controls)
    Size: O(N)
    Depth: O(N)
    Diagram:
        ──●──      ─────────●────────────●───────
          │                 │            │
        ──●──      ─────────●────────────●───────
          │                 │            │
        ──┼──      ───────●─⊕─●────────●─⊕─●─────
          │    =          │   │        │   │
        ──●──      ───────●───●────────●───●─────
          │               │   │        │   │
        ──┼──      ─────●─⊕───⊕─●────●─⊕───⊕─●───
          │             │       │    │       │
        ──●──      ─────●───────●────●───────●───
          │             │       │    │       │
        ──┼──      ───●─⊕───────⊕─●──⊕───────⊕───
          │           │           │
        ──●──      ───●───────────●──────────────
          │           │           │
        ──⊕──      ───⊕───────────⊕──────────────
    Args:
        target (projectq.types.Qubit):
            The qubit to toggle if the controls are all satisfied.
        controls (projectq.types.Qureg):
            The qubits to condition toggling on.
        dirty_reg (projectq.types.Qureg):
            Extra workspace.
    """
    d = len(controls) - 2
    assert len(dirty_reg) >= d
    assert len(controls) > 2
    dirty_reg = dirty_reg[:d]

    def sweep(r):
        for i in r:
            X & controls[i+2] & dirty_reg[i] | dirty_reg[i+1]

    for _ in range(2):
        X & controls[-1] & dirty_reg[-1] | target
        sweep(reversed(range(d - 1)))
        X & controls[0] & controls[1] | dirty_reg[0]
        sweep(range(d - 1))


all_defined_decomposition_rules = [
    # Use many dirty bits from last step to cut all the way down to Toffolis.
    DecompositionRule(
        gate_class=XGate,
        min_controls=3,
        custom_predicate=lambda cmd:
            len(cmd.untouched_qubits()) >= len(cmd.control_qubits) - 2,
        gate_decomposer=lambda cmd: cut_not_max_controls_into_toffolis(
            target=cmd.qubits[0],
            controls=cmd.control_qubits,
            dirty_reg=cmd.untouched_qubits())),

    # Reduce from many targets to one target.
    DecompositionRule(
        gate_class=MultiNotGate,
        gate_decomposer=lambda cmd: do_multi_not_with_one_big_not_and_friends(
            targets=cmd.qubits[0],
            controls=cmd.control_qubits)),

    # Use a dirty bit to cut control counts in half.
    DecompositionRule(
        gate_class=XGate,
        min_controls=3,
        min_workspace=1,
        gate_decomposer=lambda cmd: cut_not_max_controls_in_half(
            target=cmd.qubits[0],
            controls=cmd.control_qubits,
            dirty=cmd.untouched_qubits()[0])),
]
