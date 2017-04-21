# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmath
import math
import random

import numpy as np

from projectq import MainEngine
from projectq.backends import (
    ClassicalSimulator, PermutationSimulator, Simulator
)
from projectq.backends._circuits._to_ascii import commands_to_ascii_circuit
from projectq.cengines import DummyEngine
from projectq.ops import X, H, All, Rz, Measure


def check_phase_circuit(register_sizes,
                        expected_turns,
                        engine_list,
                        actions):
    """
    Args:
        register_sizes (list[int]):
        expected_turns (function(register_sizes: tuple[int],
                                 register_vals: tuple[int])):
        engine_list (list[projectq.cengines.BasicEngine]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
        register_limits (list[int]):
    """

    sim = Simulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=engine_list + [rec])
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Simulate all.
    for reg in registers:
        for q in reg:
            H | q
    rec.restart_recording()
    actions(eng, registers)

    state = np.array(sim.cheat()[1])
    magnitude_factor = math.sqrt(len(state))
    actions = list(rec.received_commands)
    for reg in registers:
        for q in reg:
            Measure | q

    # Compare.
    for i in range(len(state)):
        vals = []
        t = 0
        for r in register_sizes:
            vals.append((i >> t) & ((1 << r) - 1))
            t += r
        vals = tuple(vals)

        actual_factor = state[i]
        expected_turn = expected_turns(register_sizes, vals)
        actual_turn = cmath.phase(state[i]) / (2 * math.pi)
        delta_turn = abs((actual_turn - expected_turn + 0.5) % 1 - 0.5)
        if not (delta_turn < 0.00001):
            print(commands_to_ascii_circuit(actions))
            print("Register Sizes", register_sizes)
            print("Conflicting state: {}".format(vals))
            print("Expected phase: {} deg".format(float(expected_turn)*360))
            print("Actual phase: {} deg".format(actual_turn*360))
        assert abs(abs(actual_factor * magnitude_factor) - 1) < 0.00001
        assert delta_turn < 0.00001


def check_permutation_circuit(register_sizes,
                              permutation,
                              engine_list,
                              actions):
    """
    Args:
        register_sizes (list[int]):
        permutation (function(register_sizes: tuple[int],
                                        register_vals: tuple[int])
                                        : tuple[int]):
        engine_list (list[projectq.cengines.BasicEngine]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
    """

    sim = PermutationSimulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=engine_list + [rec])
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Simulate.
    actions(eng, registers)

    # Compare.
    permutation_matches = sim.permutation_equals(registers,
                                                 permutation)
    if not permutation_matches:
        example_count = 0
        print(commands_to_ascii_circuit(rec.received_commands))
        print("Register Sizes", register_sizes)
        print("Differing Permutations [input --> actual != expected]:")
        starts = PermutationSimulator.starting_permutation(register_sizes)
        for a, b in zip(starts, sim.get_permutation(registers)):
            b = list(b)
            c = permutation(register_sizes, a)
            c = [i & ((1 << v) - 1) for i, v in zip(c, register_sizes)]
            if not np.array_equal(c, b):
                example_count += 1
                if example_count > 10:
                    print("   (...)")
                    break
                a = tuple(a)
                b = tuple(b)
                c = tuple(c)
                print("   " + str(a) + " --> " + str(b) + " != " + str(c))
    assert permutation_matches


def bit_to_state_permutation(bit_permutation):
    """
    Args:
        bit_permutation (function(reg_sizes: tuple[int],
                                  bit_position: int,
                                  other_vals: tuple[int]) : int):

    Returns:
        function(reg_sizes: tuple[int], reg_vals: tuple[int]) : tuple[int]):
    """
    def permute(sizes, vals):
        permuted = sum(
            ((vals[0] >> i) & 1) << bit_permutation(sizes, i, vals[1:])
            for i in range(sizes[0]))
        return (permuted,) + tuple(vals[1:])
    return permute


def check_quantum_permutation_circuit(register_size,
                                      permutation_func,
                                      engine_list,
                                      actions):
    """
    Args:
        register_size (int):
        permutation_func (function(register_sizes: tuple[int],
                                   register_vals: tuple[int]) : tuple[int]):
        engine_list (list[projectq.cengines.BasicEngine]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
    """
    sim = Simulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=engine_list + [rec])

    reg = eng.allocate_qureg(register_size)

    All(H) | reg
    for i in range(len(reg)):
        Rz(math.pi / 2**i) | reg[i]
    pre_state = np.array(sim.cheat()[1])

    # Simulate.
    rec.restart_recording()
    actions(eng, [reg])
    actions = list(rec.received_commands)

    post_state = np.array(sim.cheat()[1])
    for q in reg:
        Measure | q

    denom = math.sqrt(len(pre_state))
    pre_state *= denom
    post_state *= denom
    for i in range(len(pre_state)):
        j = permutation_func([register_size], [i]) & ((1 << len(reg)) - 1)
        if not (abs(post_state[j] - pre_state[i]) < 0.000000001):
            print(commands_to_ascii_circuit(actions))
            print("Input", i)
            print("Expected Output", j)
            print("Input Amp at " + str(i), pre_state[i])
            print("Actual Amp at " + str(j), post_state[j])
        assert abs(post_state[j] - pre_state[i]) < 0.000000001


def fuzz_permutation_circuit(register_sizes,
                             permutation,
                             engine_list,
                             actions,
                             register_limits=None):
    """
    Args:
        register_sizes (list[int]):
        permutation (function(register_vals: tuple[int],
                                        register_sizes: tuple[int])
                                        : tuple[int]):
        engine_list (list[projectq.cengines.BasicEngine]):
        actions (function(eng: MainEngine, registers: list[Qureg])):
        register_limits (list[int]):
    """

    n = len(register_sizes)
    if register_limits is None:
        register_limits = [1 << size for size in register_sizes]
    inputs = [random.randint(0, limit - 1) for limit in register_limits]
    outputs = [e % (1 << d)
               for e, d in zip(permutation(register_sizes, inputs),
                               register_sizes)]

    sim = ClassicalSimulator()
    rec = DummyEngine(save_commands=True)
    eng = MainEngine(backend=sim, engine_list=engine_list + [rec])
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Encode inputs.
    for i in range(n):
        for b in range(register_sizes[i]):
            if inputs[i] & (1 << b):
                X | registers[i][b]

    # Simulate.
    rec.restart_recording()
    actions(eng, registers)

    # Compare outputs.
    actual_outputs = [sim.read_register(registers[i]) for i in range(n)]
    if outputs != actual_outputs:
        print(commands_to_ascii_circuit(rec.received_commands))
        print("Register Sizes", register_sizes)
        print("Inputs", inputs)
        print("Expected Outputs", outputs)
        print("Actual Outputs", actual_outputs)
    assert outputs == actual_outputs
