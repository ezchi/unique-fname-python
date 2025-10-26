# unique-fname

A Python script to generate and manage unique filenames.

## Installation

Install the script using `pip`:

```bash
pip install .
```

## Usage

### Add optional fields

```bash
unique-fname add <path> [--add <fields>] [--rename] [-r]
```

-   `<path>`: The path to process. Can be a file, a directory, or a glob pattern.
-   `--add <fields>`: The optional fields to add. Can be `checksum`, `date`, `time`, `number`.
-   `--rename`: Rename the file instead of printing the new name.
-   `-r`, `--recursive`: Recursively process files in subdirectories.

If `--add` is not specified, all optional fields will be added by default.

### Remove optional fields

```bash
unique-fname remove <path> --remove <fields> [--rename] [-r]
```

-   `<path>`: The path to process. Can be a file, a directory, or a glob pattern.
-   `--remove <fields>`: The optional fields to remove. Can be `checksum`, `date`, `time`, `number`.
-   `--rename`: Rename the file instead of printing the new name.
-   `-r`, `--recursive`: Recursively process files in subdirectories.

### Clear all optional fields

```bash
unique-fname clear <path> [--rename] [-r]
```

-   `<path>`: The path to process. Can be a file, a directory, or a glob pattern.
-   `--rename`: Rename the file instead of printing the new name.
-   `-r`, `--recursive`: Recursively process files in subdirectories.

### Find duplicate files

```bash
unique-fname find-dups <path>
```

-   `<path>`: The path to scan for duplicate files.

This command will recursively scan the files in the given path, parse the filenames to extract the MD5 checksum, and print the groups of files with the same checksum. It ignores files that do not have a checksum in their filename and does not recalculate the MD5 checksum.

## Examples

### Add all optional fields to a file

```bash
unique-fname add foo.txt
```

### Add checksum and date to all .txt files in the current directory

```bash
unique-fname add "*.txt" --add checksum date
```

### Rename all files in the `~/tmp/test` directory recursively

```bash
unique-fname add ~/tmp/test -r --rename
```

### Remove the date field from a file

```bash
unique-fname remove d41d8cd98f00b204e9800998ecf8427e-20011125-153008-0001-fn-foo.txt --remove date
```

### Clear all optional fields from a file

```bash
unique-fname clear d41d8cd98f00b204e9800998ecf8427e-20011125-153008-0001-fn-foo.txt
```

### Find duplicate files in a directory

```bash
unique-fname find-dups ~/tmp/test
```
