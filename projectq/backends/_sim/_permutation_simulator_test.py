from projectq import MainEngine
from projectq.ops import X, BasicMathGate
from ._permutation_simulator import PermutationSimulator


def test_simulator_triangle_increment():
    sim = PermutationSimulator()
    eng = MainEngine(sim, [])
    a = eng.allocate_qureg(5)

    assert sim.permutation_equals([a], lambda e: (e,))

    for i in range(5)[::-1]:
        X & a[:i] | a[i]

    assert not sim.permutation_equals([a], lambda e: (e,))
    assert sim.permutation_equals([a], lambda e: ((e + 1) & 0b11111,))

    for i in range(5)[::-1]:
        X & a[:i] | a[i]

    assert not sim.permutation_equals([a], lambda e: (e,))
    assert sim.permutation_equals([a], lambda e: ((e + 2) & 0b11111,))


def test_simulator_arithmetic():
    class Offset(BasicMathGate):
        def __init__(self, amount):
            BasicMathGate.__init__(self, lambda x: (x+amount,))

    class Sub(BasicMathGate):
        def __init__(self):
            BasicMathGate.__init__(self, lambda x, y: (x, y-x))

    sim = PermutationSimulator()
    eng = MainEngine(sim, [])
    a = eng.allocate_qureg(3)
    b = eng.allocate_qureg(4)

    Offset(2) | a
    assert sim.permutation_equals([a, b],
                                  lambda x, y: ((x + 2) & 0b111,
                                                y & 0b1111))
    assert not sim.permutation_equals([a, b],
                                      lambda x, y: ((x - 2) & 0b111,
                                                    y & 0b1111))

    Offset(3) | b
    assert sim.permutation_equals([a, b],
                                  lambda x, y: ((x + 2) & 0b111,
                                                (y + 3) & 0b1111))

    Offset(32 + 5) | b
    assert sim.permutation_equals([a, b],
                                  lambda x, y: ((x + 2) & 0b111,
                                                (y + 8) & 0b1111))

    Sub() | (a, b)
    assert sim.permutation_equals(
        [a, b],
        lambda x, y: ((x + 2) & 0b111,
                      (y + 8 - ((x+2) & 0b111)) & 0b1111))

    Sub() | (a, b)
    Sub() | (a, b)
    assert sim.permutation_equals(
        [a, b],
        lambda x, y: ((x + 2) & 0b111,
                      (y + 8 - 3*((x+2) & 0b111)) & 0b1111))
