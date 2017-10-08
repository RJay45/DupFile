# DupFile
This is a simple utility that will scan a directory tree and output a CSV file of duplicate files.
It uses SHA1 to compute the hash of like sized files and compare them.

usage: DupFile [-h] [-d] PATH [PATH ...]

positional arguments:
  PATH         Path to search for duplicate files. If multiple paths are
               given, files from all paths will be compared to each other.

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  Enable debug mode. This will output a debug file containing the
               results array
