#!/usr/bin/env python
import sys
import re

if len(sys.argv) != 2:
    print("Syntax: ./yamilfy.py <infile>")
    raise
else:
    try:
        infile = open(sys.argv[1], 'r')
    except NameError, IOError:
        print("Couldn't find %s" % infile)
        raise
    try:
        outfile = open(sys.argv[2], 'w')
    except:
        print("Couldn't open output file for writing")
        # Not writing to file just yet.  Just printing to stdout
        pass

def strip(x):
    unwanted = {'[', ']', '(', ')', 'qw', 'qw(', '[(', ')]', '),', ',', '\'', ' '}
    if x in unwanted:
        return True
    else:
        return False

def splitPortRange(item):
    # find and replace port ranges using <, > or - notation
    newItem =[]
    if item[:1] == "<":
        item = int(item[1:])
        newItem.insert(0, 1)
        newItem.insert(1, item)
    elif item[:1] == ">":
        item = int(item[1:])
        newItem.insert(0, item)
        newItem.insert(1, 65535)
    elif re.search("-", item):
        try:    # Don't like port zero as a lower port in range
            newItem = [int(n) for n in item.split("-")]
            if newItem[0] == 0:
                newItem[0] = 1
        except:
            return item
    else:
        return item

    return newItem

def output(entry):
    var = entry.pop(0)      # Get the variable name
    del entry[0]            # Get rid of the '=''

    # Check for any empty variables
    if not entry or entry[0] == '':
        print("WARNING: %s is empty" % var)
        return

    print("%s:" % var),      # Print without newlines
    # Catch port ranges
    if isinstance(entry, list) and len(entry) == 2 and all(isinstance(x, int) for x in entry):
        print("\"%s %s\"" % (entry[0], entry[1]))
    elif isinstance(entry, list) and len(entry) > 1:
        print("\n"),
        for value in entry:
            print("\t- \"%s\"" % value)
    elif isinstance(entry, list):
        try:
            print("\"%s\"" % entry[0])
        except:
            print(entry)
            raise
    else:
        print("\"%s\"" % entry)

def main():
    for line in infile:
        # Skip comments and newlines
        if re.match("^#", line) or line == "\n":
            continue

        entry = line.split()

        if entry[1] != "=":
            print("Skipped %s as it didn't follow format: 'variable = value'" % line)
            continue

        # Remove $ prefix from variable names
        if entry[0][:1] == "$":
            entry[0] = entry[0][1:]

        # Iterate through values and s/$/{{}}/
        # Always work on the outer entry
        for item in entry:
            idx = entry.index(item)         # find index before we mangle the value
            if isinstance(item, int):
                continue                    # We don't need to parse integers
            if item.endswith(tuple(["'","\"","}","]",")",","])):
                #print("Removing %s from %s" % (entry[idx][-1],entry[idx]))
                entry[idx] = entry[idx][:-1]
            if item.startswith(tuple(["'","\"","{","[","(",","])):
                #print("Removing %s from %s" % (entry[idx][0],entry[idx]))
                entry[idx] = entry[idx][1:]

            newItem = splitPortRange(entry[idx])
            if isinstance(newItem, str):
                entry[idx] = newItem
            elif isinstance(newItem, list):
                entry[idx] = newItem[0]
                entry.append(newItem[1])

            # Clean up any empty entries after we've stripped unwanted chars
            if entry[idx] is "":
                del entry[idx]

        # Now check for variable after we've stripped quotes
        for item in entry:
            if not isinstance(item, str):
                continue
            else:
                idx = entry.index(item)
                if entry[idx][:1] == "$":
                    entry[idx] = entry[idx][1:] # strip leading $ and add curlies
                    entry[idx] = "{{ %s }}" % entry[idx]

        # If line contains more than just "variable = value", remove unwanted things
        if len(entry) > 3:
            entry[:] = [x for x in entry if not strip(x)]

        output(entry)

if __name__ == "__main__":
    main()
