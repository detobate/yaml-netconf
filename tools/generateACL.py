#!/usr/bin/env python3
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

def resolve_ruleset(yamlRuleset, objects):
    ''' Iterate over the ruleset and resolve Jinja2 style variables
    Replace the list of rules with the expanded ones '''

    resolved_rules = []

    # Resolve vars and turn the things we want to iterate over into lists
    for rule in yamlRuleset['ACL']['rules']:
        for item in ('source', 'dest', 'sport', 'dport', 'proto'):
            if str(rule[item])[0:2] == "{{" and str(rule[item])[-2:] == "}}":
                rule[item] = load_object(objects, rule[item])
            else:
                rule[item] = [rule[item]]

        # LOLOLOLOLOOLOLOL
        for src in rule['source']:
            for dst in rule['dest']:
                for sp in rule['sport']:
                    for dp in rule['dport']:
                        for p in rule['proto']:
                            new_rule = { 'source': src, 'dest': dst, 'sport': sp, 'dport': dp, 'proto': p, 'description': rule['description'],\
                                         '_belongs_to': rule['_belongs_to'], 'actions': rule['actions'], '_weight': rule['_weight'] }

                            # Catch special items
                            if "icmp-type" in rule:
                                new_rule['icmp-type'] = rule['icmp-type']
                            resolved_rules.append(new_rule)

    yamlRuleset['ACL']['rules'] = resolved_rules
    return yamlRuleset



def load_object(objects, object_name):
    ''' list_of_objects can either be another reference, then this function will call itself again, if not
         then we return the actual list'''

    key = object_name.strip('{} ')
    resolved_objects = []

    # Make sure results are always lists, so we can iterate over them
    if type(objects[key]) == str:
        new_objects = [objects[key]]       # Direct single match
    elif type(objects[key]) == list:
        new_objects = objects[key]         # Match contains multiple values

    # Recursively lookup objects until they're no longer {{ variables }}
    for obj in new_objects:
        if obj[0:2] == '{{':
            temp_object = load_object(objects, obj)
            if type(temp_object) == str:
                resolved_objects.append(temp_object)
            elif type(temp_object) == list:
                resolved_objects = resolved_objects + temp_object
        else:
            # No more variables, add the match to the list we'll return
            resolved_objects.append(obj)

    return resolved_objects

def find_length(obj):
    ''' Simple function to return length of prefix or 0 if "any" '''
    if obj.lower() == "any":
        length = 0
    else:
        try:
            length = ipaddress.ip_network(obj).prefixlen
        except:
            length = 0

    return(length)

def sort_ruleset(yamlRuleset):
    ''' Sort the compiled ruleset.
    Weight should override prefix lengths.
    Then sort by source length followed by dest length'''
    yamlRuleset['ACL']['rules'].sort(key=lambda rule: (rule['_weight'], find_length(rule['source']), find_length(rule['dest'])), reverse=True)

    return(yamlRuleset)

def parse_service(service, services, rules, yamlRuleset):
    ''' This function parses a SACP definition
        expands individual rules but leaves variables unresolved'''

    tests = []
    for rule in services[service]['rules']:
        tempRule = {}

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
    yamlRuleset['ACL']['default'] = ruleset['default']
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
        yamlRuleset = parse_service(service, services, rules, yamlRuleset)

    # Resolve ruleset
    yamlRuleset = resolve_ruleset(yamlRuleset, objects)
    # Sort ruleset
    yamlRuleset = sort_ruleset(yamlRuleset)

    print(yaml.dump(yamlRuleset, explicit_start=True, default_flow_style=False))
    print('...')

if __name__ == "__main__":
    main()
