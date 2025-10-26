import argparse

import os
import hashlib
import datetime
import re

def get_checksum(filename):
    with open(filename, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_date(filename):
    stat = os.stat(filename)
    try:
        return datetime.datetime.fromtimestamp(stat.st_birthtime).strftime('%Y%m%d')
    except AttributeError:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        return datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y%m%d')

def get_time(filename):
    stat = os.stat(filename)
    try:
        return datetime.datetime.fromtimestamp(stat.st_birthtime).strftime('%H%M%S')
    except AttributeError:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        return datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%H%M%S')

def get_number():
    return '0001'

def parse_fname(filename):
    parts = {}
    base, ext = os.path.splitext(os.path.basename(filename))
    match = re.match(r'((?P<checksum>[a-f0-9]{32})-)?((?P<date>\d{8})-)?((?P<time>\d{6})-)?((?P<number>\d{4})-)?fn-(?P<orignal_filename>.*)', base)
    if match:
        parts = match.groupdict()
        parts['ext'] = ext
    return parts

def construct_fname(parts, directory='.'):
    order = ['checksum', 'date', 'time', 'number']
    prefix = ''
    for key in order:
        if parts.get(key):
            prefix += parts[key] + '-'

    if prefix:
        new_name = prefix + 'fn-' + parts['orignal_filename'] + parts['ext']
    else:
        new_name = parts['orignal_filename'] + parts['ext']
    return os.path.join(directory, new_name)

import glob

def process_file(filename, args):
    parts = parse_fname(filename)
    if not parts:
        # Not a unique filename, treat as a new file
        base, ext = os.path.splitext(os.path.basename(filename))
        parts = {'orignal_filename': base, 'ext': ext}

    if args.tags is None:
        args.tags = ['checksum', 'date', 'time', 'number']

    all_tags = ['checksum', 'date', 'time', 'number']

    for tag in all_tags:
        if tag in args.tags:
            if tag == 'checksum':
                parts['checksum'] = get_checksum(filename)
            elif tag == 'date':
                parts['date'] = get_date(filename)
            elif tag == 'time':
                parts['time'] = get_time(filename)
            elif tag == 'number':
                if 'number' not in parts:
                    parts['number'] = get_number()
        else:
            if tag in parts:
                del parts[tag]

    new_fname = construct_fname(parts, os.path.dirname(filename))

    if new_fname == filename:
        return

    if not args.dry_run:
        if os.path.exists(new_fname):
            if 'number' in parts:
                i = 1
                if parts['number']:
                    i = int(parts['number'])
                while os.path.exists(new_fname):
                    i += 1
                    parts['number'] = f'{i:04d}'
                    new_fname = construct_fname(parts, os.path.dirname(filename))
                os.rename(filename, new_fname)
            else:
                # Collision and no number to increment, so skip rename
                return
        else:
            os.rename(filename, new_fname)
    else:
        if new_fname != filename:
            print(new_fname)

def find_dups(path):
    checksums = {}
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith('.'):
                continue
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                parts = parse_fname(filepath)
                if parts and parts.get('checksum'):
                    checksum = parts['checksum']
                    if checksum not in checksums:
                        checksums[checksum] = []
                    checksums[checksum].append(filepath)

    for checksum, files in checksums.items():
        if len(files) > 1:
            print(f'Files with checksum: {checksum}')
            for file in files:
                print(f'  {file}')

def main():
    parser = argparse.ArgumentParser(description='Generate unique filenames.')
    subparsers = parser.add_subparsers(dest='command')

    # Rename command
    rename_parser = subparsers.add_parser('rename', help='Rename a file with the given tags.')
    rename_parser.add_argument('path', help='The path to process. Can be a file, a directory, or a glob pattern.')
    rename_parser.add_argument('--tags', nargs='*', choices=['checksum', 'date', 'time', 'number'], help='The tags to include in the filename.')
    rename_parser.add_argument('--dry-run', action='store_true', help='Print the new name without renaming the file.')
    rename_parser.add_argument('-r', '--recursive', action='store_true', help='Recursively process files in subdirectories.')

    # Find-dups command
    find_dups_parser = subparsers.add_parser('find-dups', help='Find files with the same MD5 checksum.')
    find_dups_parser.add_argument('path', help='The path to scan for duplicate files.')

    args = parser.parse_args()

    if args.command == 'find-dups':
        find_dups(args.path)
    elif args.command == 'rename':
        if os.path.isdir(args.path):
            if args.recursive:
                for dirpath, _, filenames in os.walk(args.path):
                    for filename in filenames:
                        if filename.startswith('.'):
                            continue
                        filepath = os.path.join(dirpath, filename)
                        process_file(filepath, args)
            else:
                for filename in os.listdir(args.path):
                    if filename.startswith('.'):
                        continue
                    filepath = os.path.join(args.path, filename)
                    if os.path.isfile(filepath):
                        process_file(filepath, args)
        else:
            for filename in glob.glob(args.path):
                if os.path.basename(filename).startswith('.'):
                    continue
                if os.path.isfile(filename):
                    process_file(filename, args)


if __name__ == '__main__':
    main()
