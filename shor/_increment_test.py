# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.cengines import LimitedCapabilityEngine, AutoReplacer, DecompositionRuleSet
from projectq.ops import X, All, C_star, XGate, Allocate, ClassicalInstructionGate
from projectq.setups.decompositions import swap2cnot
from . import _addition_decompositions, _increment_decompositions
from ._addition_gates import Subtract
from ._increment_gates import Increment
from ._increment_decompositions import do_increment_with_no_controls_and_n_dirty
from ._test_util import fuzz_permutation_against_circuit


# def test_exact_commands_for_trivial_case():
#     backend = DummyEngine(save_commands=True)
#     eng = MainEngine(backend=backend, engine_list=[])
#     target = eng.allocate_qureg(10)
#     dirty = eng.allocate_qureg(10)
#     backend.restart_recording()
#
#     do_increment_with_no_controls_and_n_dirty(eng, target, dirty)
#
#     assert backend.received_commands == [cmd for cmds in [
#         Subtract.generate_commands((dirty, target)),
#         All(X).generate_commands(dirty),
#         Subtract.generate_commands((dirty, target)),
#         All(X).generate_commands(dirty),
#     ] for cmd in cmds]
#
#
# def test_permutations_for_trivial_case():
#     for _ in range(10):
#         fuzz_permutation_against_circuit(
#             register_sizes=[4, 4],
#             outputs_for_input=lambda a, b: (a + 1, b),
#             engine_list=[AutoReplacer(DecompositionRuleSet(modules=[
#                 _addition_decompositions,
#                 swap2cnot
#             ]))],
#             actions=lambda eng, regs:
#                 do_increment_with_no_controls_and_n_dirty(
#                     eng,
#                     target_reg=regs[0],
#                     dirty_reg=regs[1]))


# def test_decomposition_chain():
#     from projectq.backends._circuits._to_ascii import commands_to_ascii_circuit
#     backend = LimitedCapabilityDummyEngine(
#         save_commands=True,
#         allow_toffoli=True)
#     eng = MainEngine(backend=backend, engine_list=[
#         AutoReplacer(DecompositionRuleSet(modules=[
#             _increment_decompositions,
#             _addition_decompositions,
#             swap2cnot,
#         ]))])
#     controls = eng.allocate_qureg(6)
#     target = eng.allocate_qureg(10)
#     dirty = eng.allocate_qureg(1)
#     C_star(Increment) | (controls, target)
#     print(commands_to_ascii_circuit(backend.received_commands))
#     assert False
#
#
# def test_permutations_for_general_case():
#     for _ in range(10):
#         fuzz_permutation_against_circuit(
#             register_sizes=[random.randint(0, 6), 2, 1],
#             outputs_for_input=lambda t, c, d:
#                 (t + (1 if c == 3 else 0), c, d),
#             engine_list=[AutoReplacer(DecompositionRuleSet(modules=[
#                 _increment_decompositions,
#                 _addition_decompositions,
#                 swap2cnot,
#             ]))],
#             actions=lambda eng, regs: C_star(Increment) | (regs[1], regs[0]))
