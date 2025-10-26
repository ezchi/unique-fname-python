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

    if args.clear:
        for field in ['checksum', 'date', 'time', 'number']:
            if field in parts:
                del parts[field]
    else:
        if not args.add and not args.remove and not args.clear:
            parts['checksum'] = get_checksum(filename)
            parts['date'] = get_date(filename)
            parts['time'] = get_time(filename)
            parts['number'] = get_number()
        if args.add:
            for field in args.add:
                if field == 'checksum':
                    parts['checksum'] = get_checksum(filename)
                elif field == 'date':
                    parts['date'] = get_date(filename)
                elif field == 'time':
                    parts['time'] = get_time(filename)
                elif field == 'number':
                    parts['number'] = get_number()

        if args.remove:
            for field in args.remove:
                if field in parts:
                    del parts[field]

    new_fname = construct_fname(parts, os.path.dirname(filename))
    if args.rename:
        i = 1
        while os.path.exists(new_fname):
            i += 1
            parts['number'] = f'{i:04d}'
            new_fname = construct_fname(parts, os.path.dirname(filename))
        os.rename(filename, new_fname)
    else:
        print(new_fname)

def main():
    parser = argparse.ArgumentParser(description='Generate unique filenames.')
    parser.add_argument('path', help='The path to process. Can be a file, a directory, or a glob pattern.')
    parser.add_argument('--add', nargs='+', choices=['checksum', 'date', 'time', 'number'], help='Add optional fields.')
    parser.add_argument('--remove', nargs='+', choices=['checksum', 'date', 'time', 'number'], help='Remove optional fields.')
    parser.add_argument('--clear', action='store_true', help='Clear all optional fields.')
    parser.add_argument('--rename', action='store_true', help='Rename the file.')
    parser.add_argument('-r', '--recursive', action='store_true', help='Recursively process files in subdirectories.')

    args = parser.parse_args()

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
