import glob, os
import filecmp


def get_files_recursive(dir, all_files):
    files_in_directory = glob.glob(os.path.join(dir, '*'))
    files_in_directory.sort(key=lambda x: os.path.basename(x))
    for file in files_in_directory:
        if os.path.isdir(file):
            all_files.append(file)
            get_files_recursive(file, all_files)
            print('Finished directory {}'.format(file))
        else:
            all_files.append(file)

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str)
    parser.add_argument("dest", type=str)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="explain what is beeing done")
    parser.add_argument('-s', '--sync', action='store_true',
                        help="synchronize source with destination")

    # Parse the arguments
    return parser.parse_args()

def check_directory_exists(path):
    if not os.path.exists(path):
        raise ValueError("{} does not exist".format(path))

def mark_inconsistent(path, file, type, state):
    global buffer
    if type == "directory":
        type = "d"
    else:
        type = "f"
    buffer.append((type, state, os.path.join(path, file)))

def mark_delete(dest, files_in_directory_dest):
    for file in files_in_directory_dest:
        if os.path.isdir(os.path.join(dest, file)):
            mark_inconsistent(dest, file, "directory", "-")
        else:
            mark_inconsistent(dest, file, "file", "-")

def check_consistency(src, dest, verbose):
    if verbose:
        print("Processing {}".format(src))
    files_in_directory_src = os.listdir(src)

    try:
        files_in_directory_dest = os.listdir(dest)
    except FileNotFoundError:
        files_in_directory_dest = []

    # if a file in src is not found
    for file in files_in_directory_src:
        if os.path.isdir(os.path.join(src, file)):
            # check if directory name can be found
            if file in files_in_directory_dest:
                files_in_directory_dest.remove(file)
            else:
                mark_inconsistent(src, file, "directory", "+")
            check_consistency(os.path.join(src, file), os.path.join(dest, file), verbose)
        else:
            # check if file can be found
            file_exists = file in files_in_directory_dest
            if not (file_exists and filecmp.cmp(os.path.join(src, file), os.path.join(dest, file), shallow=False)):
                mark_inconsistent(src, file, "file", "+")
            else:
                files_in_directory_dest.remove(file)

    # the rest of the files in dest need to be deleted
    mark_delete(dest, files_in_directory_dest)
    if verbose:
        print("Finished {}".format(src))

def print_inconsistent(message):
    print("{}{} {}".format(message[1], message[0], message[2]))

def synchronize():
    global buffer
    pass


def main():
    global buffer
    buffer = []
    args = parse_args()
    check_directory_exists(args.src)
    check_directory_exists(args.dest)

    check_consistency(args.src, args.dest, args.verbose)
    print("### Result ###")
    if len(buffer) == 0:
        print("Contents are identical.")
    else:
        [print_inconsistent(message) for message in buffer]
    if args.sync:
        print("Syncing...")
        synchronize()

if __name__ == '__main__':
    main()

