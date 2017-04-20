# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cmath
import math
import random

import numpy as np

from projectq import MainEngine
from projectq.backends import CircuitDrawer
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
    sim = Simulator()
    eng = MainEngine(backend=sim, engine_list=engine_list)
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Simulate all.
    for reg in registers:
        for q in reg:
            H | q
    actions(eng, registers)

    # Compare.
    state = sim.cheat()[1]
    for i in range(len(state)):
        vals = []
        t = 0
        for r in register_sizes:
            vals.append((i >> t) & ((1 << r) - 1))
            t += r
        vals = tuple(vals)

        actual_factor = state[i]
        expected_turn = expected_turns(vals, register_sizes)
        actual_turn = cmath.phase(state[i]) / (2 * math.pi)
        delta_turn = abs((actual_turn - expected_turn + 0.5) % 1 - 0.5)
        if not (delta_turn < 0.00001):
            print(actions_as_ascii_diagram(
                register_sizes, engine_list, actions))
            print("Register Sizes", register_sizes)
            print("Conflicting state: {}".format(vals))
            print("Expected phase: {} deg".format(float(expected_turn)*360))
            print("Actual phase: {} deg".format(actual_turn*360))
        assert abs(abs(actual_factor * math.sqrt(len(state))) - 1) < 0.00001
        assert delta_turn < 0.00001


def check_permutation_circuit(register_sizes,
                              expected_outs_for_ins,
                              engine_list,
                              actions):

    backend = PermutationSimulator()
    eng = MainEngine(backend=backend, engine_list=engine_list)
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Simulate.
    actions(eng, registers)

    # Compare.
    permutation_matches = backend.permutation_equals(registers,
                                                     expected_outs_for_ins)
    if not permutation_matches:
        print(actions_as_ascii_diagram(register_sizes, engine_list, actions))
        print("Register Sizes", register_sizes)
    assert permutation_matches


def check_quantum_permutation_circuit(register_size,
                                      permutation_func,
                                      engine_list,
                                      actions):
    sim = Simulator()
    eng = MainEngine(backend=sim, engine_list=engine_list)

    reg = eng.allocate_qureg(register_size)

    All(H) | reg
    for i in range(len(reg)):
        Rz(math.pi / 2**i) | reg[i]
    pre_state = np.array(sim.cheat()[1])

    actions(eng, [reg])

    post_state = np.array(sim.cheat()[1])
    for q in reg:
        Measure | q

    denom = math.sqrt(len(pre_state))
    pre_state *= denom
    post_state *= denom
    for i in range(len(pre_state)):
        j = permutation_func(i) & ((1 << len(reg)) - 1)
        if not (abs(post_state[j] - pre_state[i]) < 0.000000001):
            print(actions_as_ascii_diagram(
                [register_size], engine_list, actions))
            print("Input", i)
            print("Expected Output", j)
            print("Input Amp at " + str(i), pre_state[i])
            print("Actual Amp at " + str(j), post_state[j])
        assert abs(post_state[j] - pre_state[i]) < 0.000000001


def fuzz_permutation_circuit(register_sizes,
                             expected_outs_for_ins,
                             engine_list,
                             actions,
                             register_limits=None):
    n = len(register_sizes)
    if register_limits is None:
        register_limits = [1 << size for size in register_sizes]
    inputs = [random.randint(0, limit - 1) for limit in register_limits]
    outputs = [e % (1 << d)
               for e, d in zip(expected_outs_for_ins(*inputs), register_sizes)]

    backend = ClassicalSimulator()
    eng = MainEngine(backend=backend, engine_list=engine_list)
    registers = [eng.allocate_qureg(size) for size in register_sizes]

    # Encode inputs.
    for i in range(n):
        for b in range(register_sizes[i]):
            if inputs[i] & (1 << b):
                X | registers[i][b]

    # Simulate.
    actions(eng, registers)

    # Compare outputs.
    actual_outputs = [backend.read_register(registers[i]) for i in range(n)]
    if outputs != actual_outputs:
        print(actions_as_ascii_diagram(register_sizes, engine_list, actions))
        print("Register Sizes", register_sizes)
        print("Inputs", inputs)
        print("Expected Outputs", outputs)
        print("Actual Outputs", actual_outputs)
    assert outputs == actual_outputs


def actions_as_ascii_diagram(register_sizes, engine_list, actions):
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=engine_list)
    registers = [eng.allocate_qureg(n) for n in register_sizes]
    actions(eng, registers)
    eng.flush()
    return commands_to_ascii_circuit(backend.received_commands)


def actions_as_latex_diagram(register_sizes, engine_list, actions):
    backend = CircuitDrawer()
    eng = MainEngine(backend=backend, engine_list=engine_list)
    registers = [eng.allocate_qureg(n) for n in register_sizes]
    actions(eng, registers)
    eng.flush()
    return backend.get_latex()
