# -*- coding: utf-8 -*-

from projectq.cengines import DecompositionRule
from projectq.ops import X
from .gates import Add, Subtract, IncrementGate, MultiNot


def do_increment_with_no_controls_and_n_dirty(target_reg, dirty_reg):
    """
    Reversibly increments a register by subtracting x and -x-1 out of it.

    N: len(target_reg)
    Size: O(N)
    Depth: O(N)
    Sources: Craig Gidney 2015
    Diagram:
       ┌────┐        ┌───┐   ┌───┐
       ┤    ├       ─┤   ├───┤   ├───
       │    │        │   │   │   │
       ┤    ├       ─┤   ├───┤   ├───
       │    │        │   │   │   │
       ┤ +1 ├       ─┤−=A├───┤−=A├───
       │    │        │   │   │   │
       ┤    ├       ─┤   ├───┤   ├───
       │    │        │   │   │   │
       ┤    ├       ─┤   ├───┤   ├───
       └────┘   =    ├───┤   ├───┤
       ──────       ─┤   ├─⊕─┤   ├─⊕─
                     │   │   │   │
       ──────       ─┤   ├─⊕─┤   ├─⊕─
                     │   │   │   │
       ──────       ─┤inp├─⊕─┤inp├─⊕─
                     │ A │   │ A │
       ──────       ─┤   ├─⊕─┤   ├─⊕─
                     │   │   │   │
       ──────       ─┤   ├─⊕─┤   ├─⊕─
                     └───┘   └───┘
    Args:
        target_reg (projectq.types.Qureg):
            The register to increment.
        dirty_reg (projectq.types.Qureg):
            A workspace register at least as large as the target register.
    """
    assert len(dirty_reg) >= len(target_reg)
    dirty_reg = dirty_reg[:len(target_reg)]

    Subtract | (dirty_reg, target_reg)
    MultiNot | dirty_reg
    Subtract | (dirty_reg, target_reg)
    MultiNot | dirty_reg


def do_increment_with_1_dirty(target_reg, dirty_qubit, controls):
    """
    Reversibly increments an even-sized register.

    N: len(target_reg) + len(controls)
    Size: O(N)
    Depth: O(N)
    Sources: Craig Gidney 2017
    Diagram:
        c                 c
       ━/━━━━●━━━        ━/━━━━━━━━━━━━━━●━━━━━━━●━━━━━━━━━━●━━━━━━━●━━━━━
        n ┌──┴─┐          n        ┌───┐ │ ┌───┐ │    ┌───┐ │ ┌───┐ │
       ━/━┥    ┝━        ━/━━━━━━━━┥ A ┝━●━┥ A ┝━●━━━━┥+=A┝━⊕━┥−=A┝━⊕━━━━━
       n-1│ +1 │         n-1       ├───┤ │ ├───┤ │    ├───┤ │ ├───┤ │
       ━/━┥    ┝━        ━/━━━╲ ╱──┤   ├─⊕─┤   ├─⊕────┤   ├─⊕─┤   ├─⊕─╲ ╱━
          └────┘    =          ╳   │−=A│ │ │+=A│ │    │inp│ │ │inp│ │  ╳
       ──────────        ─────╱ ╲━━┥   ┝━⊕━┥   ┝━⊕━━━━┥ A ┝━⊕━┥ A ┝━⊕━╱ ╲─
                                   └───┘   └───┘      └───┘   └───┘
    Args:
        target_reg (projectq.types.Qureg):
            The register to increment.
        dirty_qubit (projectq.types.Qubit):
            A workspace qubit.
        controls (list[projectq.types.Qubit]):
            Qubits to condition the operation on.
    """
    if len(target_reg) == 0:
        return

    # Reduce even-sized case to odd-sized case.
    if len(target_reg) & 1 == 0:
        do_increment_with_1_dirty(
            target_reg[1:], dirty_qubit, controls + [target_reg[0]])
        X & controls | target_reg[0]
        return

    h = (len(target_reg) + 1) // 2
    a = target_reg[:h]
    b = [dirty_qubit] + target_reg[h:]

    # Increment high bits, conditioned on low bits wrapping.
    Subtract | (a, b)
    MultiNot & (controls + a) | b
    Add | (a, b)
    MultiNot & (controls + a) | b

    # Increment low bits.
    MultiNot & controls | a + b
    Add | (b, a)
    MultiNot & controls | a + b
    Subtract | (b, a)


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=IncrementGate,
        gate_decomposer=lambda cmd: do_increment_with_no_controls_and_n_dirty(
            target_reg=cmd.qubits[0],
            dirty_reg=cmd.untouched_qubits()),
        max_controls=0,
        custom_predicate=lambda cmd:
            len(cmd.untouched_qubits()) >= len(cmd.qubits[0])),

    DecompositionRule(
        gate_class=IncrementGate,
        gate_decomposer=lambda cmd: do_increment_with_1_dirty(
            target_reg=cmd.qubits[0],
            dirty_qubit=cmd.untouched_qubits()[0],
            controls=cmd.control_qubits),
        min_workspace=1,
    ),
]
