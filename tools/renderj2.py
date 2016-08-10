#!/usr/bin/env python3

import jinja2
import os
import yaml
import argparse

parser = argparse.ArgumentParser(description='A small tool to render Jinja2 templates with YAML objects')
parser.add_argument('-j', dest='j2', metavar='<j2_file>', required=True, help='Jinja2 template')
parser.add_argument('-y', dest='yaml', metavar='<yaml_file>', required=True, help='YAML variable file')
args = parser.parse_args()

def main():
    loader = jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(args.j2)), followlinks=True)
    env = jinja2.Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(os.path.basename(args.j2))

    with open(args.yaml, 'r') as f:
        print(template.render(yaml.load(f)))

if __name__ == '__main__':
    main()
