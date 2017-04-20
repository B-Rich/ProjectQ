import numpy as np

from projectq.cengines import BasicEngine
from projectq.ops import (XGate,
                          BasicMathGate,
                          Measure,
                          FlushGate,
                          Allocate,
                          Deallocate)


class PermutationSimulator(BasicEngine):
    def __init__(self):
        BasicEngine.__init__(self)
        self._states = np.array([0], np.int32)

    def _get_permutation(self, quregs):
        n = sum(len(reg) for reg in quregs)
        if len(self._states) != 1 << n:
            raise ValueError("Need all allocated qubits.")

        result = np.zeros((1 << n, len(quregs)), np.int32)
        for i in range(len(quregs)):
            result[:, i] = self._get_partial_permutation(quregs[i])
        return result

    def _get_partial_permutation(self, qureg):
        return np.array(self._internal_order_to_given_order(
            self._states, qureg))

    def permutation_equals(self, quregs, permutation_func):
        actual = self._get_permutation(quregs)
        for i in range(len(self._states)):
            xs = []
            t = 0
            for reg in quregs:
                xs.append((i >> t) & ((1 << len(reg)) - 1))
                t += len(reg)
            if permutation_func(*xs) != tuple(actual[i]):
                return False
        return True

    def _internal_order_to_given_order(self, v, little_endian_qubits):
        return sum(
            ((v >> little_endian_qubits[i].id) & 1) << i
            for i in range(len(little_endian_qubits)))

    def _given_order_to_internal_order(self, v, little_endian_qubits):
        return sum(
            ((v >> i) & 1) << little_endian_qubits[i].id
            for i in range(len(little_endian_qubits)))

    def is_available(self, cmd):
        return (cmd.gate == Measure or
                cmd.gate == Allocate or
                cmd.gate == Deallocate or
                isinstance(cmd.gate, BasicMathGate) or
                isinstance(cmd.gate, FlushGate) or
                isinstance(cmd.gate, XGate))

    def receive(self, command_list):
        for cmd in command_list:
            self._handle(cmd)
        if not self.is_last_engine:
            self.send(command_list)

    def _apply_operation(self, controls, func):
        c = self._given_order_to_internal_order(
            (1 << len(controls)) - 1, controls)
        for i in range(len(self._states)):
            if self._states[i] & c == c:
                self._states[i] = func(self._states[i])

    def _handle(self, cmd):
        if (cmd.gate == Measure or
                isinstance(cmd.gate, FlushGate) or
                cmd.gate == Deallocate):
            return

        if cmd.gate == Allocate:
            new_id = cmd.qubits[0][0].id
            if not (0 <= new_id < 32):
                raise ValueError("Too many allocations.")
            n = len(self._states)
            self._states = np.resize(self._states, 2 * n)
            self._states[n:] += 1 << new_id
            return

        if isinstance(cmd.gate, XGate):
            assert len(cmd.qubits) == 1 and len(cmd.qubits[0]) == 1
            target = cmd.qubits[0][0]
            self._apply_operation(cmd.control_qubits,
                                  lambda x: x ^ (1 << target.id))
            return

        if isinstance(cmd.gate, BasicMathGate):
            def reordered_op(v):
                xs = [self._internal_order_to_given_order(v, reg)
                      for reg in cmd.qubits]
                ys = cmd.gate.get_math_function(None)(xs)
                pys = [
                    self._given_order_to_internal_order(
                        y & ((1 << len(reg)) - 1),
                        reg)
                    for y, reg in zip(ys, cmd.qubits)
                ]
                pxs = [
                    self._given_order_to_internal_order(x, reg)
                    for x, reg in zip(xs, cmd.qubits)
                ]
                return v + sum(pys) - sum(pxs)
            self._apply_operation(cmd.control_qubits, reordered_op)
            return

        raise ValueError("Only support alloc/dealloc/measure/not/math ops.")
