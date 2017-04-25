class _CommandPredicate(object):
    """
    Utility base class for predicates that can be combined with & and |.
    """
    def __call__(self, cmd):
        raise NotImplementedError()

    def __and__(self, other):
        return _CommandPredicateCombinator([self, other], all, 'all')

    def __or__(self, other):
        return _CommandPredicateCombinator([self, other], any, 'any')


class _CommandPredicateCombinator(_CommandPredicate):
    def __init__(self, predicates, combinator, combinator_desc):
        self.predicates = predicates
        self.combinator = combinator
        self.combinator_desc = combinator_desc

    def __call__(self, cmd):
        return self.combinator(predicate(cmd) for predicate in self.predicates)

    def __str__(self):
        return '{}({})'.format(self.combinator_desc,
                               ', '.join(str(e) for e in self.predicates))


class _CommandPredicateLambda(_CommandPredicate):
    def __init__(self, predicate, desc):
        self.predicate = predicate
        self.desc = desc

    def __call__(self, cmd):
        return self.predicate(cmd)

    def __str__(self):
        return self.desc()


def min_controls(limit):
    return _CommandPredicateLambda(
        predicate=lambda cmd: len(cmd.control_qubits) >= limit,
        desc=lambda: 'min_controls({})'.format(limit))


def max_controls(limit):
    return _CommandPredicateLambda(
        predicate=lambda cmd: len(cmd.control_qubits) <= limit,
        desc=lambda: 'max_controls({})'.format(limit))


def max_register_sizes(*limits):
    return _CommandPredicateLambda(
        predicate=lambda cmd:
            len(cmd.qubits) == len(limits) and
            all(len(r) <= n for r, n in zip(cmd.qubits, limits)),
        desc=lambda:
            'max_register_sizes({})'.format(', '.join(str(e) for e in limits)))


def min_register_sizes(*limits):
    return _CommandPredicateLambda(
        predicate=lambda cmd:
            len(cmd.qubits) == len(limits) and
            all(len(r) >= n for r, n in zip(cmd.qubits, limits)),
        desc=lambda:
            'min_register_sizes({})'.format(', '.join(str(e) for e in limits)))


def min_workspace(limit):
    return _CommandPredicateLambda(
        predicate=lambda cmd: len(cmd.untouched_qubits()) >= limit,
        desc=lambda: 'min_workspace({})'.format(limit()))


def min_workspace_vs_controls(factor, offset=0):
    return _CommandPredicateLambda(
        predicate=lambda cmd:
        len(cmd.untouched_qubits()) >= offset + factor*len(cmd.control_qubits),
        desc=lambda: 'min_workspace({}, {})'.format(offset, factor))


def min_workspace_vs_reg1(factor, offset=0):
    return _CommandPredicateLambda(
        predicate=lambda cmd:
        len(cmd.untouched_qubits()) >= offset + factor*len(cmd.qubits[0]),
        desc=lambda: 'min_workspace({}, {})'.format(offset, factor))


def max_workspace(limit):
    return _CommandPredicateLambda(
        predicate=lambda cmd: len(cmd.untouched_qubits()) <= limit,
        desc=lambda: 'max_workspace({})'.format(limit()))
