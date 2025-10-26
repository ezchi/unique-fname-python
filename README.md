# unique-fname

A Python script to generate and manage unique filenames.

## Installation

Install the script using `pip`:

```bash
pip install .
```

## Usage

### Rename files

```bash
unique-fname rename <path> [--tags <tags>] [--rename] [-r]
```

-   `<path>`: The path to process. Can be a file, a directory, or a glob pattern.
-   `--tags <tags>`: The tags to include in the filename. Can be `checksum`, `date`, `time`, `number`.
-   `--rename`: Rename the file instead of printing the new name.
-   `-r`, `--recursive`: Recursively process files in subdirectories.

If `--tags` is not specified, all tags will be added by default.

### Find duplicate files

```bash
unique-fname find-dups <path>
```

-   `<path>`: The path to scan for duplicate files.

This command will recursively scan the files in the given path, parse the filenames to extract the MD5 checksum, and print the groups of files with the same checksum. It ignores files that do not have a checksum in their filename and does not recalculate the MD5 checksum.

## Examples

### Add all tags to a file

```bash
unique-fname rename foo.txt
```

### Add checksum and date to all .txt files in the current directory

```bash
unique-fname rename "*.txt" --tags checksum date
```

### Rename all files in the `~/tmp/test` directory recursively

```bash
unique-fname rename ~/tmp/test -r --rename
```

### Remove the date field from a file

```bash
unique-fname rename d41d8cd98f00b204e9800998ecf8427e-20011125-153008-0001-fn-foo.txt --tags checksum time number
```

### Clear all tags from a file

```bash
unique-fname rename d41d8cd98f00b204e9800998ecf8427e-20011125-153008-0001-fn-foo.txt --tags
```

### Find duplicate files in a directory

```bash
unique-fname find-dups ~/tmp/test
```
