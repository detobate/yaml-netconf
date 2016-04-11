import yaml
import click


@click.command()
@click.option('--file_arg', default='example', help='ACL to process in YAML format with path, default is example.yaml in ./ ')
def get_file(file_arg):
    with open("{}".format(file_arg), 'r') as stream:
        try:
            print(yaml.load(stream))
        except yaml.Event as exc:
            print(exc)


def main():
    print_title()
    get_file()

def print_title():
    print('------------------------------')
    print('--------HYDRATING ACL---------')
    print('------------------------------')


if __name__ == '__main__':
    main()
