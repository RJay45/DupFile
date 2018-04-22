#!/usr/bin/env python
#
# (c) Jason "RJay45" Griffith 2017
#
import argparse
import os.path
from os import scandir
from os.path import isfile
import hashlib
import shutil
import sys
import json
from time import gmtime, strftime


def progress(filename):
    progress.count += 1
    if progress.count >= 25:
        progress.count = 0
        try:
            output = "Current File: " + filename
            width = shutil.get_terminal_size((80, 20)).columns - 1
            if len(output) > width:
                output = output[:width]
            sys.stdout.write("\r" + output + ' ' * (shutil.get_terminal_size((80, 20)).columns - len(output) - 1))
            sys.stdout.flush()
        except UnicodeEncodeError:
            # FIXME: Some file names have UTF-16 characters in them which cause exceptions when writing to STDOUT.
            return


progress.count = 25


def hash_file(file):
    try:
        hash = hashlib.sha1()
        f = open(file, "rb")
        hash.update(f.read())
        f.close()
        return hash.hexdigest()
    except Exception:
        return "Unable to open file to hash"


def traverse(current_path, results, recurse=True):
    try:
        for file in scandir(current_path):
            progress(file.path)

            if file.is_file(follow_symlinks=False):
                # Convert this to a string to make merging loaded JSON debug files easier.
                try:
                    size = file.stat(follow_symlinks=False).st_size
                except OSError:
                    print("Unable to get size of file " + file.path + ", skipping.")
                    continue

                # We only compute hashes when there are two files of the same size,
                # otherwise we'll leave an indicator and run the hash later if we find a second same-sized file.
                if size not in results:
                    results[size] = {
                        'first': file.path
                    }
                    continue

                elif 'first' in results[size]:
                    results[size][hash_file(results[size]['first'])] = [results[size]['first']]
                    results[size].pop('first', None)

                hsum = hash_file(file.path)
                if hsum not in results[size]:
                    results[size][hsum] = [file.path]
                else:
                    results[size][hsum].append(file.path)
            elif recurse:
                # Don't follow symlinks.
                if file.is_symlink():
                    return

                traverse(file.path, results)
    except Exception:
        print("Unable to scan directory: " + current_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('PATH', help="Path to search for duplicate files. If multiple paths are given, files from all "
                                     "paths will be compared to each other.", nargs='+')
    parser.add_argument('-d', '--debug', help="Enable debug mode. This will output a debug file containing the results"
                        " array", action="store_true")
    parser.add_argument('-r', '--resume', help="Resume a previous run by using a generated debug file",
                        default=None, type=str)
    parser.add_argument('-R', '--no-recurse', help="Disable file recursion",
                        default=False, action="store_true")
    args = parser.parse_args()

    # Quick check that the paths are valid before we continue
    errors = ""
    for path in args.PATH:
        if not os.path.isdir(path):
            errors += "\n" + path + " is not a directory."

    if errors != "":
        print("Error:" + errors)
        exit()

    results = {}

    if args.resume is not None:
        if not isfile(args.resume):
            print("Cannot load previous results, file " + args.resume + " does not exist.")
            exit()

        print("Loading results from " + args.resume + "...")
        try:
            f = open(args.resume, "r")
            results = json.load(f)
            f.close()
        except Exception:
            print("Unable to read or parse debug file.")
            exit()
        print("Loading complete.");

    for path in args.PATH:
        traverse(path, results, not args.no_recurse)

    datestamp = strftime("%Y%m%d_%H%M%S", gmtime())

    f = open("./output_" + datestamp + ".csv", "w")

    f.write('Hash,Size,Name\n')

    for size in results:
        if 'first' in results[size]:
            continue

        for hsum in results[size]:
            if len(results[size][hsum]) > 1:
                for file_name in results[size][hsum]:
                    f.write(hsum + "," + str(size) + "," + file_name + '\n')

    f.close()
    if args.debug:
        f = open("./debug_" + datestamp + ".txt", "w")

        f.write(json.dumps(results, indent=2))
        f.close()


main()

