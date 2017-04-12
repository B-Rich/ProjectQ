# -*- coding: utf-8 -*-

from projectq.types import Qureg
from projectq.meta import Control, Dagger
from projectq.ops import X, Swap
import math
from fractions import Fraction


def sample_period(eng,
                  factor,
                  modulus,
                  precision,
                  phase_qubit,
                  work_qureg,
                  ancilla_qureg):
    """

    Args:
        eng (projectq.cengines.BasicEngine):
        factor (int):
        modulus (int):
        precision (int):
            The number of iterations.
        phase_qubit (Qubit):
            A clean zero-initialized qubit.
        work_qureg (Qureg):
            A clean zero-initialized register with lg(modulus) bits.
        ancilla_qureg (Qureg): A semi-dirty register.
            A mostly-dirty register with lg(modulus) bits.
            Only the most significant bit must be clean and zero-initialised.

    Returns:
        int:
            A number related to the period.
    """

    a = Fraction(0, 1)
    for i in range(precision):
        rev_i = precision - i - 1
        k = pow(factor, 1 << rev_i, modulus)
        modular_multiply_both_ways(eng,
                                   k,
                                   modulus,
                                   work_qureg,
                                   ancilla_qureg,
                                   controls=[phase_qubit])
        X**a | phase_qubit
        a += Fraction(measure(phase_qubit), 2 << i)
        reset(phase_qubit)

    total = measure(work_qureg)
    modular_multiply_both_ways(eng,
                               total,
                               modulus,
                               ancilla_qureg,
                               work_qureg)


def modular_multiply_both_ways(eng,
                               factor,
                               modulus,
                               target_qureg,
                               inverse_qureg,
                               controls=()):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        factor (int):
        modulus (int):
        controls (list[Qubit]):
        target_qureg (Qureg):
        inverse_qureg (Qureg):
    """
    inverse_factor = multiplicative_inverse(factor, modulus)
    scaled_modular_add(eng,
                       factor,
                       modulus,
                       target_qureg,
                       inverse_qureg,
                       controls)
    scaled_modular_add(eng,
                       inverse_factor,
                       modulus,
                       inverse_qureg,
                       target_qureg,
                       controls)
    scaled_modular_add(eng,
                       factor,
                       modulus,
                       target_qureg,
                       inverse_qureg,
                       controls)


def scaled_modular_add(eng,
                       scale_factor,
                       modulus,
                       input_qureg,
                       target_qureg,
                       controls=()):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        scale_factor (int):
        modulus (int):
        input_qureg (Qureg):
        target_qureg (Qureg):
        controls (list[Qubit]):
    """
    n = len(target_qureg)
    assert n >= 3
    assert len(input_qureg) == n
    d1, d2, d3 = input_qureg[:3]
    for _ in range(n - 1):
        inverse_modular_double(eng, modulus, target_qureg, d1, d2)
    for i in range(n)[::-1]:
        modular_offset(eng,
                       offset_amount=scale_factor,
                       modulus=modulus,
                       target_qureg=target_qureg,
                       dirty_1=d1 if i > 0 else d2,
                       dirty_2=d2 if i > 1 else d3,
                       controls=controls + [input_qureg[i]])
        if i > 0:
            modular_double(eng, modulus, target_qureg, d1, d2)


def inverse_modular_double(eng, modulus, target, dirty_1, dirty_2):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        modulus (int):
        target (Qureg):
        dirty_1 (Qubit):
        dirty_2 (Qubit):
    """
    with Dagger(eng):
        modular_double(eng, modulus, target, dirty_1, dirty_2)


def modular_double(eng, modulus, target, dirty_1, dirty_2):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        modulus (int):
        target (Qureg):
        dirty_1 (Qubit):
        dirty_2 (Qubit):
    """
    f = (modulus + 1) >> 1
    flip_below(eng,
               pivot=f,
               target_qureg=target,
               dirty_1=dirty_1,
               dirty_2=dirty_2)
    modular_offset(eng,
                   offset_amount=f,
                   target_qureg=target,
                   modulus=modulus,
                   dirty_1=dirty_1,
                   dirty_2=dirty_2)
    with Control(eng, target[-1]):
        X | All(target[:-1])
    X | target[-1]
    left_rotate(eng, target)


def flip_below(eng, target_qureg, pivot, dirty_1, dirty_2, controls=()):
    """
    N: len(target_qureg)  ???controls???
    Depth: O(N)
    Size: O(N lg N)
    Args:
        eng (projectq.cengines.BasicEngine):
        pivot (int):
        target_qureg (Qureg):
        dirty_1 (Qubit):
        dirty_2 (Qubit):
        controls (list[Qubit]):
    """
    c = controls + [dirty_1]
    for _ in range(2):
        toggle_if_less_than_const(eng,
                                  target=dirty_1,
                                  comparand=target_qureg,
                                  pivot=pivot,
                                  dirty=dirty_2)
        offset(eng,
               target=target_qureg,
               offset_amount=-pivot,
               dirty_1=dirty_2,
               controls=c)
        with Control(eng, c):
            All(X) | target_qureg


def toggle_if_less_than_const(eng,
                              target,
                              comparand,
                              pivot,
                              dirty,
                              controls=()):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        target (Qubit): The qubit to toggle based on the comparison.
        comparand (Qureg): The register to compare against the pivot.
        pivot (int): The upper limit being compared against.
        dirty (Qubit):
        controls (list[Qubit]):
    """

    # could be O(N) with more dirty since only carry is needed?

    offset(eng,
           target=comparand + [target],
           offset_amount=-pivot,
           dirty_1=dirty,
           controls=controls)
    offset(eng,
           target=comparand,
           offset_amount=+pivot,
           dirty_1=dirty,
           controls=controls)


def modular_offset(eng,
                   target_qureg,
                   offset_amount,
                   modulus,
                   dirty_1,
                   dirty_2,
                   controls=()):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        target_qureg (Qureg):
        offset_amount (int):
        modulus (int):
        dirty_1 (Qubit):
        dirty_2 (Qubit):
        controls (list[Qubit]):
    """
    for pivot in [modulus - offset_amount, modulus, offset_amount]:
        flip_below(eng,
                   pivot=pivot,
                   target_qureg=target_qureg,
                   dirty_1=dirty_1,
                   dirty_2=dirty_2,
                   controls=controls)


