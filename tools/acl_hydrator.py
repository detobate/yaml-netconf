import yaml
import click
import ipaddress


@click.command()
@click.option('--acl', default='../rulesets/example_ACL.yaml', help='The input ACL with relative path.')
@click.option('--object_dir', default='../objects/', help='Relative path to objects')
@click.option('--hydrated_file', default='./hydrated.yaml', help='Output file after hydration')
def main(acl, object_dir, hydrated_file):
    print_title()
    result = load_file(acl)
    process_objects(result, object_dir)


def print_title():
    print('------------------------------')
    print('      ACL HYDRATOR APP')
    print('------------------------------')


def load_file(file):
    with open(file, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.MarkedYAMLError as exc:
            print(exc)


def process_objects(raw_acl, object_dir):
    rules = raw_acl['ACL']
    for rule in rules['rules']:
        try:
            if ipaddress.ip_network(rule['source']):
                print(rule['source'])
        except ValueError as VE:
            acl_object = (rule['source'].strip('{{ ').strip(' }}'))
            print(load_file(object_dir + acl_object + '.yaml'))

    return None


if __name__ == '__main__':
    main()
