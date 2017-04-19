# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.cengines import (LimitedCapabilityEngine,
                               AutoReplacer,
                               DecompositionRuleSet,
                               DummyEngine)
from projectq.setups.decompositions import swap2cnot
from . import (_addition_decompositions,
               _increment_decompositions,
               _multi_not_decompositions)
from ._addition_gates import Subtract
from ._increment_decompositions import (
    do_increment_with_no_controls_and_n_dirty
)
from ._increment_gates import Increment
from ._multi_not_gates import MultiNot
from ._test_util import fuzz_permutation_against_circuit


def test_do_increment_with_no_controls_and_n_dirty():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    target = eng.allocate_qureg(10)
    dirty = eng.allocate_qureg(10)
    backend.restart_recording()

    do_increment_with_no_controls_and_n_dirty(eng, target, dirty)

    assert backend.received_commands == [
        Subtract.generate_command((dirty, target)),
        MultiNot.generate_command(dirty),
        Subtract.generate_command((dirty, target)),
        MultiNot.generate_command(dirty),
    ]


def test_fuzz_do_increment_with_no_controls_and_n_dirty():
    for _ in range(10):
        fuzz_permutation_against_circuit(
            register_sizes=[4, 4],
            outputs_for_input=lambda a, b: (a + 1, b),
            engine_list=[AutoReplacer(DecompositionRuleSet(modules=[
                _addition_decompositions,
                _multi_not_decompositions,
                swap2cnot
            ]))],
            actions=lambda eng, regs:
                do_increment_with_no_controls_and_n_dirty(
                    eng,
                    target_reg=regs[0],
                    dirty_reg=regs[1]))


def test_decomposition_chain():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            _multi_not_decompositions,
            _increment_decompositions,
            _addition_decompositions,
            swap2cnot,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(40)
    target = eng.allocate_qureg(35)
    _ = eng.allocate_qureg(2)
    Increment & controls | target
    assert 1000 < len(backend.received_commands) < 10000


def test_fuzz_controlled_increment():
    for _ in range(10):
        n = random.randint(1, 30)
        control_size = random.randint(0, 3)
        satisfy = (1 << control_size) - 1
        fuzz_permutation_against_circuit(
            register_sizes=[control_size, n, 2],
            outputs_for_input=lambda c, t, d:
                (c, t + (1 if c == satisfy else 0), d),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    swap2cnot,
                    _multi_not_decompositions,
                    _increment_decompositions,
                    _addition_decompositions,
                ])),
                LimitedCapabilityEngine(allow_toffoli=True),
            ],
            actions=lambda eng, regs: Increment & regs[0] | regs[1])
