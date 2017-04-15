# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import (DummyEngine,
                               AutoReplacer,
                               DecompositionRuleSet,
                               LimitedCapabilityEngine)
from . import (
    _const_modular_double_multiplication_decompositions
)
from ._const_modular_double_multiplication_decompositions import (
    do_double_multiplication
)
from ._const_modular_double_multiplication_gates import (
    ConstModularDoubleMultiplicationGate
)
from ._modular_addition_gates import (
    ModularAdditionGate, ModularSubtractionGate
)
from ._modular_scaled_addition_gates import ModularScaledAdditionGate
from ._test_util import fuzz_permutation_against_circuit


def test_do_double_multiplication():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    a = eng.allocate_qureg(4)
    b = eng.allocate_qureg(4)
    c = eng.allocate_qureg(3)

    backend.restart_recording()
    with eng.pipe_operations_into_receive():
        do_double_multiplication(
            ConstModularDoubleMultiplicationGate(3, 13), a, b, c)

    m = ModularScaledAdditionGate
    assert backend.received_commands == [cmd for cmds in [
        (m(3, 13) & c).generate_commands((a, b)),
        (m(4, 13) & c).generate_commands((b, a)),
        (m(3, 13) & c).generate_commands((a, b)),
        (ModularAdditionGate(13) & c).generate_commands((b, a)),
        (ModularSubtractionGate(13) & c).generate_commands((a, b)),
        (ModularAdditionGate(13) & c).generate_commands((b, a)),
    ] for cmd in cmds]


# def test_decompose_big_to_toffolis():
#     backend = DummyEngine(save_commands=True)
#     eng = MainEngine(backend=backend,engine_list=[
#         AutoReplacer(DecompositionRuleSet(modules=[
#             swap2cnot,
#             _multi_not_decompositions,
#             _addition_decompositions,
#             _increment_decompositions
#         ])),
#         LimitedCapabilityEngine(allow_nots_with_many_controls=True),
#     ])
#     src = eng.allocate_qureg(50)
#     dst = eng.allocate_qureg(100)
#     Add | (src, dst)
#
#     assert 1000 < len(backend.received_commands) < 10000


def test_fuzz_double_multiplication():
    for _ in range(100):
        n = 10
        cn = 1
        mod = 1001
        op = ConstModularDoubleMultiplicationGate(5, mod)
        fuzz_permutation_against_circuit(
            register_sizes=[n, cn, n],
            register_limits=[mod, 1 << cn, mod],
            outputs_for_input=lambda a, c, b:
                (a, c, b)
                if c != 2**cn - 1
                else (a*5 % 1001, c, b*801 % 1001),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    _const_modular_double_multiplication_decompositions,
                ])),
                LimitedCapabilityEngine(
                    allow_arithmetic=True,
                    allow_nots_with_many_controls=True,
                    ban_classes=[ConstModularDoubleMultiplicationGate]
                )
            ],
            actions=lambda eng, regs: op & regs[1] | (regs[0], regs[2]))