def left_rotate(eng, target):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        target (Qureg):
    """
    for i in range(len(target) - 1):
        swap | target[i], target[i + 1]


def offset(eng,
           target,
           offset_amount,
           dirty_1,
           controls=()):
    """
    Args:
        eng (projectq.cengines.BasicEngine):
        target (Qureg):
        offset_amount (int):
        dirty_1 (Qubit):
        controls (list[Qubit]):
    """
    raise NotImplementedError()


def subtract(eng, input, target, dirty_1, controls=()):
    """
    Reversibly subtracts the input register's value out of the target register,
    in O(N) depth and O(N) size with no ancilla using only CNOT and CSWAP
    operations.

    This construction is based on the VanRantergem adder, but modified in a way
    that avoids the need for an ancilla for the carry signal. Instead, the high
    bit of the input is used to hold the carry signal.

    Args:
        eng (projectq.cengines.BasicEngine): Engine.
        input (Qureg):
            The source register. Used as workspace, but not affected in the
            end.
        target (Qureg): The destination register.
    """

    if len(controls) == 0:
        subtract_no_controls(eng, input, target)
        return

    lcs = [dirty_1] + target
    subtract_no_controls(eng, input, lcs)
    poly_cnot(targets=lcs, controls=controls, dirty_1=input[0])
    All(X) | lcs
    subtract_no_controls(eng, input, lcs)
    All(X) | lcs
    poly_cnot(targets=lcs, controls=controls, dirty_1=input[0])


def poly_cnot(targets, dirty_1, controls=()):
    """
    Efficiently applies controlled-nots with many controls and many targets.

    N: len(targets) + len(controls)
    Depth: O(N)
    Size: O(N)
    Args:
        targets (list[Qubit]):
        dirty_1 (Qubit)
        controls (list[Qubit]):
    Diagram:
                     ⋮
        ─────────────●─────────────
                     │
        ─────────────●─────────────
                     │
        ─────────────●─────────────
                     │
        ───────────●─X─●───────────
                   │   │
        ─────────●─X───X─●─────────
                 │       │
        ───────●─X───────X─●───────
               │           │
        ───────X───────────X───────
             ⋰             ⋱
    """
    if not targets:
        return
    if not controls:
        All(X) | targets
        return

    controls_not(target=targets[0], dirty_1=dirty_1, controls=controls)
    raise NotImplementedError()


def controls_not(target, dirty_1, controls=()):
    """
    N: len(controls)
    Depth: O(N)
    Size: O(N)
    Args:
        target (Qubit):
        dirty_1 (Qubit):
        controls (list[Qubit]):
    """
    c1 = controls[::2]
    c2 = controls[1::2]
    for _ in range(2):
        controls_not_many_dirty(target=dirty_1,
                                dirty=c1,
                                controls=c2)
        controls_not_many_dirty(target=target,
                                dirty=c2,
                                controls=c1 + [dirty_1])


def controls_not_many_dirty(target, dirty, controls=()):
    """
    N: len(controls)
    Depth: O(N)
    Size: O(N)
    Args:
        target (Qubit):
        dirty (list[Qubit]):
        controls (list[Qubit]):
    """
    raise NotImplementedError()


def subtract_no_controls(eng, input, target):
    n = len(target)

    if len(input) < n:
        # TODO: carry into an increment.
        raise NotImplementedError("Target is larger than the input.")

    avail, used = input[:-n], input[-n:]
    return subtract_same_size(eng, Qureg(used), target)


def subtract_same_size(eng, input, target):
    """
    Reversibly subtracts the input register's value out of the target register,
    in O(N) depth and O(N) size with no ancilla using only CNOT and CSWAP
    operations.

    This construction is based on the VanRantergem adder, but modified in a way
    that avoids the need for an ancilla for the carry signal. Instead, the high
    bit of the input is used to hold the carry signal.

    Args:
        eng (projectq.cengines.BasicEngine): Engine.
        input (Qureg):
            The source register. Used as workspace, but not affected in the
            end.
        target (Qureg): The destination register.
    """
    n = len(target)
    assert len(input) == n

    carry_signal = input[-1]
    low_inputs = input[:-1]
    m = n - 1

    # Stash same-or-different in target.
    for i in range(m):
        with Control(eng, low_inputs[i]):
            X | target[i]

    # Correct for inverted carry signal (part 1/2).
    with Control(eng, carry_signal):
        X | low_inputs

    # Propagate carry signals through input.
    for i in range(m):
        # If bits were different, carry stays same. Else bits replace carry.
        with Control(eng, target[i]):
            Swap | (carry_signal, low_inputs[i])

    # Apply carry signal effects while uncomputing carry signal.
    for i in range(m)[::-1]:
        # Apply.
        with Control(eng, carry_signal):
            X | target[i + 1]
        # Uncompute.
        with Control(eng, target[i]):
            Swap | (carry_signal, low_inputs[i])

    # Unstash same-vs-dif and correct for inverted carry signal (part 2/2).
    with Control(eng, carry_signal):
        X | low_inputs + target[1:-1]


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = extended_gcd(b % a, a)
    return g, x - (b // a) * y, y


def multiplicative_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    return x % m
