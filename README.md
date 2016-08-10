# yaml-netconf

YAML-NETCONF
======================
A bunch of [Jinja2](http://jinja.pocoo.org/docs/dev/) templates and [YAML](http://docs.ansible.com/ansible/YAMLSyntax.html) object files to output [YANG](https://tools.ietf.org/html/rfc6020) in NETCONF compatible XML ACL rules.

Based on the current [ietf YANG model draft](https://tools.ietf.org/html/draft-ietf-netmod-acl-model-06)

File Structure:
---------------

![File Structure](https://github.com/detobate/yaml-netconf/raw/master/docs/file_structure.png)


Definitions:
-----------------

* ACL Template - A collection of services, description and target hosts.
* SACP - Service Access Control Policy. YAML mappings containing a list of rules and the owner of the service.
* Rules - YAML mappings containing a rule definition, including source/destination IPs and ports and the action.
* Objects - YAML mappings of common host/network/ip variables.  Can be recursive using Jinja2 variable syntax.
* Ruleset - A compiled access list in YAML format.
* Compiled ACL - The end result, as either CLI configuration or YANG XML, generated by the [renderj2.py](https://github.com/detobate/yaml-netconf/blob/master/tools/renderj2.py) tool
* Templates - The Jinja2 template files that convert a compiled ACL in to either CLI compatible config, or NETCONF compatible XML.


Usage:
------


* Git clone this repository
* Create/modify objects/SACPs/rules as required.  Try to use existing objects where possible.
* Create/modify the top-level ACL Template to reference the required SACPs/
* Use the [generateACL.py](https://github.com/detobate/yaml-netconf/blob/master/tools/generateACL.py) tool to compile the ACL template and objects.

    `./tools/generateACL.py ACL_templates/example.yaml > rulesets/example_ruleset.yaml`

* Use [renderj2.py](https://github.com/detobate/yaml-netconf/blob/master/tools/renderj2.py) to generate configuration files by passing it the appropriate Jinja2 template and YAML ruleset:

    `./tools/renderj2.py -j templates/huawei-cli.j2 -y rulesets/example_ruleset.yaml`



Bonus Tools:
------------

- [/tools/SRtoYAML.py](https://github.com/detobate/yaml-netconf/blob/master/tools/SRtoYAML.py) - Feed it an SROS/TiMOS ACL configlet and some YAML object definitions it'll spit out YAML that we can consume

- [/tools/yamilfy.py](https://github.com/detobate/yaml-netconf/blob/master/tools/yamlify.py) - Consumes legacy World of ACL object files and spits out YAML object definitions for use above

- [/tools/netconf-tool.py](https://github.com/detobate/yaml-netconf/blob/master/tools/netconf-tool.py) - A small script to interact with a device via NETCONF
