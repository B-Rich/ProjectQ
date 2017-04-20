# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import (LimitedCapabilityEngine,
                               AutoReplacer,
                               DecompositionRuleSet)
from projectq.ops import X
from projectq.setups.decompositions import swap2cnot
from . import (
    quantum_ancilla_bootstrap_decompositions,
    phase_gradient_decompositions,
    increment_decompositions,
    multi_not_decompositions,
    addition_decompositions
)
from ._test_util import check_quantum_permutation_circuit
from .gates import Increment


def test_full_cnot_permutations_small():
    for n in [1, 2, 3, 4, 7, 9]:
        control_mask = ((1 << (n - 1)) - 1) << 1

        check_quantum_permutation_circuit(
            register_size=n,
            permutation_func=lambda i:
                i ^ (1 if control_mask & i == control_mask else 0),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    quantum_ancilla_bootstrap_decompositions,
                    phase_gradient_decompositions,
                    increment_decompositions,
                    multi_not_decompositions,
                    addition_decompositions,
                    swap2cnot,
                ])),
                LimitedCapabilityEngine(
                    allow_toffoli=True,
                    allow_single_qubit_gates=True
                ),
            ],
            actions=lambda eng, regs: X & regs[0][1:] | regs[0][0])


def test_full_increment_permutations_small():
    for n in [1, 2, 3, 4, 7, 9]:
        for c in [0, 1, 2]:
            control_mask = (1 << c) - 1

            check_quantum_permutation_circuit(
                register_size=c + n,
                permutation_func=lambda i:
                    i + (1 << c if control_mask & i == control_mask else 0),
                engine_list=[
                    AutoReplacer(DecompositionRuleSet(modules=[
                        quantum_ancilla_bootstrap_decompositions,
                        phase_gradient_decompositions,
                        increment_decompositions,
                        multi_not_decompositions,
                        addition_decompositions,
                        swap2cnot,
                    ])),
                    LimitedCapabilityEngine(
                        allow_toffoli=True,
                        allow_single_qubit_gates=True
                    ),
                ],
                actions=lambda eng, regs:
                    Increment & regs[0][:c] | regs[0][c:])
