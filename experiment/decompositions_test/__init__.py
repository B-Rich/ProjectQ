import addition

all_defined_decomposition_rules = [
    rule
    for module in [
        addition
    ]
    for rule in module.all_defined_decomposition_rules
]
