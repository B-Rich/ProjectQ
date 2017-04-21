from projectq.ops import BasicMathGate


class BasicMathGate2(BasicMathGate):
    def __init__(self):
        def do_not_call(*_):
            raise AssertionError()
        BasicMathGate.__init__(self, do_not_call)

    def do_operation(self, *args):
        raise NotImplementedError()

    def get_math_function(self, qubits):
        return lambda x: self.do_operation(*x)
