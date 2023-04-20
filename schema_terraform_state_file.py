from schema import Schema, And, Or, Use, SchemaError, Optional
   
def check_state_file_against_schema(data):

     # Predefined version values
    allowed_format_versions = ["1.0"]
     
    format_version = data.get("format_version")
    terraform_version = data.get("terraform_version")

    if format_version not in allowed_format_versions:
        print(f"Warning: format_version '{format_version}' is not tested. Tested: {allowed_format_versions}")


    try:
        state_file_dict_schema.validate(data)
    except SchemaError as e:
        raise Exception("State File Validation failed!", e)
        


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
    Optional("index"): str,
    "owner_id": str,
    "tags": Or(None, dict),
    "tags_all": Or(None, dict),
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
    Optional("index"): str,
    "name_prefix": str,
    "owner_id": str,
    "revoke_rules_on_delete": bool,
    "tags": Or(None, dict),
    "tags_all": Or(None, dict),
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
    Optional("index"): str,
    "provider_name": str,
    "schema_version": int,
    "values": any,
    Optional("sensitive_values"): dict,
    Optional("depends_on"): list
})

state_file_resource_schema_security_group = Schema({
    "address": str,
    "mode": str,
    "type": str,
    "name": str,
    Optional("index"): str,
    "provider_name": str,
    "schema_version": int,
    "values": state_file_aws_security_group_values_schema,
    Optional("sensitive_values"): dict,
    Optional("depends_on"): list
})

state_file_resource_schema_prefix_list = Schema({
    "address": str,
    "mode": str,
    "type": str,
    "name": str,
    Optional("index"): str,
    "provider_name": str,
    "schema_version": int,
    "values": state_file_aws_ec2_managed_prefix_list_values_schema,
    Optional("sensitive_values"): dict,
    Optional("depends_on"): list
})

state_file_child_modules_schema = Schema({
    "resources": any ,# lambda resource_values: state_file_validate_resource_values(resource_values), #todo: add validation; there is a bug...
    "address": str
})

state_file_root_module_schema = Schema({
    "resources": lambda resource_values: state_file_validate_resource_values(resource_values),
    Optional("child_modules"): [state_file_child_modules_schema]
})



state_file_values_schema = Schema({
    "root_module": state_file_root_module_schema
})

state_file_dict_schema = Schema({
    "format_version": str,
    "terraform_version": str,
    "values": state_file_values_schema
})


