import sys
import pprint
import re
import json


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


def parse_tables_and_chains(contents):
    ret = {}
    current_table = None
    for line in contents.splitlines():
        # clean input: remove comments, empty lines, COMMIT lines
        if line.startswith('#') or line.startswith('COMMIT') or len(line.strip()) == 0:
            continue
        
        if line.startswith('*'):
            current_table = line.strip()[1:]
            ret[current_table] = {}
            continue
        elif not current_table:
            print(f'Cannot parse line without table: {line}. Stop.')
            sys.exit(1)

        if line.startswith(':'):
            fields = line.strip()[1:].split()
            chain = fields[0]
            ret[current_table][chain] = {}
            ret[current_table][chain]['default_policy'] = fields[1]
            ret[current_table][chain]['raw_rules'] = []
            continue

        if not line.startswith('-A '):
            print(f'don\'t know what to do with line {line}. Stop.')
            sys.exit(1)
        chain = line[3:].split()[0]
        ret[current_table][chain]['raw_rules'].append(' '.join(line.split()[2:]))

    return ret


def parse_rules(raw_dict, version):
    for table, tc in raw_dict.items():
        for chain in tc:
            raw_dict[table][chain]['rules'] = []
            for r in raw_dict[table][chain]['raw_rules']:
                l3_protocol = version
                
                # l4_protocol
                m = re.search(r'-p\s+(\S+)', r)
                l4_protocol = m.group(1) if m else 'any'

                # source_address
                m = re.search(r'-s\s+(\S+)', r)
                source_address = m.group(1) if m else 'any'

                # destination address
                m = re.search(r'-d\s+(\S+)', r)
                destination_address = m.group(1) if m else 'any'

                # in_interface
                m = re.search(r'-i\s+(\S+)', r)
                in_interface = m.group(1) if m else 'any'

                # out_interface
                m = re.search(r'-o\s+(\S+)', r)
                out_interface = m.group(1) if m else 'any'

                # match_module
                m = re.search(r'-m\s+(\S+)', r)
                if m:
                    match_module = m.group(1)
                else:
                    if l4_protocol != 'any':
                        match_module = l4_protocol
                    else:
                        match_module = None

                # FIXME match_parameters
                match_parameters = None

                # action and target_module
                m = re.search(r'(-j|-g)\s+(\S+)', r)
                if not m:
                    print(f'no action specified in {r}. Stop.')
                    sys.exit(1)
                if m.group(1) == '-j':
                    action = 'jump'
                else:
                    action = 'goto'
                target_module = m.group(2)

                # FIXME target_parameters
                target_parameters = None

                rule = Rule(l3_protocol=l3_protocol,
                        l4_protocol=l4_protocol,
                        source_address=source_address,
                        destination_address=destination_address,
                        in_interface=in_interface,
                        out_interface=out_interface,
                        match_module=match_module,
                        match_parameters=match_parameters,
                        action=action,
                        target_module=target_module,
                        target_parameters=target_parameters,
                        raw=r)
                raw_dict[table][chain]['rules'].append(rule)

    return raw_dict


def create_objects(raw_dict):
    tables = []
    for table in raw_dict:
        chains = []
        for chain in raw_dict[table]:
            chains.append(Chain(chain, raw_dict[table][chain]['rules'],
                    is_default=(raw_dict[table][chain]['default_policy']!='-'),
                    default_policy=raw_dict[table][chain]['default_policy']))
        tables.append(Table(table, chains))
    return tables


def parse_iptables_save(path, version):
    contents = ""
    with open(path, 'r') as f:
        contents = f.read()

    raw_dict = parse_tables_and_chains(contents)
    raw_dict = parse_rules(raw_dict, version)
    return create_objects(raw_dict)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'usage: {sys.argv[0]} <path> <4/6>')
        sys.exit(1)

    tables = parse_iptables_save(sys.argv[1], sys.argv[2])

