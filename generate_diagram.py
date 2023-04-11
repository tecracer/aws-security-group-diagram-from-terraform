from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import VPC, VPCPeering, RouteTable
from schema_diagram_generator_input import check_input_json_against_schema


GRAPH_ATTR = {
    "splines": "polyline",
    "overlap": "false",
    "nodesep": "4",
    "ranksep": "2",
    "rankdir": "LR",
    "compound": "true"
}
NODE_ATTR = {
    "fontsize": "12",
}
EDGE_ATTR = {
    "fontsize": "11",
}

def generate_security_groups_diagram(json_data: dict, output_filename: str = "security_groups_diagram", outformat: str = "png", show: bool = False):
    if not isinstance(json_data, dict):
        raise ValueError("Input should be a dictionary")



    check_input_json_against_schema(json_data)

    sg_nodes = {}
    pl_nodes = {}
    ipv4_cidr_nodes = {}
    ipv6_cidr_nodes = {}

    with Diagram("Security Groups Diagram", show=show, filename=output_filename, graph_attr=GRAPH_ATTR, node_attr=NODE_ATTR, edge_attr=EDGE_ATTR, outformat=outformat) as diagram:

        accounts = extract_unique_account_ids(json_data)
        for account_id in accounts:
            with Cluster(f"Account {account_id}"):
                sgs = extract_security_groups_for_account(json_data, account_id)
                pls = extract_prefix_lists_for_account(json_data, account_id)

                with Cluster(f"Security Groups"):
                    for sg in sgs:
                        sg_key = sg["id"]
                        sg_nodes[sg_key] = VPC(f'{sg["name"]} ({sg["id"]})')


                with Cluster(f"Prefix Lists"):
                    for pl in pls:
                        pl_key = pl["id"]
                        pl_nodes[pl_key] = VPCPeering(f'{pl["name"]} ({pl["id"]})')

        ipv4_cidrs = extract_all_ipv4_cidrs(json_data)
        ipv6_cidrs = extract_all_ipv6_cidrs(json_data)

        with Cluster(f"IPv4 CIDR Ranges"):

            for ipv4_cidr in ipv4_cidrs:
                ipv4_cidr_key = ipv4_cidr
                ipv4_cidr_nodes[ipv4_cidr_key] = RouteTable(ipv4_cidr)

        with Cluster(f"IPv6 CIDR Ranges"):
            for ipv6_cidr in ipv6_cidrs:
                ipv6_cidr_key = ipv6_cidr
                ipv6_cidr_nodes[ipv6_cidr_key] = RouteTable(ipv6_cidr)

            
        #print(json_data.get("security_groups"))

        for sg in json_data.get("security_groups", []):
            #print(sg)
            sg_key = sg["id"]
            for rule in sg.get("ingress_rules", []):

                #print(rule)
                

              

                for src_sg in (rule.get("source_security_group_ids") if rule.get("source_security_group_ids") is not None else []):
                    if src_sg in sg_nodes:
                        sg_nodes[src_sg] >> Edge(label=f"{rule['from_port']}-{rule['to_port']} ({rule['protocol']})") >> sg_nodes[sg_key]   
                        
                for cidr in (rule.get("cidr_blocks") if rule.get("cidr_blocks") is not None else []):
                    if cidr in ipv4_cidr_nodes:
                        ipv4_cidr_nodes[cidr] >> Edge(label=f"{rule['from_port']}-{rule['to_port']} ({rule['protocol']})") >> sg_nodes[sg_key]

                for ipv6_cidr in (rule.get("ipv6_cidr_blocks") if rule.get("ipv6_cidr_blocks") is not None else []):
                    if ipv6_cidr in ipv6_cidr_nodes:
                        ipv6_cidr_nodes[ipv6_cidr] >> Edge(label=f"{rule['from_port']}-{rule['to_port']} ({rule['protocol']})") >> sg_nodes[sg_key]
                        
                for pl_id in (rule.get("prefix_list_ids") if rule.get("prefix_list_ids") is not None else []):
                    if pl_id in pl_nodes:
                        pl_nodes[pl_id] >> Edge(label=f"{rule['from_port']}-{rule['to_port']} ({rule['protocol']})") >> sg_nodes[sg_key]

     


def extract_unique_account_ids(data: dict) -> list:
    account_ids = set()

    for prefix_list in data.get('prefix_lists', []):
        account_ids.add(prefix_list.get('account_id'))

    for security_group in data.get('security_groups', []):
        account_ids.add(security_group.get('account_id'))

    return list(account_ids)

def extract_security_groups_for_account(data: dict, account_id: str) -> list:
    return [sg for sg in data.get('security_groups', []) if sg.get('account_id') == account_id]

def extract_prefix_lists_for_account(data: dict, account_id: str) -> list:
    return [pl for pl in data.get('prefix_lists', []) if pl.get('account_id') == account_id]

def extract_all_ipv4_cidrs(data: dict) -> list:
    ipv4_cidrs = set()
    for sg in data.get('security_groups', []):
        for rule in sg.get('ingress_rules', []):
            cidr_blocks = rule.get('cidr_blocks')
            if cidr_blocks is not None:
                for cidr_block in cidr_blocks:
                    ipv4_cidrs.add(cidr_block)
    return list(ipv4_cidrs)



def extract_all_ipv6_cidrs(data: dict) -> list:
    ipv6_cidrs = set()
    for sg in data.get('security_groups', []):
        for rule in sg.get('ingress_rules', []):
            ipv6_cidr_blocks = rule.get('ipv6_cidr_blocks')
            if ipv6_cidr_blocks is not None:
                for ipv6_cidr_block in ipv6_cidr_blocks:
                    ipv6_cidrs.add(ipv6_cidr_block)
    return list(ipv6_cidrs)

