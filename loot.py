#!/bin/env python3
'''
loot.py

A simple, configurable loot roller.
'''


# ------- Python Library Imports -------

# Standard Library
import argparse
import copy
import os
import random
import sys

# Additional Dependencies
try:
    import yaml
except ImportError as e:
    sys.exit('Unable to import PyYAML library - ' + str(e) + '.')

# --------------------------------------



# ----------- Initialization -----------

HELP_DESCRIPTION = """
A simple, configurable loot roller.
"""

HELP_EPILOG = """

----- Environment Variables -----

The following maps each available environment variable with its corresponding CLI argument:

LOOT_CONFIG_FILE  :  --config-file
"""

# Color Sequences
C_BLUE   = '\033[94m'
C_GREEN  = '\033[92m'
C_ORANGE = '\033[93m'
C_RED    = '\033[91m'
C_END    = '\033[0m'
C_BOLD   = '\033[1m'

# --------------------------------------



# ---------- Private Functions ---------

def _c(instring, color=C_BLUE):
    '''
    Colorizes the specified string.
    '''
    if args.color_output and not color is None:
        return color + instring + C_END
    else:
        return instring


def _parse_arguments():
    '''
    Parses the command-line arguments into a global namespace called "args".
    '''
    argparser = argparse.ArgumentParser(
        description = HELP_DESCRIPTION,
        epilog = HELP_EPILOG,
        usage = 'loot [-c FILE] [-C INT] [-t TABLE]',
        add_help = False,
        formatter_class = lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=45, width=100)
    )
    argparser.add_argument(
        '-c',
        '--config-file',
        default = os.getenv('LOOT_CONFIG_FILE', 'loot.yaml'),
        dest = 'config_file',
        help = 'Specifies the configuration file to load loot table definitions from. Defaults to "loot.yaml".',
        metavar = 'FILE'
    )
    argparser.add_argument(
        '-C',
        '--count',
        default = 1,
        dest = 'count',
        help = 'Specifies the number of loot rolls to generate. Defaults to "1".',
        metavar = 'INT',
        type = int
    )
    argparser.add_argument(
        '-t',
        '--table',
        default = '',
        dest = 'table',
        help = 'Specifies the name table to start with. Subtables may be specified using a path-like syntax. Defaults to the root table.',
        metavar = 'TABLE'
    )
    argparser.add_argument(
        '-h',
        '--help',
        action = 'help',
        help = 'Displays help and usage information.'
    )
    argparser.add_argument(
        '--no-color',
        action = 'store_false',
        dest = 'color_output',
        help = 'Disables color output to stdout/stderr.'
    )
    global args
    args = argparser.parse_args()

# --------------------------------------



# ---------- Public Functions ----------


def get_loot(item):
    if isinstance(item, str):
        return item
    buildup = []
    for i in item:
        if isinstance(i, str):
            buildup.append(i)
        elif 'weight' in i:
            buildup.extend([i['name']] * i['weight'])
        else:
            buildup.append(i['name'])
    selected = random.choice(buildup)
    for i in item:
        if isinstance(i, str):
            if i == selected:
                return i
        elif i['name'] == selected:
            if 'loot' in i:
                if 'types' in i:
                    return get_loot(i['loot']) + ' (' + get_loot(non_loot[i['types']]) + ')'
                else:
                    return get_loot(i['loot'])
            else:
                return i['name']

def main():
    '''
    The entrypoint of the script.
    '''
    # Parse command-line arguments
    _parse_arguments()

    if not os.path.isfile(args.config_file):
        sys.exit('Specified loot file doesn\'t exist.')

    try:
        with open(args.config_file, 'r') as f:
            config = yaml.safe_load(f.read())
    except Exception as e:
        sys.exit('Unable to load configuration file - ' + str(e))

    global non_loot
    non_loot = copy.deepcopy(config)
    non_loot.pop('loot')

    table_path = args.table.strip('/').split('/')

    config = config['loot']
    types = ''
    if table_path and table_path[0]:
        for p in table_path:
            found = False
            for i in config:
                if i['name'] == p:
                    config = i['loot']
                    if 'types' in i:
                        types = i['types']
                    found = True
                    break
            if not found:
                sys.exit('Specified start table doesn\'t exist.')

    for i in range(args.count):
        if types:
            print(get_loot(config) + ' (' + get_loot(non_loot[types]) + ')')
        else:
            print(get_loot(config))

    print('')

# --------------------------------------



# ---------- Boilerplate Magic ---------

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError) as ki:
        sys.stderr.write('Recieved keyboard interrupt!\n')
        sys.exit(100)

# --------------------------------------
