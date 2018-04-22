# DupFile
This is a simple utility that will scan a directory tree and output a CSV file of duplicate files.
It uses SHA1 to compute the hash of like sized files and compare them.

```
usage: df.py [-h] [-d] [-r RESUME] [-R NO_RECURSE] PATH [PATH ...]

positional arguments:
  PATH                  Path to search for duplicate files. If multiple paths
                        are given, files from all paths will be compared to
                        each other.

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Enable debug mode. This will output a debug file
                        containing the results array
  -r RESUME, --resume RESUME
                        Resume a previous run by using a generated debug file
  -R NO_RECURSE, --no-recurse NO_RECURSE
                        Disable file recursion
```