import os
from pathlib import Path


def create_structure(src_files, dest_files):
    os.mkdir("simpletest")
    os.mkdir("simpletest/1")
    os.mkdir("simpletest/1/a")
    for file in src_files:
        if os.path.dirname(file):
            Path(os.path.dirname(os.path.join("simpletest/1/a", file))).mkdir(
                parents=True, exist_ok=True
            )

        open(os.path.join("simpletest/1/a", file), "a").close()

    os.mkdir("simpletest/2")
    os.mkdir("simpletest/2/a")
    for file in dest_files:
        if os.path.dirname(file):
            Path(os.path.dirname(os.path.join("simpletest/2/a", file))).mkdir(
                parents=True, exist_ok=True
            )
        open(os.path.join("simpletest/2/a", file), "a").close()
