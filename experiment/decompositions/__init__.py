import addition_rules
import bootstrap_ancilla_rules
import increment_rules
import modular_bimultiplication_rules
import multi_not_rules
import phase_gradient_rules
import reverse_bits_rules
import rotate_bits_rules

all_defined_decomposition_rules = [
    rule
    for module in [
        addition_rules,
        bootstrap_ancilla_rules,
        increment_rules,
        modular_bimultiplication_rules,
        multi_not_rules,
        phase_gradient_rules,
        reverse_bits_rules,
        rotate_bits_rules,
    ]
    for rule in module.all_defined_decomposition_rules
]
