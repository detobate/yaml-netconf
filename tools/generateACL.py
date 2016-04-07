#!/usr/bin/env python3
import sys
import os
import yaml
import argparse
import ipaddress

parser = argparse.ArgumentParser(description='Take a YAML ACL template and generate a YAML ACL ruleset')
parser.add_argument('-s', dest='service', metavar='<SACP Path>', default="./SACPs/", help='Path to YAML SACP definition files. Defaults to ./SACPs/')
parser.add_argument('-r', dest='rules', metavar='<Rules Path>', default="./rules/", help='Path to YAML rule definition files. Defaults to ./rules/')
parser.add_argument('-o', dest='objects', metavar='<Objects Path>', default="./objects/", help='YAML Object files')
parser.add_argument('aclTemplate', metavar='<ACL_template>', help='ACL Template')
args = parser.parse_args()

defaultWeight = 50

def addLengths(yamlRuleset, objects):
    ''' A horrible function to temporarily resolve variables
        in order to determine how specific the source/destinations are '''

    for rule in yamlRuleset['ACL']['rules']:
        if rule['source'][0] == "{" and rule['source'][-1] == "}":
            svalue = lookupVar(objects, rule['source'])
            # Do we need to iterate over this variable?
            if isinstance(svalue, list):
                slen = 0
                for source in svalue:
                    if source[0] == "{" and source[-1] == "}":
                        try:
                            svalue = ipaddress.ip_network(lookupVar(objects, source[0]), strict=False)
                        except:
                            # not found, break out of loop
                            continue
                    else:
                        svalue = ipaddress.ip_network(source)
                if svalue.prefixlen > slen:
                    slen = svalue.prefixlen
                rule['_slen'] = slen
            else:
                try:
                    svalue = ipaddress.ip_network(svalue, strict=False)
                    rule['_slen'] = svalue.prefixlen
                except:
                    print("%s isn't an IP or prefix" % svalue)
        # Treat "any" as zero length
        elif rule['source'] == "any":
            rule['_slen'] = 0

        # If not a variable or "any", assume it's an IP/prefix
        else:
            try:
                svalue = ipaddress.ip_network(rule['source'], strict=False)
                rule['_slen'] = svalue.prefixlen
            except:
                print("%s isn't an IP or prefix" % svalue)

        if rule['dest'][0] == "{" and rule['dest'][-1] == "}":
            dvalue = lookupVar(objects, rule['dest'])
            try:
                dvalue = ipaddress.ip_network(dvalue, strict=False)
                rule['_dlen'] = dvalue.prefixlen
            except:
                print("%s isn't an IP or prefix" % dvalue)
        elif rule['dest'] == "any":
            rule['_dlen'] = 0
        else:
            try:
                dvalue = ipaddress.ip_network(rule['dest'], strict=False)
                rule['_dlen'] = svalue.prefixlen
            except:
                print("%s isn't an IP or prefix" % dvalue)

    return yamlRuleset

def lookupVar(objects, var):

    var = var.strip("{} ")
    # First try to match variable exactly
    try:
        value = objects[var]
    except:
        # Failing that, try to match one layer deeper
        try:
            var1, var2 = var.split(".")
            value = objects[var1][var2]
        except:
            pass

    return value

def parseService(service, services, rules, yamlRuleset):
    ''' This function parses a SACP definition
        expands individual rules but leaves variables unresolved'''
    tests = []
    for rule in services[service]['rules']:
        tempRule = {}
        newRule = True
        # Check if a rule is weighted, else set weight to 50
        try:
            tempRule['_weight'] = rule['weight']
        except:
            tempRule['_weight'] = defaultWeight
        rulename = rule['rule'].strip("{} ")    # We expect J2 style variables so strip off curly braces
        for key, value in sorted(rules[rulename].items()):
            tempRule[key] = value
        tempRule['_belongs_to'] = services[service]['name']     # Keep track of which service definition created this rule
        yamlRuleset['ACL']['rules'].append(tempRule)
        # Did this rule have any test cases that haven't already been included?
        if 'testcase' in rule and rule['testcase'] not in tests:
            tests.append(rule['testcase'])

    # If this SACP included testcases, add them to the ruleset
    if 'testcases' in yamlRuleset['ACL'] and tests:
        yamlRuleset['ACL']['testcases'].extend(tests)
    elif tests:
        yamlRuleset['ACL']['testcases'] = tests
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
    yamlRuleset['ACL']['acl_id'] = ruleset['acl_id']
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

    # Build a dict of all the objects we know about
    objects = {}
    for filename in os.listdir(args.objects):
        with open(args.objects + filename) as infile:
            for entry in yaml.safe_load_all(infile):
                objects.update(entry)


    for service in ruleset['SACP']:
        service = service.strip("{} ")
        if services[service]['acl_type'] != aclType:
            print("Error: SACP definition %s is not of type %s" % (services[service]['name'], aclType))
            exit(1)
        yamlRuleset = parseService(service, services, rules, yamlRuleset)

    # Sort ruleset by IP/prefix size
    yamlRuleset = addLengths(yamlRuleset, objects)

    # Sort the compiled rules list first by dest prefix, then source, finally weight.
    yamlRuleset['ACL']['rules'].sort(key=lambda x: (x['_dlen'], x['_slen'], x['_weight']), reverse=True)

    print(yaml.dump(yamlRuleset, explicit_start=True, default_flow_style=False))
    print('...')

if __name__ == "__main__":
    main()
