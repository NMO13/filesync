import os


def create_structure(src_files, dest_files):
    os.mkdir("simpletest")
    os.mkdir("simpletest/1")
    os.mkdir("simpletest/1/a")
    for file in src_files:
        if os.path.dirname(file):
            os.mkdir(os.path.join("simpletest/1/a", os.path.dirname(file)))
        open(os.path.join("simpletest/1/a", file), "a").close()

    os.mkdir("simpletest/2")
    os.mkdir("simpletest/2/a")
    for file in dest_files:
        if os.path.dirname(file):
            os.mkdir(os.path.join("simpletest/2/a", os.path.dirname(file)))
        open(os.path.join("simpletest/2/a", file), "a").close()
