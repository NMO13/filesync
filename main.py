import os
from pathlib import Path
import filecmp


base_src = ""
base_dest = ""


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str)
    parser.add_argument("dest", type=str)

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="explain what is beeing done"
    )
    parser.add_argument(
        "-s", "--sync", action="store_true", help="synchronize source with destination"
    )

    # Parse the arguments
    return parser.parse_args()


def check_directory_exists(path):
    if not os.path.exists(path):
        raise ValueError("{} does not exist".format(path))


def mark_inconsistent(path, file, type, state, base, add_buffer, delete_buffer):
    if type == "directory":
        type = "d"
    else:
        type = "f"
    x = os.path.relpath(os.path.join(path, file), base)
    if state == "+":
        add_buffer.append((type, state, x))
    elif state == "-":
        delete_buffer.append((type, state, x))


def mark_delete(dest, files_in_directory_dest, add_buffer, delete_buffer):
    for file in files_in_directory_dest:
        if os.path.isdir(os.path.join(dest, file)):
            mark_inconsistent(
                dest, file, "directory", "-", base_dest, add_buffer, delete_buffer
            )
        else:
            mark_inconsistent(
                dest, file, "file", "-", base_dest, add_buffer, delete_buffer
            )


def check_consistency(src, dest, verbose, add_buffer, delete_buffer):
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
                mark_inconsistent(
                    src, file, "directory", "+", base_src, add_buffer, delete_buffer
                )
            check_consistency(os.path.join(src, file), os.path.join(dest, file), verbose, add_buffer, delete_buffer)
        else:
            # check if file can be found
            file_exists = file in files_in_directory_dest
            if not (
                file_exists
                and filecmp.cmp(
                    os.path.join(src, file), os.path.join(dest, file), shallow=False
                )
            ):
                mark_inconsistent(
                    src, file, "file", "+", base_src, add_buffer, delete_buffer
                )
            else:
                files_in_directory_dest.remove(file)

    # the rest of the files in dest need to be deleted
    mark_delete(dest, files_in_directory_dest, add_buffer, delete_buffer)
    if verbose:
        print("Finished {}".format(src))


def print_inconsistent(message):
    print("{}{} {}".format(message[1], message[0], message[2]))


def synchronize(verbose, add_buffer, delete_buffer):
    for p in delete_buffer:
        # 1. delete stale directories
        if p[0] == "d" and p[1] == "-":
            import shutil

            shutil.rmtree(os.path.join(base_dest, p[2]))
            if verbose is True:
                print("Deleted directory {}".format(p[2]))
        # 2. delete stale files
        elif p[0] == "f" and p[1] == "-":
            import shutil

            os.remove(os.path.join(base_dest, p[2]))
            if verbose is True:
                print("Deleted file {}".format(p[2]))

    for p in add_buffer:
        # 1. make new directories
        if p[0] == "d" and p[1] == "+":
            Path(os.path.join(base_dest, p[2])).mkdir(parents=True, exist_ok=True)
            if verbose is True:
                print("Created directory {}".format(p[2]))
        # 2. make new files
        elif p[0] == "f" and p[1] == "+":
            from shutil import copyfile

            # os.makedirs(os.path.dirname(os.path.join(base_dest, p[2])), exist_ok=True)
            copyfile(os.path.join(base_src, p[2]), os.path.join(base_dest, p[2]))
            if verbose is True:
                print("Created file {}".format(p[2]))


def main():
    global base_src, base_dest

    args = parse_args()

    check_directory_exists(args.src)
    check_directory_exists(args.dest)

    base_src = args.src
    base_dest = args.dest

    if base_src == base_dest:
        raise ValueError("Source and destination directories are equal.")

    add_buffer, delete_buffer = analyse_diffs(
        args.src, args.dest, args.verbose
    )

    print("### Result ###")
    if len(delete_buffer) == 0 and len(add_buffer) == 0:
        print("Contents are identical.")
        print("Nothing to do.")
        return
    else:
        print("Files to add:")
        print("-------------")
        [print_inconsistent(message) for message in add_buffer]

        print("\nFiles to delete:")
        print("----------------")
        [print_inconsistent(message) for message in delete_buffer]

    if args.sync:
        print("Syncing...")
        synchronize(args.verbose, add_buffer, delete_buffer)
    else:
        option = input("Do you want to synchronize now? [y/N] ")
        if option == "y":
            synchronize(args.verbose, add_buffer, delete_buffer)
        else:
            print("Abort.")


def analyse_diffs(src, dest, verbose):
    add_buffer = []
    delete_buffer = []
    print("Starting diff analysis synchronously")
    check_consistency(src, dest, verbose, add_buffer, delete_buffer)

    return add_buffer, delete_buffer

if __name__ == "__main__":
    main()
