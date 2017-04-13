# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import random

from projectq.cengines import DummyEngine

from projectq import MainEngine
from projectq.backends import Simulator
from projectq.ops import X
from projectq.backends._circuits._to_ascii import commands_to_ascii_circuit


def fuzz_permutation_against_circuit(register_sizes,
                                     outputs_for_input,
                                     engine_list,
                                     actions):
    inputs = [random.randint(0, (1 << n) - 1) for n in register_sizes]
    outputs = [e % (1 << d)
               for e, d in zip(outputs_for_input(*inputs), register_sizes)]

    backend = Simulator()
    eng = MainEngine(backend=backend, engine_list=engine_list)

    # Encode inputs.
    registers = [eng.allocate_qureg(n) for n in register_sizes]
    for i in range(len(register_sizes)):
        for b in range(register_sizes[i]):
            if inputs[i] & (1 << b):
                X | registers[i][b]

    # Simulate.
    actions(eng, registers)
    eng.flush()

    # Compare outputs.
    _, state = backend.cheat()
    expected_output_state = 0
    for output, size in reversed(zip(outputs, register_sizes)):
        expected_output_state <<= size
        expected_output_state |= output
    assert state[expected_output_state] == 1


def actions_as_ascii_diagram(register_sizes, engine_list, actions):
    backend = DummyEngine(save_commands=True)
    eng = MainEngine(backend=backend, engine_list=engine_list)
    registers = [eng.allocate_qureg(n) for n in register_sizes]
    actions(eng, registers)
    eng.flush()
    return commands_to_ascii_circuit(backend.received_commands)
