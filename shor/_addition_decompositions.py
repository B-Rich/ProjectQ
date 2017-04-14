# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from projectq.cengines import DecompositionRule
from projectq.ops import X, Swap, All, C, C_star
from ._addition_gates import AdditionGate
from ._increment_gates import Increment, Decrement


def do_addition_with_same_size_and_no_controls(input_reg, target_reg):
    """
    Reversibly adds one register into another of the same size.

    N: len(input_reg) + len(target_ref)
    Size: O(N)
    Depth: O(N)

    Sources:
        Takahashi and Kunihiro, 2005
        "A linear-size quantum circuit for addition with no ancillary qubits"

        Yvan Van Rentergem and Alexis De Vos, 2004
        "Optimal Design of A Reversible Full Adder"

    Diagram:
       ┌───┐
       ┤   ├       ─⊕─────×─────────────────────────────────────×─●───⊕─
       │   │        │     │                                     │ │   │
       ┤   ├       ─⊕─────┼────×───────────────────────────×─●──┼─┼───⊕─
       │   │        │     │    │                           │ │  │ │   │
       ┤inp├       ─⊕─────┼────┼────×─────────────────×─●──┼─┼──┼─┼───⊕─
       │ A │        │     │    │    │                 │ │  │ │  │ │   │
       ┤   ├       ─⊕─────┼────┼────┼────×───────×─●──┼─┼──┼─┼──┼─┼───⊕─
       │   │        │     │    │    │    │       │ │  │ │  │ │  │ │   │
       ┤   ├       ─●───●─×──●─×──●─×──●─×───●───×─┼──×─┼──×─┼──×─┼───●─
       └─┬─┘        │   │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │   │
       ┌─┴─┐   =    │   │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │   │
       ┤   ├       ─⊕───⊕─●──┼─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──┼─┼──●─⊕───⊕─
       │   │        │        │ │  │ │  │ │   │   │ │  │ │  │ │        │
       ┤   ├       ─⊕────────⊕─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──●─⊕────────⊕─
       │   │        │             │ │  │ │   │   │ │  │ │             │
       ┤+=A├       ─⊕─────────────⊕─●──┼─┼───┼───┼─┼──●─⊕─────────────⊕─
       │   │        │                  │ │   │   │ │                  │
       ┤   ├       ─⊕──────────────────⊕─●───┼───●─⊕──────────────────⊕─
       │   │        │                        │                        │
       ┤   ├       ─⊕────────────────────────⊕────────────────────────⊕─
       └───┘
                   (1)  --------(2)-------  (3)  --------(4)-------  (5)
    Args:
        eng (projectq.cengines.BasicEngine): Engine.
        input_reg (projectq.types.Qureg):
            The source register. Used as workspace, but ultimately not affected
            by the operation.
            end.
        target_reg (projectq.types.Qureg):
            The destination register, whose value is increased by the value in
            the source register.
    """
    assert len(input_reg) == len(target_reg)
    n = len(target_reg)
    if n == 0:
        return

    carry_bit = input_reg[-1]
    cnot = C(X)
    cnots = C(All(X))
    cswap = C(Swap)

    # (1) Dirty MSB correction.
    cnots | (carry_bit, (input_reg[:-1] + target_reg)[::-1])

    # (2) Ripple forward.
    for i in range(n - 1):
        cnot | (carry_bit, target_reg[i])
        cswap | (target_reg[i], carry_bit, input_reg[i])

    # (3) High bit toggle.
    cnot | (carry_bit, target_reg[-1])

    # (4) Ripple backward.
    for i in range(n - 1)[::-1]:
        cswap | (target_reg[i], carry_bit, input_reg[i])
        cnot | (input_reg[i], target_reg[i])

    # (5) Dirty MSB correction.
    cnots | (carry_bit, input_reg[:-1] + target_reg)


