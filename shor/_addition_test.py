# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import DummyEngine, AutoReplacer, DecompositionRuleSet
from projectq.ops import Allocate, Swap, X, C
from projectq.setups.decompositions import swap2cnot
from ._addition_decompositions import do_addition_with_same_size_and_no_controls
from ._test_util import fuzz_permutation_against_circuit


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
        C(X).generate_commands((c, y)),
        C(X).generate_commands((c, x)),
        C(X).generate_commands((c, a)),
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
    for _ in range(10):
        fuzz_permutation_against_circuit(
            register_sizes=[4, 4],
            outputs_for_input=lambda a, b: (a, b + a),
            engine_list=[AutoReplacer(DecompositionRuleSet(modules=[
                swap2cnot
            ]))],
            actions=lambda eng, regs:
                do_addition_with_same_size_and_no_controls(
                    eng,
                    input_reg=regs[0],
                    target_reg=regs[1]))
