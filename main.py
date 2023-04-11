import sys
import subprocess
import json
from convert_state_file_to_diagram_generator_input import process_json
from generate_diagram import generate_security_groups_diagram
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import VPC




if __name__ == "__main__":
    input_json = None

    if "-f" in sys.argv:
        index = sys.argv.index("-f")
        file_name = sys.argv[index + 1]
        with open(file_name, "r") as f:
            input_json = json.load(f)
    elif "-i" in sys.argv:
        terraform_show_output = sys.stdin.read()
        input_json = json.loads(terraform_show_output)
    else:
        print("No input flag specified. Use -f or -i flags.")
       
    security_groups = process_json(input_json)
    # print(security_groups)

    generate_security_groups_diagram_diagrams(security_groups)
    