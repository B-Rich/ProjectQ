# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import random

from projectq import MainEngine
from projectq.backends import ClassicalSimulator
from projectq.backends._circuits._to_ascii import commands_to_ascii_circuit
from projectq.cengines import DummyEngine
from projectq.ops import X


def fuzz_permutation_against_circuit(register_sizes,
                                     outputs_for_input,
                                     engine_list,
                                     actions,
                                     register_limits=None):
    n = len(register_sizes)
    if register_limits is None:
        register_limits = [1 << size for size in register_sizes]
    inputs = [random.randint(0, limit - 1) for limit in register_limits]
    outputs = [e % (1 << d)
               for e, d in zip(outputs_for_input(*inputs), register_sizes)]

    backend = ClassicalSimulator()
    eng = MainEngine(backend=backend, engine_list=engine_list)

    # Encode inputs.
    registers = [eng.allocate_qureg(size) for size in register_sizes]
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
