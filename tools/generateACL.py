#!/usr/bin/env python3
import sys
import os
import yaml
import argparse

parser = argparse.ArgumentParser(description='Take a YAML ACL template and generate a YAML ACL ruleset')
parser.add_argument('-s', dest='service', metavar='<SACP Path>', default="./SACPs/", help='Path to YAML SACP definition files. Defaults to ./SACPs/')
parser.add_argument('-r', dest='rules', metavar='<Rules Path>', default="./rules/", help='Path to YAML rule definition files. Defaults to ./rules/')
#parser.add_argument('-o', metavar='./outpath/', help='YAML Object files')
parser.add_argument('aclTemplate', metavar='<ACL_template>', help='ACL Template')
args = parser.parse_args()

def parseService(service, services, rules, yamlRuleset):
    for rule in services[service]['rules']:
        tempRule = {}
        newRule = True
        rule = rule.strip("{} ")    # We expect J2 style variables so strip off curly braces
        for key, value in sorted(rules[rule].items()):
            tempRule[key] = value
        tempRule['_belongs_to'] = services[service]['name']     # Keep track of which service definition created this rule
        yamlRuleset['ACL']['rules'].append(tempRule)
    return yamlRuleset

def main():
    # First, build a dict of the ruleset definition
    ruleset = {}
    with open(args.aclTemplate, 'r') as infile:
        for entry in yaml.safe_load_all(infile):
            ruleset.update(entry)

    aclType = ruleset['acl_type']

    # Build a crazy dict of dicts of lists to create the appropriate YAML heirachy
    yamlRuleset = {}
    yamlRuleset['ACL'] = {}
    yamlRuleset['ACL']['acl_type'] = aclType
    yamlRuleset['ACL']['description'] = ruleset['description']
    yamlRuleset['ACL']['name'] = ruleset['name']
    yamlRuleset['ACL']['rules'] = []


    # Build a dict of all the rules we know about
    rules = {}
    for filename in os.listdir(args.rules):
        with open(args.rules + filename) as infile:
            for entry in yaml.safe_load_all(infile):
                rules.update(entry)

    # Build a dict of all service definitions
    services = {}
    for filename in os.listdir(args.service):
        with open(args.service + filename, 'r') as infile:
            allServices = list(yaml.safe_load_all(infile))  # Convert generator to list
            for entry in allServices:
                #print("Adding: %s" % entry)
                services[entry['name']] = entry

    for service in ruleset['services']:
        service = service.strip("{} ")
        if services[service]['acl_type'] != aclType:
            print("Error: SACP definition %s is not of type %s" % (services[service]['name'], aclType))
            exit(1)
        yamlRuleset = parseService(service, services, rules, yamlRuleset)

    print(yaml.dump(yamlRuleset, explicit_start=True, default_flow_style=False))
    print('...')


if __name__ == "__main__":
    main()
