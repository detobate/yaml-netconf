#!/usr/bin/env python2.7

import sys
import getpass
import argparse
from ncclient import manager

parser = argparse.ArgumentParser(description='A simple script to push XML to a router via NETCONF')
parser.add_argument('-u', dest='user', help='CAUTH Username')
parser.add_argument('-t', dest='type', default='alu', help='Device Type. [Default:"alu"]')
parser.add_argument('-H', dest='host', default='localhost', help='Target Host [Default:"localhost"]')
parser.add_argument('-p', dest='port', default=830, help='NETCONF Port [Default:"830"]')
parser.add_argument('-c', dest='target', default='running', help='Target Configuration [default:"running"]')
parser.add_argument('xmlfile', metavar='<YANG-XML>', help='YANG XML Config File')
args = parser.parse_args()

try:
    user = args.user
except:
    user = getpass.getuser()

password = getpass.getpass("Enter CAUTH Password: ")
devtype = args.type
port = args.port
xmlfile = args.xmlfile
host = args.host
target = args.target

def main():

    try:
        with open(xmlfile, 'r') as input:
            xml = input.read().replace('\n', '')
    except:
        print("Couldn't find XML file %s" % xmlfile)
        exit(1)

    manager.logging.basicConfig(filename='ncclient.log', level=manager.logging.DEBUG)
    with manager.connect_ssh(host=host, port=port, username=user, password=password, hostkey_verify=False, device_params={'name':devtype}) as m:
        m.edit_config(target=target, config=xml, default_operation='merge')


if __name__ == "__main__":
    main()
