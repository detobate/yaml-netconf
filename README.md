# yaml-netconf

YAML-NETCONF
======================
A bunch of [Jinja2](http://jinja.pocoo.org/docs/dev/) templates and [YAML](http://docs.ansible.com/ansible/YAMLSyntax.html) object files to output [YANG](https://tools.ietf.org/html/rfc6020) in NETCONF compatible XML ACL rules.

Based on the current [ietf YANG model draft](https://tools.ietf.org/html/draft-ietf-netmod-acl-model-06)

Usage:
------

**Step 1:**

Update definitions in:

    ./objects/    - Any object*variables
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

    ansible-playbook -i hosts example_playbook.yml
