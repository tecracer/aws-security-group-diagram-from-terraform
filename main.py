import sys
import subprocess
import json
from convert_state_file_to_diagram_generator_input import process_json
from generate_diagram import generate_security_groups_diagram
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import VPC




if __name__ == "__main__":
    input_json = None

    # check for flag -f and input file name
    if "-f" in sys.argv:
        index = sys.argv.index("-f")
        file_name = sys.argv[index + 1]
        with open(file_name, "r") as f:
            input_json = json.load(f)
            
    # check for flag -i and input from stdin
    elif "-i" in sys.argv:
        terraform_show_output = sys.stdin.read()
        input_json = json.loads(terraform_show_output)
    else:
        print("No input flag specified. Use -f or -i flags.")

    # check for flag -o and output file name
    if "-o" in sys.argv:
        index = sys.argv.index("-o")
        output_filename = sys.argv[index + 1]
    else:
        output_filename = "diagram"

    # check for flag -of and output format
    if "-of" in sys.argv:
        index = sys.argv.index("-of")
        output_format = sys.argv[index + 1]
    else:
        output_format = "png"

    # check for flag --show and show diagram
    if "--show" in sys.argv:
        show_after_generation = True
    else:
        show_after_generation = False

    
       
    preprocessed_json = process_json(input_json)
    # print(security_groups)

    generate_security_groups_diagram(preprocessed_json, output_filename=output_filename, outformat=output_format, show=show_after_generation)
    