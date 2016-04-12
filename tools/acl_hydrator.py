import yaml
import click


@click.command()
@click.option('--acl', default='../rulesets/example_ACL.yaml', help='The input ACL with relative path.')
@click.option('--object_dir', default='../objects/', help='Relative path to objects')
@click.option('--hydrated_file', default='./hydrated.yaml', help='Output file after hydration')
def main(acl, object_dir, hydrated_file):
    print_title()
    new_rule_set = load_rulesets(acl, object_dir)
    print(new_rule_set)
    # write_rule_set(rule_set, hydrated_file)


def print_title():
    print('------------------------------')
    print('      ACL HYDRATOR APP')
    print('------------------------------')


def load_rulesets(file, object_dir):
    with open(file, 'r') as stream:
        master_dict = yaml.load(stream)
        counter = 0

        '''create copy of original and later only replace the bits that get hydrated. All the descriptions etc remain
        untouched'''

        new_master_dict = master_dict

        for rule in master_dict['ACL']['rules']:

            '''check whether there is a further reference via curly brackets to another object, if so invoke
            the recursive load_object function which returns with the full list'''

            if rule['source'][0:2] == '{{':
                object_file_name = rule['source'].strip('{{').strip('}}').strip() + '.yaml'
                list_of_objects = load_object(object_dir + object_file_name, object_dir)
                new_master_dict['ACL']['rules'][counter]['source'] = list_of_objects

            ''' do the above for the other four tuples i.e. ports, dest etc'''

            if rule['dest'][0:2] == '{{':
                object_file_name = rule['dest'].strip('{{').strip('}}').strip() + '.yaml'
                list_of_objects = load_object(object_dir + object_file_name, object_dir)
                new_master_dict['ACL']['rules'][counter]['dest'] = list_of_objects

            if rule['sport'][0:2] == '{{':
                object_file_name = rule['sport'].strip('{{').strip('}}').strip() + '.yaml'
                list_of_objects = load_object(object_dir + object_file_name, object_dir)
                new_master_dict['ACL']['rules'][counter]['sport'] = list_of_objects

            if rule['dport'][0:2] == '{{':
                object_file_name = rule['dport'].strip('{{').strip('}}').strip() + '.yaml'
                list_of_objects = load_object(object_dir + object_file_name, object_dir)
                new_master_dict['ACL']['rules'][counter]['dport'] = list_of_objects

            if rule['proto'][0:2] == '{{':
                object_file_name = rule['proto'].strip('{{').strip('}}').strip() + '.yaml'
                list_of_objects = load_object(object_dir + object_file_name, object_dir)
                new_master_dict['ACL']['rules'][counter]['proto'] = list_of_objects

            counter += 1
        return new_master_dict


def load_object(file, object_dir):
    with open(file, 'r') as stream:
        list_of_objects = yaml.load(stream)
        ''' list_of_objects can either be another reference, then this function will cal itself again, if not
         then we return the actual list'''

        network_objects = []

        for network_object in list_of_objects['object']:
            if network_object[0:2] == '{{':
                object_file_name = network_object.strip('{{').strip('}}') + '.yaml'
                temp_objects = load_object(object_file_name, object_dir)
                network_objects.append(temp_objects)
            else:
                network_objects.append(network_object)

        return network_objects


if __name__ == '__main__':
    main()
