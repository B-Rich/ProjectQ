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
    multi_not_decompositions,
    addition_decompositions,
    increment_decompositions
)
from .addition_decompositions import (
    do_addition_with_same_size_and_no_controls
)
from .gates import Add, Subtract, MultiNot
from ._test_util import fuzz_permutation_circuit


def test_exact_commands_for_small_circuit():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    src = eng.allocate_qureg(2)
    dst = eng.allocate_qureg(2)
    backend.restart_recording()
    do_addition_with_same_size_and_no_controls(src, dst)

    a, c = src[0], src[1]
    x, y = dst[0], dst[1]
    assert backend.received_commands == [
        (MultiNot & c).generate_command(Qureg([y, x, a])),
        (X & c).generate_command(x),
        (Swap & x).generate_command((a, c)),
        (X & c).generate_command(y),
        (Swap & x).generate_command((a, c)),
        (X & a).generate_command(x),
        (MultiNot & c).generate_command(Qureg([a, x, y])),
    ]


def test_decompose_big_to_toffolis():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[
        AutoReplacer(DecompositionRuleSet(modules=[
            swap2cnot,
            multi_not_decompositions,
            addition_decompositions,
            increment_decompositions
        ])),
        LimitedCapabilityEngine(allow_nots_with_many_controls=True),
    ])
    src = eng.allocate_qureg(50)
    dst = eng.allocate_qureg(100)
    Add | (src, dst)

    assert 1000 < len(backend.received_commands) < 10000


def test_fuzz_add_same_size():
    for _ in range(10):
        n = random.randint(1, 100)
        fuzz_permutation_circuit(
            register_sizes=[n, n],
            expected_outs_for_ins=lambda a, b: (a, b + a),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    swap2cnot,
                    multi_not_decompositions,
                    addition_decompositions
                ])),
                LimitedCapabilityEngine(allow_toffoli=True)],
            actions=lambda eng, regs: Add | (regs[0], regs[1]))


def test_fuzz_subtract_into_large():
    for _ in range(10):
        n = random.randint(1, 15)
        e = random.randint(1, 15)
        fuzz_permutation_circuit(
            register_sizes=[n, n + e, 2],
            expected_outs_for_ins=lambda a, b, d: (a, b - a, d),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    swap2cnot,
                    multi_not_decompositions,
                    addition_decompositions,
                    increment_decompositions
                ])),
                LimitedCapabilityEngine(allow_toffoli=True)],
            actions=lambda eng, regs: Subtract | (regs[0], regs[1]))
