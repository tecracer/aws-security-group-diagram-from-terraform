from schema import Schema, And, Or, Use, SchemaError, Optional

def check_state_file_against_schema(data):


    try:
        state_file_dict_schema.validate(data)
        print("Validation successful!")
    except SchemaError as e:
        print("Validation failed!", e)



state_file_entry_schema = Schema({
    "cidr": str,
    "description": str
})

state_file_aws_ec2_managed_prefix_list_values_schema = Schema({
    "address_family": str,
    "arn": str,
    "entry": [state_file_entry_schema],
    "id": str,
    "max_entries": int,
    "name": str,
    "owner_id": str,
    "tags": dict,
    "tags_all": dict,
    "version": int
})

state_file_ingress_schema = Schema({
    Optional("cidr_blocks"): Or(None, [str]),
    "description": str,
    "from_port": int,
    Optional("ipv6_cidr_blocks"): Or(None, [str]),
    Optional("prefix_list_ids"): Or(None, [str]),
    "protocol": str,
    Optional("security_groups"): Or(None, [str]),
    "self": bool,
    "to_port": int
})

state_file_aws_security_group_values_schema = Schema({
    "arn": str,
    "description": str,
    "egress": list,
    "id": str,
    "ingress": [state_file_ingress_schema],
    "name": str,
    "name_prefix": str,
    "owner_id": str,
    "revoke_rules_on_delete": bool,
    "tags": dict,
    "tags_all": dict,
    Optional("timeouts"): Or(None, dict),
    "vpc_id": str
})

def state_file_validate_resource_values(resource_values):

    for resource in resource_values:
        resource_type = resource['type']

        if resource_type == 'aws_security_group':
            return state_file_resource_schema_security_group.validate(resource)
        elif resource_type == 'aws_ec2_managed_prefix_list':
            return state_file_resource_schema_prefix_list.validate(resource)
        else:
            return state_file_resource_schema_generic.validate(resource)


    
state_file_resource_schema_generic = Schema({
    "address": str,
    "mode": str,
    "type": str,
    "name": str,
    "provider_name": str,
    "schema_version": int,
    "values": any,
    "sensitive_values": dict,
    Optional("depends_on"): list
})

state_file_resource_schema_security_group = Schema({
    "address": str,
    "mode": str,
    "type": str,
    "name": str,
    "provider_name": str,
    "schema_version": int,
    "values": state_file_aws_security_group_values_schema,
    "sensitive_values": dict,
    Optional("depends_on"): list
})

state_file_resource_schema_prefix_list = Schema({
    "address": str,
    "mode": str,
    "type": str,
    "name": str,
    "provider_name": str,
    "schema_version": int,
    "values": state_file_aws_ec2_managed_prefix_list_values_schema,
    "sensitive_values": dict,
    Optional("depends_on"): list
})

state_file_root_module_schema = Schema({
    "resources": state_file_validate_resource_values
})

state_file_values_schema = Schema({
    "root_module": state_file_root_module_schema
})

state_file_dict_schema = Schema({
    "format_version": And(str, lambda s: s == "1.0"),
    "terraform_version": str,
    "values": state_file_values_schema
})

