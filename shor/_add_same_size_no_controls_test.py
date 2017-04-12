# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.backends import Simulator
from projectq.cengines import DummyEngine, AutoReplacer, DecompositionRuleSet
from projectq.ops import Allocate, Swap, X, C
from shor._add_same_size_no_controls import do_addition_with_same_size_and_no_controls


def test_exact_commands_for_small_circuit():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    src = eng.allocate_qureg(2)
    dst = eng.allocate_qureg(2)
    do_addition_with_same_size_and_no_controls(eng, src, dst)

    a, c = src[0], src[1]
    x, y = dst[0], dst[1]
    assert backend.received_commands == [cmd for cmds in [
        Allocate.generate_commands(a),
        Allocate.generate_commands(c),
        Allocate.generate_commands(x),
        Allocate.generate_commands(y),
        C(X).generate_commands((c, a)),
        C(X).generate_commands((c, x)),
        C(X).generate_commands((c, y)),
        C(X).generate_commands((c, x)),
        C(Swap).generate_commands((x, a, c)),
        C(X).generate_commands((c, y)),
        C(Swap).generate_commands((x, a, c)),
        C(X).generate_commands((a, x)),
        C(X).generate_commands((c, a)),
        C(X).generate_commands((c, x)),
        C(X).generate_commands((c, y)),
    ] for cmd in cmds]


def test_equivalence_to_expected_permutation_by_fuzzing():
    from projectq.setups.decompositions import swap2cnot
    for _ in range(10):
        reg_size = 5
        limit = 1 << reg_size
        src_in = random.randint(0, limit - 1)
        dst_in = random.randint(0, limit - 1)
        src_out = src_in
        dst_out = (src_in + dst_in) % limit

        backend = Simulator()
        eng = MainEngine(backend=backend, engine_list=[
            AutoReplacer(DecompositionRuleSet(modules=[swap2cnot]))
        ])

        # Encode inputs.
        src = eng.allocate_qureg(reg_size)
        dst = eng.allocate_qureg(reg_size)
        for i in range(reg_size):
            if src_in & (1 << i):
                X | src[i]
            if dst_in & (1 << i):
                X | dst[i]

        # Simulate.
                do_addition_with_same_size_and_no_controls(eng, src, dst)
        eng.flush()

        # Compare outputs.
        _, state = backend.cheat()
        assert state[src_out + (dst_out << reg_size)] == 1
