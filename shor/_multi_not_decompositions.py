# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.ops import X, C, C_star, XGate
from ._multi_not_gates import MultiNotGate


def do_multi_not_with_one_big_not_and_friends(targets, controls):
    """
    N: len(targets) + len(controls)
    Size: O(N)
    Depth: O(N)
    Sources: ???
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

    for i in reversed(range(len(targets) - 1)):
        C(X) | (targets[i], targets[i + 1])

    C_star(X) | (controls, targets[0])

    for i in range(len(targets) - 1):
        C(X) | (targets[i], targets[i + 1])


def cut_not_max_controls_in_half(target, controls, dirty):
    """
    Uses a bit of workspace to build a C*NOT out of C*NOTs with half as many
    controls. A NOT with C controls is reduced to four NOTs with at most
    floor(C/2)+1 controls and at least floor(C/2) workspace.

    N: len(controls)
    Size: O(N)
    Depth: O(N)
    Sources: ???
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
    if len(controls) <= 2:
        return

    h = len(controls) // 2
    a = controls[h:]
    b = controls[:h] + [dirty]
    for _ in range(2):
        C_star(X) | (a, dirty)
        C_star(X) | (b, target)


def cut_not_max_controls_into_toffolis(target, controls, dirty_reg):
    """
    Uses C-2 workspace to build a C*NOT with C controls out of Toffoli gates.

    N: len(controls)
    Size: O(N)
    Depth: O(N)
    Sources: ???
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
        dirty_reg (projectq.types.Qureg):
            Extra workspace.
    """
    d = len(controls) - 2
    assert len(dirty_reg) >= d
    if len(controls) <= 2:
        return
    dirty_reg = dirty_reg[:d]

    ccx = C(X, 2)

    def sweep(r):
        for i in r:
            ccx | (controls[i+2], dirty_reg[i], dirty_reg[i+1])

    for _ in range(2):
        ccx | (controls[-1], dirty_reg[-1], target)
        sweep(reversed(range(d - 1)))
        ccx | (controls[0], controls[1], dirty_reg[0])
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
        min_allocated_but_untouched_bits=1,
        gate_decomposer=lambda cmd: cut_not_max_controls_in_half(
            target=cmd.qubits[0],
            controls=cmd.control_qubits,
            dirty=cmd.untouched_qubits()[0])),
]