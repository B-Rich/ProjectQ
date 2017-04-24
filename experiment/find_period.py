# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math
from fractions import Fraction

from experiment.decompositions import *
from experiment.gates import *
from projectq.setups.decompositions import swap2cnot
from experiment.gates._modular_bimultiplication import multiplicative_inverse
from projectq import MainEngine
from projectq.backends import Simulator, ResourceCounter
from projectq.cengines import (AutoReplacer,
                               DecompositionRuleSet,
                               LimitedCapabilityEngine)
from projectq.ops import Measure, H, X
from projectq.types import Qureg


def sample_period(eng,
                  factor,
                  modulus,
                  precision,
                  phase_qubit,
                  work_qureg,
                  ancilla_qureg):
    """

    Args:
        eng (projectq.cengines.MainEngine):
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
    # Incremental phase estimation.
    X | work_qureg[0]
    f = Fraction(0, 1)
    for i in range(precision):
        rev_i = precision - i - 1
        op = ModularBimultiplicationGate(pow(factor, 1 << rev_i, modulus),
                                         modulus)

        H | phase_qubit
        op & phase_qubit | (work_qureg, ancilla_qureg)
        Z**f | phase_qubit
        H | phase_qubit

        Measure | phase_qubit
        eng.flush()
        b = bool(phase_qubit)
        if b:
            X | phase_qubit
            f += Fraction(1, 2 << i)
        print("done iter", i, b, f)

    # Fix work register.
    Measure | work_qureg
    eng.flush()
    total_factor = int(work_qureg)
    fix_factor = multiplicative_inverse(total_factor,
                                        modulus) * -(-1)**precision % modulus
    ModularBimultiplicationGate(fix_factor, modulus) | (ancilla_qureg,
                                                        work_qureg)

    # Done done done.
    return f


sim = Simulator()
ctr = ResourceCounter()
eng = MainEngine(backend=sim, engine_list=[
    AutoReplacer(DecompositionRuleSet(modules=[
        addition_rules,
        increment_rules,
        modular_addition_rules,
        modular_bimultiplication_rules,
        modular_double_rules,
        modular_scaled_addition_rules,
        multi_not_rules,
        offset_rules,
        pivot_flip_rules,
        reverse_bits_rules,
        rotate_bits_rules,
        swap2cnot
    ])),
    LimitedCapabilityEngine(
        allow_toffoli=True,
        allow_single_qubit_gates=True,
    ),
    ctr
])

m = 7 * 11
n = int(math.ceil(math.log(m, 2)))
sample_period(eng,
              factor=3,
              modulus=m,
              precision=1,
              phase_qubit=eng.allocate_qubit(),
              work_qureg=eng.allocate_qureg(n),
              ancilla_qureg=eng.allocate_qureg(n))
print('{}'.format(ctr))
