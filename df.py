#
# (c) Jason "RJay45" Griffith 2017
#
import argparse
import os.path
from os import listdir
from os.path import isfile, join
import pathlib
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


def traverse(current_path, results):
    # Don't follow symlinks.
    if pathlib.Path(current_path).is_symlink():
        return

    for file in listdir(current_path):
        try:
            full_name = join(current_path, file)
            progress(full_name)

            if isfile(full_name):
                # Convert this to a string to make merging loaded JSON debug files easier.
                size = str(os.path.getsize(full_name))

                # We only compute hashes when there are two files of the same size,
                # otherwise we'll leave an indicator and run the hash later if we find a second same-sized file.
                if size not in results:
                    results[size] = {
                        'first': full_name
                    }
                    continue

                elif 'first' in results[size]:
                    results[size][hash_file(results[size]['first'])] = [results[size]['first']]
                    results[size].pop('first', None)

                hsum = hash_file(full_name)
                if hsum not in results[size]:
                    results[size][hsum] = [full_name]
                else:
                    results[size][hsum].append(full_name)
            else:
                traverse(full_name, results)
        except Exception as e:
            print("Exception: ", "\n\nCurrent File:", full_name, "\n\nSize:", os.path.getsize(full_name),
                  "\n\nCurrent Results:", results, "\n\n")
            raise e


def main():
    parser = argparse.ArgumentParser("DupFile")
    parser.add_argument('PATH', help="Path to search for duplicate files. If multiple paths are given, files from all "
                                     "paths will be compared to each other.", nargs='+')
    parser.add_argument('-d', '--debug', help="Enable debug mode. This will output a debug file containing the results"
                        " array", action="store_true")
    parser.add_argument('-r', '--resume', help="Resume a previous run by using a generated debug file",
                        default=None, type=str)
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
        traverse(path, results)

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

