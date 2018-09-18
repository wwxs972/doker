#!/usr/bin/env python

import argparse
import os
import sys
import yaml

from doker import fileutils, generate

def main():
    try:
        import pkg_resources
        __version__ = pkg_resources.get_distribution('doker').version
    except Exception:
        __version__ = 'unknown'

    parser = argparse.ArgumentParser(prog='doker', usage='%(prog)s [options] <project>', add_help=False,
        description='Tool for creating beautiful PDF and HTML documentation.')
    parser.add_argument('project', metavar='<project>', help='Project file in YAML format')
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__, help='Show version and exit')
    parser.add_argument('--pdf', action="store_true", help='Generate documentation in PDF format')
    parser.add_argument('--html', action="store_true", help='Generate documentation in HTML format')

    args = parser.parse_args()
    project_file = args.project

    if not os.path.isfile(project_file):
        project_file += '.yaml'
        if not os.path.isfile(project_file):
            sys.stderr.write('Error: Unable to open project file: ' + project_file + '\n')
            sys.exit(1)
    
    with open(project_file, 'r') as f:
        try:
            project = yaml.load(f)
        except yaml.YAMLError as err:
            sys.stderr.write('Error: Parsing YAML project file failed: ' + err + '\n')
            sys.exit(1)
    current_dir = os.getcwd()
    os.chdir(os.path.abspath(os.path.dirname(project_file)))
    if not 'root' in project:
        project['root'] = '.'
    root_dir = os.path.abspath(project['root'])

    file_tree = fileutils.to_tree(project['files']) if 'files' in project else fileutils.get_tree(root_dir)

    files = []
    if 'index' in file_tree:
        files.append({ 'src': file_tree['index'] })
    files = files + fileutils.to_list(file_tree)

    if args.pdf:
        output_pdf = os.path.splitext(os.path.basename(project_file))[0] + '.pdf'
        generate.pdf(files, project, os.path.join(current_dir, output_pdf))
    elif args.html:
        generate.html(files, project)
    #elif 'script' in project:
        # TODO: Exec the script
    else:
        sys.stderr.write('Error: Either PDF (--pdf) or HTML (--html) format should be chosen\n\n')
        parser.print_help()
        sys.exit(1)

# Start
if __name__ == '__main__':
    main()
