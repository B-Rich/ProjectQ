# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import unicode_literals

import itertools
import random

from projectq.cengines import (LimitedCapabilityEngine,
                               AutoReplacer,
                               DecompositionRuleSet)
from ._test_util import (
    fuzz_permutation_circuit, check_permutation_circuit
)
from ..decompositions import (
    modular_double_rules, rotate_bits_rules, reverse_bits_rules
)
from ..gates import (
    ModularDoubleGate, ModularUndoubleGate, RotateBitsGate, ReverseBitsGate
)


def test_check_modular_double_permutations_small():
    for n, nc in itertools.product([2, 3, 4],
                                   [0, 1]):
        for modulus in range((1 << (n-1)) + 1, (1 << n) + 1)[::2]:
            check_permutation_circuit(
                register_sizes=[n, nc],
                register_limits=[modulus, 1 << nc],
                permutation=lambda _, (t, c):
                    (t * 2 % modulus if c + 1 == 1 << nc else t, c),
                engine_list=[
                    AutoReplacer(DecompositionRuleSet(modules=[
                        modular_double_rules,
                        rotate_bits_rules,
                        reverse_bits_rules,
                    ])),
                    LimitedCapabilityEngine(
                        allow_all=True,
                        ban_classes=[
                            ModularDoubleGate,
                            ModularUndoubleGate,
                            RotateBitsGate,
                            ReverseBitsGate,
                        ],
                    ),
                ],
                actions=lambda eng, regs:
                    ModularDoubleGate(modulus) & regs[1] | regs[0])


def test_fuzz_modular_double_permutations_large():
    for _ in range(10):
        n = random.randint(2, 50)
        nc = random.randint(0, 2)
        modulus = random.randint((1 << (n-1)) + 1, (1 << n) - 1)
        if modulus % 2 == 0:
            modulus += 1
        fuzz_permutation_circuit(
            register_sizes=[n, nc],
            register_limits=[modulus, 1 << nc],
            permutation=lambda _, (t, c):
                (t * 2 % modulus if c + 1 == 1 << nc else t, c),
            engine_list=[
                AutoReplacer(DecompositionRuleSet(modules=[
                    modular_double_rules,
                    rotate_bits_rules,
                    reverse_bits_rules,
                ])),
                LimitedCapabilityEngine(
                    allow_all=True,
                    ban_classes=[
                        ModularDoubleGate,
                        ModularUndoubleGate,
                        RotateBitsGate,
                        ReverseBitsGate,
                    ],
                ),
            ],
            actions=lambda eng, regs:
                ModularDoubleGate(modulus) & regs[1] | regs[0])
