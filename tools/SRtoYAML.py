#!/usr/bin/env python3
import sys
import yaml


if len(sys.argv) < 2:
    print("Syntax: %s <infile> [objectfiles]" % sys.argv[0])
    exit(1)
else:
    try:
        infile = open(sys.argv[1], 'r')
    except (NameError, IOError):
        print("Couldn't find %s" % infile)
        exit(1)

objectFiles = (sys.argv[2:])

def fetchObjects(objectFiles):
    for file in objectFiles:
        with open(file, 'r') as f:
            objects = f.read()
    objects = yaml.safe_load_all(objects)

    return list(objects)


def parseRule(rule):
    newRule = {}
    try:
        newRule['description'] = rule['description']
    except:
        newRule['description'] = "NO DESCRIPTION PROVIDED"
    try:
        newRule['source'] = rule['source']
    except:
        newRule['source'] = "any"
    try:
        newRule['dest'] = rule['dest']
    except:
        newRule['dest'] = "any"
    try:
        if isinstance(rule['sport'], str):
            newRule['sport'] = rule['sport']
        elif isinstance(rule['sport'], list):
            newRule['sport'] = {}
            newRule['sport']['startrange'] = rule['sport'][0]
            newRule['sport']['endrange'] = rule['sport'][1]
    except:
        newRule['sport'] = "any"
    try:
        if isinstance(rule['dport'], str):
            newRule['dport'] = rule['dport']
        elif isinstance(rule['dport'], list):
            newRule['dport'] = {}
            newRule['dport']['startrange'] = rule['dport'][0]
            newRule['dport']['endrange'] =rule['dport'][1]
    except:
        newRule['dport'] = "any"

    try:
        newRule['actions'] = rule['actions']
    except:
        print("ERROR: Rule missing action")
        exit(1)

    return newRule

def fetchRules(infile):
    ruleset = []    # Use an ordered list for rules
    rule = {}
    newEntry = False
    for line in infile:
        line = line.strip()

        entry = line.split()
        if entry[0] == "entry":
            newEntry = True
            rule.clear()
            continue
        elif newEntry == True:
            if entry[0] == "description":
                entry.pop(0)
                rule['description'] = ' '.join(map(str, entry))
            elif entry[0] == "src-ip":
                rule['source'] = entry[1]
            elif entry[0] == "dst-ip":
                rule['dest'] = entry[1]
            elif entry[0] == "src-port":
                if entry[1] == "eq":
                    rule['sport'] = entry[2]
                elif entry[1] == "range":
                    rule['sport'] = [entry[2], entry[3]]
            elif entry[0] == "dst-port":
                if entry[1] == "eq":
                    rule['dport'] = entry[2]
                elif entry[1] == "range":
                    rule['dport'] = [entry[2], entry[3]]
            elif entry[0] == "action" and entry[1] == "drop":
                rule['actions'] = "deny"
                newEntry = False        # a rule should always end after the action
            elif entry[0] == "action" and entry[1] == "forward":
                rule['actions'] = "permit"
                newEntry = False
        if bool(rule) == True and newEntry == False:
            ruleset.append(rule.copy())     # Add a copy of this dict to the ruleset list
            rule.clear()                    # Then clear the dict so we can re-use it for the next rule

    return ruleset


def findVar(search, objects):

    for doc in objects:
        for entry in doc:
            if isinstance(doc[entry], str):
                if search.strip('\"') == doc[entry].strip('\"'):
                    varname = entry
                    #print("%s matched %s" % (search, doc[entry]))

            ##########################################
            ### Can't reverse lookup an element with multiple entries as it will introduce unknowns
            ##########################################
            #elif isinstance(doc[entry], list):
            #    if search.strip('"') in str(iter(doc[entry])).strip('"'):
            #        varname = entry
            #        print("%s matched %s" % (search, doc[entry]))

    if 'varname' in locals():
        return varname
    else:
        return False

def main():

    yamlFile = {}
    yamlFile['acl_type'] = '"ipv4-acl" OR "ipv6-acl"'
    yamlFile['description'] = '<FILL_ME>'
    yamlFile['owner'] = '<FILL_ME>'
    yamlFile['rules'] = []

    ruleset = fetchRules(infile)
    objects = fetchObjects(objectFiles)

    for rule in ruleset:
        for key, value in rule.items():
            #print("Checking: %s" % value)
            varname = findVar(value, objects)
            if varname is not False:
                #print("Replacing %s with {{ %s }}" % (value, varname))
                rule[key] = "{{ %s }}" % varname

        yamlFile['rules'].append(parseRule(rule))   # Add the parsed rule dict to the YAML file as a new list item

    print(yaml.dump(yamlFile, explicit_start=True, default_flow_style=False))
    #print(yamlFile)
    print('...')

    infile.close()

if __name__ == "__main__":
    main()
