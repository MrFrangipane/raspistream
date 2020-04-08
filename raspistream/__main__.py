import logging
import argparse
from raspistream.runner import Runner


def parse_args(args=None):
    default_runner = Runner()

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--filename', help='Use this if you want to pass a file instead of args, see example.raspistream in Github')

    for name, default in sorted(vars(default_runner).items()):
        if name.startswith('_'): continue

        fullname = '--{}'.format(name.replace('_', '-'))
        shortname = '-{}'.format(''.join(item[0] for item in name.split('_')))
        type_ = type(getattr(default_runner, name))

        if name == 'vid_resolution':
            default = '{}x{}'.format(*default)

        parser.add_argument(shortname, fullname, type=type_, default=default, help='Defaults to {}'.format(default))

    args = parser.parse_args(args)
    return args


def file_to_args(filename):
    with open(filename, 'r') as f_profile:
        command_line = f_profile.readlines()
        command_line = [line.strip() for line in command_line]
        command_line = ' '.join(command_line)
        command_line = command_line.split(' ')
        command_line = [item for item in command_line if item]

    return command_line


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    runner = Runner()

    args = parse_args()
    if args.filename:
        args = parse_args(file_to_args(args.filename))

    for i, v in vars(args).items():
        if i == 'vid_resolution':
            try:
                v = ''.join(v).split('x')
            except TypeError as e:
                pass

        setattr(runner, i, v)

    runner.run()
