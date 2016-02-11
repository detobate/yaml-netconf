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

* Rulesets - A collection of services, description and target hosts.
* Services - YAML mappings containing a list of rules and the owner of the service.
* Rules - YAML mappings containing a rule definition, including source/destination IPs and ports and the action.
* Objects - YAML mappings of common host/network/ip variables.  Can be recursive using Jinja2 variable syntax.
* ACL Template - A compiled access list in YAML format still containing Jinja2 variables referencing objects.
* Compiled ACL - The end result, as either CLI configuration or YANG XML, generated by an Ansible playbook and Jinja2 templates.


Usage:
------

**Step 1:**

Update definition files in:

    ./objects/    - Any object variables
    ./rules/      - ACL rule definitions
    ./services/   - Service definitions containing the above rule definitions
    ./rulesets/   - A ruleset containing multiple services

*Note:* Any new object files added need to be included in the playbook.yml


**Step 2:**

Generate an ACL.yml template file with:

    ./tools/generateRuleset.py <ruleset>


**Step 3:**

Edit `example_playbook.yml` to reference the appropriate objects and ACL file.

Run:

    ansible-playbook -i hosts example_playbook.yaml



Bonus Tools:
------------

- [/tools/SRtoYAML.py](https://github.com/detobate/yaml-netconf/blob/master/tools/SRtoYAML.py) - Feed it an SROS/TiMOS ACL configlet and some YAML object definitions it'll spit out YAML that we can consume

- [/tools/yamilfy.py](https://github.com/detobate/yaml-netconf/blob/master/tools/yamlify.py) - Consumes legacy World of ACL object files and spits out YAML object definitions for use above
