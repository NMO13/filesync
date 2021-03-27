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

    # Parse the arguments
    return parser.parse_args()

def check_directory_exists(path):
    if not os.path.exists(path):
        raise ValueError("{} does not exist".format(path))

def mark_inconsistent(path, file, type, state):
    if type == "directory":
        print("{}d {}".format(state, os.path.join(path, file)))
    else:
        print("{}f {}".format(state, os.path.join(path, file)))

def mark_delete(dest, files_in_directory_dest):
    for file in files_in_directory_dest:
        if os.path.isdir(os.path.join(dest, file)):
            mark_inconsistent(dest, file, "directory", "-")
        else:
            mark_inconsistent(dest, file, "file", "-")

def check_consistency(src, dest):
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
            check_consistency(os.path.join(src, file), os.path.join(dest, file))
        else:
            # check if file can be found
            file_exists = file in files_in_directory_dest
            if not (file_exists and filecmp.cmp(os.path.join(src, file), os.path.join(dest, file), shallow=False)):
                mark_inconsistent(src, file, "file", "+")
            else:
                files_in_directory_dest.remove(file)

    # the rest of the files in dest need to be deleted
    mark_delete(dest, files_in_directory_dest)



def main():
    args = parse_args()
    check_directory_exists(args.src)
    check_directory_exists(args.dest)

    check_consistency(args.src, args.dest)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
