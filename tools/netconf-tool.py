#!/usr/bin/env python2.7

import sys
import getpass
import argparse
from ncclient import manager

parser = argparse.ArgumentParser(description='A simple script to talk to a router via NETCONF')
parser.add_argument('-u', dest='user', help='CAUTH Username')
parser.add_argument('-t', dest='type', default='alu', help='Device Type. [Default:"alu"]')
parser.add_argument('-T', dest='timeout', default=30, help='Timeout value. [Default:"30sec"]')
parser.add_argument('-H', dest='host', default='localhost', help='Target Host [Default:"localhost"]')
parser.add_argument('-p', dest='port', default=830, help='NETCONF Port [Default:"830"]')
parser.add_argument('-c', dest='target', default='running', help='Target Configuration [default:"running"]')
parser.add_argument('-P', dest='push', metavar='PUSH <XML_File>', help='Push <XML_File> Config')
parser.add_argument('-G', dest='get', default=False, nargs='?', metavar='XML_Filter', help='Get config, optionally filter by XML query')
parser.add_argument('-l', action='store_true', help='Enable logging to ncclient.log')
args = parser.parse_args()


# Make sure user hasn't specified both or neither PUSH/GET
if (args.push and args.get) or (not args.push and args.get is False):
    print("Please provide either Push or Get options")
    exit(1)
try:
    user = args.user
except:
    user = getpass.getuser()

password = getpass.getpass("Enter CAUTH Password: ")
devtype = args.type
port = args.port
host = args.host
target = args.target
timeout = args.timeout

try:
    if args.push:
        xmlfile = args.push
        command = 'push'
    elif args.get is None:
        xmlfile = None
        command = 'get'
        timeout = 60 # Increase the timeout value as fetching the whole config can take awhile.
    elif args.get:
        xmlfile = args.get
        command = 'get'
except:
    print("Please provide the path to an XML file")
    exit(1)

def main():

    if xmlfile is not None:
        try:
            with open(xmlfile, 'r') as input:
                xml = input.read().replace('\n', '')
        except:
            print("Couldn't read XML file %s" % xmlfile)
            exit(1)
    if args.l:
        manager.logging.basicConfig(filename='ncclient.log', level=manager.logging.DEBUG)
    with manager.connect_ssh(host=host, port=port, username=user, password=password, hostkey_verify=False, device_params={'name':devtype}, timeout=timeout) as m:
        if command == 'push':
            m.edit_config(target=target, config=xml, default_operation='merge')
        elif command == 'get':
            if xmlfile is not None:
                output = m.get_config(source=target, filter=xml)
            else:
                output = m.get_config(source=target)
            print(output)


if __name__ == "__main__":
    main()
