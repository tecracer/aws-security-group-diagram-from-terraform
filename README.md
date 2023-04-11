# README
## Introduction

The code provided is a Python script that takes Terraform state file information, processes it, and generates a visual diagram of AWS Security Groups and their associated ingress and egress rules. The generated diagrams are in PNG format and can be used to visualize AWS infrastructure security rules and their relationships.

The program is by no means complete and can surely be improved. Feel free to contribute. I do not actively maintain the project.

Dependencies
    - Python 3.11 (only version it was tested with)
    - diagrams library (for generating diagrams)
    - schema library (for JSON schema validation)

To install the required dependencies, run the following command:

```bash
pip3 install diagrams schema
```

## How to use

The Python script accepts input data in two ways:
-  A Terraform state file (use the -f flag) or a text file created from `terraform show -json` via the `-f` flag

```bash
    python3 main.py -f terraform.tfstate
```

 - The output of the `terraform show -json` command directly piped into the script (use the `-i` flag)

```bash
    terraform show -json | python3 main.py -i
```

I recommend running `terraform refresh` before accessing the state file if you use the `aws_security_group_rule`resource (reason: the script doesn't read the rules from that resource but instead directly from `aws_security_group`. With the refresh, they are automatically copied from `aws_security_group_rule` to `aws_security_group`. Before that, the diagram might be incomplete)




The script will then process the input data, extract security groups and their rules, and generate a visual diagram in PNG format. The default file name for the output diagram is `diagram.png`. It can be changed with the `-o`flag accompanied by a file name. Use `-of` flag to change output format. Use the `--show`flag to directly open the result.