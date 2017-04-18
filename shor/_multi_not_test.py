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

    with eng.pipe_operations_into_receive():
        do_multi_not_with_one_big_not_and_friends(targets, controls)

    assert backend.received_commands == [cmd for cmds in [
        C(X).generate_commands(eng, (targets[3], targets[4])),
        C(X).generate_commands(eng, (targets[2], targets[3])),
        C(X).generate_commands(eng, (targets[1], targets[2])),
        C(X).generate_commands(eng, (targets[0], targets[1])),
        (X & controls).generate_commands(eng, targets[0]),
        C(X).generate_commands(eng, (targets[0], targets[1])),
        C(X).generate_commands(eng, (targets[1], targets[2])),
        C(X).generate_commands(eng, (targets[2], targets[3])),
        C(X).generate_commands(eng, (targets[3], targets[4])),
    ] for cmd in cmds]


def test_do_multi_not_with_one_big_not_and_friends_trivial():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    controls = eng.allocate_qureg(1)
    targets = eng.allocate_qureg(4)
    backend.restart_recording()

    with eng.pipe_operations_into_receive():
        do_multi_not_with_one_big_not_and_friends(targets, controls)

    assert backend.received_commands == [cmd for cmds in [
        (X & controls).generate_commands(eng, targets[0]),
        (X & controls).generate_commands(eng, targets[1]),
        (X & controls).generate_commands(eng, targets[2]),
        (X & controls).generate_commands(eng, targets[3]),
    ] for cmd in cmds]


def test_cut_not_max_controls_in_half():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    controls = eng.allocate_qureg(8)
    target = eng.allocate_qureg(1)[0]
    dirty = eng.allocate_qureg(1)[0]
    backend.restart_recording()

    with eng.pipe_operations_into_receive():
        cut_not_max_controls_in_half(target, controls, dirty)

    assert backend.received_commands == [cmd for cmds in [
        (X & controls[4:]).generate_commands(eng, dirty),
        (X & controls[:4] + [dirty]).generate_commands(eng, target),
    ] for cmd in cmds] * 2


def test_cut_not_max_controls_into_toffolis():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    c = eng.allocate_qureg(4)
    target = eng.allocate_qureg(1)[0]
    d = eng.allocate_qureg(2)
    backend.restart_recording()

    with eng.pipe_operations_into_receive():
        cut_not_max_controls_into_toffolis(target, c, d)

    assert backend.received_commands == [cmd for cmds in [
        (X & d[1] & c[3]).generate_commands(eng, target),
        (X & d[0] & c[2]).generate_commands(eng, d[1]),
        (X & c[0] & c[1]).generate_commands(eng, d[0]),
        (X & d[0] & c[2]).generate_commands(eng, d[1]),
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
    with eng.pipe_operations_into_receive():
        MultiNot & controls | targets
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
