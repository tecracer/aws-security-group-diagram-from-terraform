from schema import Schema, And, Or, Optional, Use, SchemaError

cidr_block_entry_schema = {
    'cidr': str,
    'description': str
}

prefix_list_schema = {
    'id': str,
    'name': str,
    'account_id': str,
    'entries': [cidr_block_entry_schema],
    'not_defined_in_state': bool
}

rule_schema = {
    'security_group_id': str,
    'type': str,
    'description': str,
    'from_port': int,
    'to_port': int,
    'protocol': str,
    'source_security_group_ids': Or(None, [str]),
    'cidr_blocks': Or(None, [str]),
    'ipv6_cidr_blocks': Or(None, [str]),
    'prefix_list_ids': Or(None, [str])
}

security_group_schema = {
    'id': str,
    'name': str,
    'account_id': str,
    'ingress_rules': [rule_schema],
    'egress_rules': [rule_schema],
    'not_defined_in_state': bool
}

json_schema = Schema({
    'prefix_lists': [prefix_list_schema],
    'cidr_blocks': [str],
    'ipv6_cidr_blocks': [str],
    'security_groups': [security_group_schema]
})

def check_input_json_against_schema(data):

    try:
        json_schema.validate(data)

    except SchemaError as e:
        raise Exception("JSON Validation failed!", e)
