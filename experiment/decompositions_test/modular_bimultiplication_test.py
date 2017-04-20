# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

from projectq import MainEngine
from projectq.cengines import (DummyEngine,
                               AutoReplacer,
                               DecompositionRuleSet,
                               LimitedCapabilityEngine)
from ._test_util import fuzz_permutation_circuit
from ..decompositions import modular_bimultiplication_rules
from ..decompositions.modular_bimultiplication_rules import (
    do_bimultiplication
)
from ..gates import (
    ConstModularDoubleMultiplicationGate,
    ModularAdditionGate,
    ModularSubtractionGate,
    ModularScaledAdditionGate
)


def test_do_double_multiplication():
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=[])
    a = eng.allocate_qureg(4)
    b = eng.allocate_qureg(4)
    c = eng.allocate_qureg(3)

    backend.restart_recording()
    do_bimultiplication(
        ConstModularDoubleMultiplicationGate(3, 13), a, b, c)

    m = ModularScaledAdditionGate
    assert backend.received_commands == [
        (m(3, 13) & c).generate_command((a, b)),
        (m(4, 13) & c).generate_command((b, a)),
        (m(3, 13) & c).generate_command((a, b)),
        (ModularAdditionGate(13) & c).generate_command((b, a)),
        (ModularSubtractionGate(13) & c).generate_command((a, b)),
        (ModularAdditionGate(13) & c).generate_command((b, a)),
    ]


# def test_decompose_big_to_toffolis():
#     backend = DummyEngine(save_commands=True)
#     eng = MainEngine(backend=backend,engine_list=[
#         AutoReplacer(DecompositionRuleSet(modules=[
#             swap2cnot,
#             _multi_not_rules,
#             _addition_rules,
#             _increment_rules
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
        fuzz_permutation_circuit(
            register_sizes=[n, cn, n],
            register_limits=[mod, 1 << cn, mod],
            expected_outs_for_ins=lambda a, c, b:
                (a, c, b)
                if c != 2**cn - 1
                else (a*5 % 1001, c, b*801 % 1001),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    modular_bimultiplication_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_arithmetic=True,
                    allow_nots_with_many_controls=True,
                    ban_classes=[ConstModularDoubleMultiplicationGate]
                )
            ],
            actions=lambda eng, regs: op & regs[1] | (regs[0], regs[2]))
