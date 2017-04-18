# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.cengines import (DummyEngine,
                               AutoReplacer,
                               DecompositionRuleSet,
                               LimitedCapabilityEngine)
from projectq.ops import Swap, X
from projectq.setups.decompositions import swap2cnot
from projectq.types import Qureg
from . import (
    _multi_not_decompositions,
    _addition_decompositions,
    _increment_decompositions
)
from ._addition_decompositions import (
    do_addition_with_same_size_and_no_controls
)
from ._addition_gates import Add, Subtract
from ._multi_not_gates import MultiNot
from ._test_util import fuzz_permutation_against_circuit


def test_exact_commands_for_small_circuit():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    src = eng.allocate_qureg(2)
    dst = eng.allocate_qureg(2)
    backend.restart_recording()
    with eng.pipe_operations_into_receive():
        do_addition_with_same_size_and_no_controls(src, dst)

    a, c = src[0], src[1]
    x, y = dst[0], dst[1]
    assert backend.received_commands == [cmd for cmds in [
        (MultiNot & c).generate_commands(eng, Qureg([y, x, a])),
        (X & c).generate_commands(eng, x),
        (Swap & x).generate_commands(eng, (a, c)),
        (X & c).generate_commands(eng, y),
        (Swap & x).generate_commands(eng, (a, c)),
        (X & a).generate_commands(eng, x),
        (MultiNot & c).generate_commands(eng, Qureg([a, x, y])),
    ] for cmd in cmds]


def test_decompose_big_to_toffolis():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            swap2cnot,
            _multi_not_decompositions,
            _addition_decompositions,
            _increment_decompositions
        ])),
        LimitedCapabilityEngine(allow_nots_with_many_controls=True),
    ])
    src = eng.allocate_qureg(50)
    dst = eng.allocate_qureg(100)
    with eng.pipe_operations_into_receive():
        Add | (src, dst)

    assert 1000 < len(backend.received_commands) < 10000


def test_fuzz_add_same_size():
    for _ in range(10):
        n = random.randint(1, 100)
        fuzz_permutation_against_circuit(
            register_sizes=[n, n],
            outputs_for_input=lambda a, b: (a, b + a),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    swap2cnot,
                    _multi_not_decompositions,
                    _addition_decompositions
                ])),
                LimitedCapabilityEngine(allow_toffoli=True)],
            actions=lambda eng, regs: Add | (regs[0], regs[1]))


def test_fuzz_subtract_into_large():
    for _ in range(10):
        n = random.randint(1, 15)
        e = random.randint(1, 15)
        fuzz_permutation_against_circuit(
            register_sizes=[n, n + e, 2],
            outputs_for_input=lambda a, b, d: (a, b - a, d),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    swap2cnot,
                    _multi_not_decompositions,
                    _addition_decompositions,
                    _increment_decompositions
                ])),
                LimitedCapabilityEngine(allow_toffoli=True)],
            actions=lambda eng, regs: Subtract | (regs[0], regs[1]))
