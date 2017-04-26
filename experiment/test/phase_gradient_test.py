# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq.cengines import AutoReplacer, DecompositionRuleSet
from ._test_util import check_phase_circuit
from ..decompositions import phase_gradient_rules
from ..extensions.limited_capability_engine import LimitedCapabilityEngine
from ..gates import PhaseGradient


def test_circuit_implements_phase_angle_specified_by_gate():
    check_phase_circuit(
        register_sizes=[8],
        expected_turns=lambda lens, vals:
            PhaseGradient.phase_angle_in_turns_for(vals[0], lens[0]),
        engine_list=[
            AutoReplacer(DecompositionRuleSet(modules=[
                phase_gradient_rules
            ])),
            LimitedCapabilityEngine(
                allow_single_qubit_gates=True
            )
        ],
        actions=lambda eng, regs: PhaseGradient | regs[0])


def test_controlled_circuit():
    check_phase_circuit(
        register_sizes=[5, 2],
        expected_turns=lambda (ns, nc), (s, c):
            s/2**ns/-4 if c + 1 == 1 << nc else 0,
        engine_list=[
            AutoReplacer(DecompositionRuleSet(modules=[
                phase_gradient_rules
            ])),
            LimitedCapabilityEngine(
                allow_single_qubit_gates_with_controls=True
            )
        ],
        actions=lambda eng, regs: PhaseGradient**(-1/4) & regs[1] | regs[0])
