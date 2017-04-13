# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.cengines import (LimitedCapabilityEngine,
                               AutoReplacer,
                               DecompositionRuleSet,
                               DummyEngine)
from projectq.ops import X, C_star, C
from . import _multi_not_decompositions
from ._multi_not_decompositions import (
    do_multi_not_with_one_big_not_and_friends,
    cut_not_max_controls_in_half,
    cut_not_max_controls_into_toffolis,
)
from ._multi_not_gates import MultiNot
from ._test_util import fuzz_permutation_against_circuit


def test_do_multi_not_with_one_big_not_and_friends():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    controls = eng.allocate_qureg(5)
    targets = eng.allocate_qureg(5)
    backend.restart_recording()

    do_multi_not_with_one_big_not_and_friends(targets, controls)

    assert backend.received_commands == [cmd for cmds in [
        C(X).generate_commands((targets[3], targets[4])),
        C(X).generate_commands((targets[2], targets[3])),
        C(X).generate_commands((targets[1], targets[2])),
        C(X).generate_commands((targets[0], targets[1])),
        C_star(X).generate_commands((controls, targets[0])),
        C(X).generate_commands((targets[0], targets[1])),
        C(X).generate_commands((targets[1], targets[2])),
        C(X).generate_commands((targets[2], targets[3])),
        C(X).generate_commands((targets[3], targets[4])),
    ] for cmd in cmds]


def test_cut_not_max_controls_in_half():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    controls = eng.allocate_qureg(8)
    target = eng.allocate_qureg(1)[0]
    dirty = eng.allocate_qureg(1)[0]
    backend.restart_recording()

    cut_not_max_controls_in_half(target, controls, dirty)

    assert backend.received_commands == [cmd for cmds in [
        C_star(X).generate_commands((controls[4:], dirty)),
        C_star(X).generate_commands((controls[:4] + [dirty], target)),
    ] for cmd in cmds] * 2


def test_cut_not_max_controls_into_toffolis():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    c = eng.allocate_qureg(4)
    target = eng.allocate_qureg(1)[0]
    d = eng.allocate_qureg(2)
    backend.restart_recording()

    cut_not_max_controls_into_toffolis(target, c, d)
    tof = C(X, 2)

    assert backend.received_commands == [cmd for cmds in [
        tof.generate_commands((d[1], c[3], target)),
        tof.generate_commands((d[0], c[2], d[1])),
        tof.generate_commands((c[0], c[1], d[0])),
        tof.generate_commands((d[0], c[2], d[1])),
    ] for cmd in cmds] * 2


def test_big_decomposition_chain_size():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            _multi_not_decompositions,
        ])),
        LimitedCapabilityEngine(allow_toffoli=True),
    ])
    controls = eng.allocate_qureg(200)
    targets = eng.allocate_qureg(150)
    C_star(MultiNot) | (controls, targets)
    assert 200*4*2 <= len(backend.received_commands) <= 200*4*4


def test_fuzz():
    for _ in range(10):
        targets = random.randint(2, 4)
        controls = random.randint(0, 4)
        fuzz_permutation_against_circuit(
            register_sizes=[targets, controls],
            outputs_for_input=lambda t, c:
                (t ^ (((1 << targets) - 1) if c+1 == 1 << controls else 0), c),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    _multi_not_decompositions,
                ])),
                LimitedCapabilityEngine(allow_toffoli=True),
            ],
            actions=lambda eng, regs: C_star(MultiNot) | (regs[1], regs[0]))
