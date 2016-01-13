# yaml-netconf

YAML-NETCONF
======================
A bunch of [Jinja2](http://jinja.pocoo.org/docs/dev/) templates and [YAML](http://docs.ansible.com/ansible/YAMLSyntax.html) object files to output [YANG](https://tools.ietf.org/html/rfc6020) in NETCONF compatible XML ACL rules.

Based on the current [ietf YANG model draft](https://tools.ietf.org/html/draft-ietf-netmod-acl-model-06)

Usage:
------
    ansible-playbook -i hosts example_playbook.yml
