#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from projectq.ops import BasicGate, Command


class ThisIsNotAGateClassError(TypeError):
    pass


class DecompositionRule:
    """
    A rule for breaking down specific gates into sequences of simpler gates.
    """

    def __init__(self,
                 gate_class,
                 gate_decomposer,
                 custom_predicate=lambda cmd: True,
                 min_workspace=0,
                 max_workspace=float('inf'),
                 max_controls=float('infinity'),
                 min_controls=0):
        """
        Args:
            gate_class (type): The type of gate that this rule decomposes.

                The gate class is redundant information used to make lookups
                faster when iterating over a circuit and deciding "which rules
                apply to this gate?" again and again.

                Note that this parameter is a gate type, not a gate instance.
                You supply gate_class=MyGate or gate_class=MyGate().__class__,
                not gate_class=MyGate().

            gate_decomposer (function[Command]): Function which,
                given the command to decompose, applies a sequence of gates
                corresponding to the high-level function of a gate of type
                gate_class.

            min_workspace (int):
                When this many 'workspace qubits' aren't already allocated and
                available, the decomposition won't be used.

            max_workspace (int):
                When more than this many 'workspace qubits' are available,
                the decomposition won't be used.

            max_controls (int|infinity):
                When a command has more than this many controls, the
                decomposition won't be used.

            custom_predicate (function[Command] : boolean):
                A function that determines if the decomposition applies to the
                given command (on top of the filtering by gate_class).

                For example, a decomposition rule may only to apply rotation
                gates that rotate by a specific angle.

                If no gate_recognizer is given, the decomposition applies to
                all gates matching the gate_class.
        """

        # Check for common gate_class type mistakes.
        if isinstance(gate_class, BasicGate):
            raise ThisIsNotAGateClassError(
                "gate_class is a gate instance instead of a type of BasicGate."
                "\nDid you pass in someGate instead of someGate.__class__?")
        if gate_class == type.__class__:
            raise ThisIsNotAGateClassError(
                "gate_class is type.__class__ instead of a type of BasicGate."
                "\nDid you pass in GateType.__class__ instead of GateType?")

        self.gate_class = gate_class
        self.gate_decomposer = gate_decomposer
        self._min_extra_space = min_workspace
        self._max_extra_space = max_workspace
        self._max_controls = max_controls
        self._min_controls = min_controls
        self._custom_predicate = custom_predicate

    def can_apply_to_command(self, command):
        """
        Args:
            command (Command): The command to potentially decompose.
        Returns:
            bool: If this decomposition rule can be applied to the command.
        """
        if not isinstance(command.gate, self.gate_class):
            return False

        controls = len(command.control_qubits)
        if controls < self._min_controls:
            return False
        if controls > self._max_controls:
            return False

        extra_space = len(command.untouched_qubits())
        if extra_space < self._min_extra_space:
            return False
        if extra_space > self._max_extra_space:
            return False

        return self._custom_predicate(command)