def do_addition_with_larger_target_and_no_controls(input_reg, target_reg):
    """
    Reversibly adds one register into another larger one size.

    N: len(input_reg) + len(target_ref)
    Size: O(N)
    Depth: O(N)

    Sources:
        Takahashi and Kunihiro, 2005
        "A linear-size quantum circuit for addition with no ancillary qubits"

        Yvan Van Rentergem and Alexis De Vos, 2004
        "Optimal Design of A Reversible Full Adder"

    Diagram:
                     ╭──●───╮
       ┌───┐         │ ┌┴─┐ │
       ┤   ├       ──┼─┤  ├─┼────────×─────────────────────────────────────×─●─
       │   │         │ │  │ │        │                                     │ │
       ┤   ├       ──┼─┤  ├─┼────────┼────×───────────────────────────×─●──┼─┼─
       │   │         │ │  │ │        │    │                           │ │  │ │
       ┤inp├       ──┼─┤  ├─┼────────┼────┼────×─────────────────×─●──┼─┼──┼─┼─
       │ A │         │ │  │ │        │    │    │                 │ │  │ │  │ │
       ┤   ├       ──┼─┤  ├─┼────────┼────┼────┼────×───────×─●──┼─┼──┼─┼──┼─┼─
       │   │         │ │  │ │        │    │    │    │       │ │  │ │  │ │  │ │
       ┤   ├       ──╯ │  │ ╰─●────●─×──●─×──●─×──●─×───●───×─┼──×─┼──×─┼──×─┼─
       └─┬─┘           │−1│   │    │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │
       ┌─┴─┐   =       │  │  ┌┴─┐  │ │  │ │  │ │  │ │   │   │ │  │ │  │ │  │ │
       ┤   ├       ────┤  ├──┤  ├──⊕─●──┼─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──┼─┼──●─⊕─
       │   │           │  │  │  │       │ │  │ │  │ │   │   │ │  │ │  │ │
       ┤   ├       ────┤  ├──┤  ├───────⊕─●──┼─┼──┼─┼───┼───┼─┼──┼─┼──●─⊕──────
       │   │           │  │  │  │            │ │  │ │   │   │ │  │ │
       ┤+=A├       ────┤  ├──┤+1├────────────⊕─●──┼─┼───┼───┼─┼──●─⊕───────────
       │   │           │  │  │  │                 │ │   │   │ │
       ┤   ├       ────┤  ├──┤  ├─────────────────⊕─●───┼───●─⊕────────────────
       │   │        e  │  │  │  │                      ┌┴─┐
       ┤   ├       ━/━━┥  ┝━━┥  ┝━━━━━━━━━━━━━━━━━━━━━━┥+1┝━━━━━━━━━━━━━━━━━━━━
       └───┘           └──┘  └──┘                      └──┘
                       (1)    (2)  -------(3)--------  (4)  --------(5)--------
    Args:
        eng (projectq.cengines.BasicEngine): Engine.
        input_reg (projectq.types.Qureg):
            The source register. Used as workspace, but ultimately not affected
            by the operation.
            end.
        target_reg (projectq.types.Qureg):
            The destination register, whose value is increased by the value in
            the source register.
    """
    assert len(input_reg) <= len(target_reg)
    n = len(input_reg)
    if n == 0:
        return

    carry_bit = input_reg[-1]
    cnot = C(X)
    cswap = C(Swap)

    # (1) Dirty MSB correction.
    C(Decrement) | (carry_bit, target_reg)

    # (2) Handle MSB separately.
    C(Increment) | (carry_bit, target_reg[n-1:])

    # (3) Ripple forward.
    for i in range(n - 1):
        cnot | (carry_bit, target_reg[i])
        cswap | (target_reg[i], carry_bit, input_reg[i])

    # (4) Carry into high output bits.
    C(Increment) | (carry_bit, target_reg[n-1:])

    # (5) Ripple backward.
    for i in range(n - 1)[::-1]:
        cswap | (target_reg[i], carry_bit, input_reg[i])
        cnot | (input_reg[i], target_reg[i])


def do_addition_no_controls(input_reg, target_reg):
    # When input is larger, just ignore its high bits.
    if len(input_reg) >= len(target_reg):
        do_addition_with_same_size_and_no_controls(
            input_reg[:len(target_reg)], target_reg)
        return

    do_addition_with_larger_target_and_no_controls(input_reg, target_reg)


def do_addition(input_reg, target_reg, dirty, controls):
    if len(controls) == 0:
        return do_addition_no_controls(input_reg, target_reg)

    # Remove controls with double-add-invert trick.
    expanded = [dirty] + target_reg
    for _ in range(2):
        do_addition_no_controls(input_reg, expanded)
        C_star(All(X)) | (controls, expanded)
        All(X) | expanded


all_defined_decomposition_rules = [
    DecompositionRule(
        gate_class=AdditionGate,
        gate_decomposer=lambda cmd: do_addition_no_controls(
            input_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1]),
        max_controls=0),

    DecompositionRule(
        gate_class=AdditionGate,
        gate_decomposer=lambda cmd: do_addition(
            input_reg=cmd.qubits[0],
            target_reg=cmd.qubits[1],
            controls=cmd.control_qubits,
            dirty=cmd.untouched_qubits()[0]),
        min_allocated_but_untouched_bits=1),
]
