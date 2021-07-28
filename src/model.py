class Table:
    def __init__(self, name, chains):
        self.name = name
        self.chains = chains

    def __str__(self):
        return f'Table {{ {self.name}, {str(self.chains)} }}'

    def __repr__(self):
        return self.__str__()


class Chain:
    def __init__(self, name, rules, is_default=False, default_policy='ACCEPT'):
        self.name = name
        self.rules = rules
        self.is_default = is_default
        self.default_policy = default_policy

    def __str__(self):
        return f'Chain {{ {self.name}, {self.is_default}, {self.default_policy}, {str(self.rules)} }}'

    def __repr(self):
        return self.__str__()


class Rule:
    def __init__(self, l3_protocol, l4_protocol, source_address, destination_address,
            in_interface, out_interface, match_module, match_parameters, action,
            target_module, target_parameters, raw):
        self.l3_protocol = l3_protocol
        self.l4_protocol = l4_protocol
        self.source_address = source_address
        self.destination_address = destination_address
        self.in_interface = in_interface
        self.out_interface = out_interface
        self.match_module = match_module
        self.match_parameters = match_parameters
        self.action = action
        self.target_module = target_module
        self.target_parameters = target_parameters
        self.raw = raw

    def __str__(self):
        return f'Rule {{ {self.l3_protocol}, {self.l4_protocol}, {self.source_address}, {self.destination_address}, {self.in_interface}, {self.out_interface}, {self.match_module}, {self.match_parameters}, {self.action}, {self.target_module}, {self.target_parameters}, {self.raw} }}'

    def __repr__(self):
        return self.__str__()


