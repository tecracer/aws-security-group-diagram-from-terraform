import hashlib
import json
from schema_terraform_state_file import check_state_file_against_schema
from schema_diagram_generator_input import check_input_json_against_schema


def process_json(input_json):
    if isinstance(input_json, str):
        data = json.loads(input_json)
    elif isinstance(input_json, dict):
        data = input_json
    else:
        raise TypeError('input_json must be a str or dict')

    check_state_file_against_schema(data)

    resources = data['values']['root_module']['resources']

    output = {
        "prefix_lists": [],
        "cidr_blocks": [],
        "ipv6_cidr_blocks": [],
        "security_groups": [],
    }

    prefix_lists = {}
    security_groups = {}

    # get all prefix lists and security groups
    for resource in resources:
        if resource['type'] == 'aws_ec2_managed_prefix_list':
            prefix_lists[resource['name']] = {
                "id": resource['values']['id'],
                "name": resource['values']['name'],
                "account_id": resource['values']['owner_id'],
                "entries": resource['values']['entry'],
                "not_defined_in_state": False
            }

        elif resource['type'] == 'aws_security_group':
            security_groups[resource['name']] = {
                "id": resource['values']['id'],
                "name": resource['values']['name'],
                "account_id": resource['values']['owner_id'],
                "ingress_rules": [],
                "egress_rules": [],
                "not_defined_in_state": False
            }


    # loop through security groups and add rules
    security_group_rules = {}
    for resource in resources:
        if resource['type'] == 'aws_security_group':

            def process_rules(rule_type, input_rule):

                

                extracted_security_group_ids = []
                for sg_id in input_rule['security_groups']:
                    if '/' in sg_id:
                        sg_id = sg_id.split('/')[-1]
                    extracted_security_group_ids.append(sg_id)

                if input_rule['self'] is True:
                    extracted_security_group_ids.append(resource['values']['id'])

                rule = {
                    "security_group_id": resource['values']['id'],
                    "type": rule_type,
                    "description": input_rule['description'],
                    "from_port": input_rule['from_port'],
                    "to_port": input_rule['to_port'],
                    "protocol": input_rule['protocol'],
                    "source_security_group_ids": extracted_security_group_ids,
                    "source_security_group_ids_raw": input_rule['security_groups'],
                    "cidr_blocks": input_rule['cidr_blocks'],
                    "ipv6_cidr_blocks": input_rule['ipv6_cidr_blocks'],
                    "prefix_list_ids": input_rule['prefix_list_ids']
                }

                

                return rule


            # loop through ingress rule and create rule objects for each
            for ingress_rule in resource['values']['ingress']:

                rule = process_rules("ingress", ingress_rule)
                
                
                sg_rule_id = hashlib.sha256(json.dumps(rule).encode('utf-8')).hexdigest()
                
                if sg_rule_id not in security_group_rules:
                    security_group_rules[sg_rule_id] = rule

            for egress_rule in resource['values']['egress']:

                rule = process_rules("egress", egress_rule)
                
                sg_rule_id = hashlib.sha256(json.dumps(rule).encode('utf-8')).hexdigest()
                
                if sg_rule_id not in security_group_rules:
                    security_group_rules[sg_rule_id] = rule

    output['prefix_lists'] = list(prefix_lists.values())
    output['security_groups'] = list(security_groups.values())

    for rule in security_group_rules.values():
        if rule['type'] == 'ingress':
             for security_group in output['security_groups']:
                if security_group['id'] == rule['security_group_id']:
                    security_group["ingress_rules"].append(rule)
        elif rule['type'] == 'egress':
            for security_group in output['security_groups']:
                if security_group['id'] == rule['security_group_id']:
                    security_group["egress_rules"].append(rule)

        # extract cidr blocks and ipv6 cidr blocks from security group rules      
        output['cidr_blocks'].extend(ingress_rule['cidr_blocks'])
        output['ipv6_cidr_blocks'].extend(ingress_rule['ipv6_cidr_blocks'])

        # add unknown prefix lists to prefix list list
        for prefix_list_id in rule['prefix_list_ids']:
            if not any(prefix_list['id'] == prefix_list_id for prefix_list in output['prefix_lists']):
                output['prefix_lists'].append({
                    "id": prefix_list_id,
                    "name": None,
                    "account_id": None,
                    "entries": None,
                    "not_defined_in_state": True
                })

        # add unknown security groups to security group list
        for security_group_id in rule['source_security_group_ids']:
            #print(rule)
            if not any(security_group['id'] == security_group_id for security_group in output['security_groups']):
              #  print("security group " + security_group_id + " not found")
                parent_sg_id = rule['security_group_id']
                sg_id = security_group_id
                
                # get account id from parent
                for security_group in output['security_groups']:
                    if security_group['id'] == parent_sg_id:
                        account_id = security_group['account_id']
                        break

                # get raw security group id from rule
                for raw_sg_id in rule['source_security_group_ids_raw']:
                    if security_group_id in raw_sg_id:
                        sg_id_raw = raw_sg_id
                        break

                if '/' in sg_id_raw:
                        print("splitting")
                        sg_id = sg_id_raw.split('/')[-1]
                        account_id = sg_id_raw.split('/')[0]
                        print("new sg id: " + sg_id)
                        print("new account id: " + account_id)

             
                
                
                output['security_groups'].append({
                    "id": sg_id,
                    "name": sg_id,
                    "account_id": account_id,
                    "ingress_rules": [],
                    "egress_rules": [],
                    "not_defined_in_state": True
                })

    
     # Remove duplicates from cidr_blocks and ipv6_cidr_blocks lists
    output['cidr_blocks'] = list(set(output['cidr_blocks']))
    output['ipv6_cidr_blocks'] = list(set(output['ipv6_cidr_blocks']))


    # remove all raw security group ids from all rules
    for security_group in output['security_groups']:
        for ingress_rule in security_group['ingress_rules']:
            ingress_rule.pop('source_security_group_ids_raw', None)
        for egress_rule in security_group['egress_rules']:
            egress_rule.pop('source_security_group_ids_raw', None)


    check_input_json_against_schema(output)

    # print(output)
    return output

