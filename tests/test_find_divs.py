import sys, subprocess
import os
import shutil
from tests import create_structure


def _exec(src, dest):
    with subprocess.Popen(
        [sys.executable, "../main.py", src, dest],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as proc:
        try:
            outs, errs = proc.communicate(timeout=120, input=b"n")
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        outs = outs.decode("utf-8").replace("\r", "")
        errs = errs.decode("utf-8").replace("\r", "")
        return outs, errs


def test_src_diverging_base():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    os.mkdir("simpletest")
    os.mkdir("simpletest/1")
    os.mkdir("simpletest/1/a")
    os.mkdir("simpletest/1/a/a1")

    os.mkdir("simpletest/2")
    os.mkdir("simpletest/2/b")
    os.mkdir("simpletest/2/b/b1")

    outs, errs = _exec("simpletest/1/a", "simpletest/2/b")
    assert "+d a1\n-d b1\n" in outs
    assert errs == ""
    shutil.rmtree("simpletest")


def test_src_invalid():
    outs, errs = _exec("a", "b")
    assert "a does not exist" in errs


def test_dest_invalid():
    try:
        shutil.rmtree("a")
    except FileNotFoundError:
        pass

    os.mkdir("a")
    outs, errs = _exec("a", "b")
    assert "b does not exist" in errs
    shutil.rmtree("a")


def test_src_equals_dest():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass
    os.mkdir("simpletest")
    os.mkdir("simpletest/1")
    os.mkdir("simpletest/1/a")

    outs, errs = _exec("simpletest/1/a", "simpletest/1/a")
    assert "Source and destination directories are equal." in errs

    shutil.rmtree("simpletest")


def test_simple_diff_common_files():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(["1.txt", "2.txt"], ["2.txt", "3.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert "+f 1.txt\n-f 3.txt\n" in outs
    assert errs == ""
    shutil.rmtree("simpletest")


def test_simple_diff_common_dirs():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(["1.txt", "2.txt", "c/1c.txt"], ["2.txt", "3.txt", "c/1c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert "+f 1.txt\n-f 3.txt\n" in outs
    assert errs == ""
    shutil.rmtree("simpletest")


def test_simple_diff_divergent_dirs():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(["1.txt", "2.txt", "c/1c.txt"], ["2.txt", "3.txt", "c/2c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert "+f 1.txt\n+f c/1c.txt\n-f c/2c.txt\n-f 3.txt\n" in outs
    assert errs == ""
    shutil.rmtree("simpletest")


def test_empty_src():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure([], ["2.txt", "3.txt", "c/2c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert "-f 2.txt\n-d c\n-f 3.txt\n" in outs
    assert errs == ""
    shutil.rmtree("simpletest")


def test_empty_dest():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(["2.txt", "3.txt", "c/2c.txt"], [])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert "+f 2.txt\n+d c\n+f c/2c.txt\n+f 3.txt\n" in outs
    assert errs == ""
    shutil.rmtree("simpletest")


def test_hidden_files():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(
        ["1.txt", "2.txt", "c/1c.txt", "d/.1d.txt"],
        ["2.txt", "3.txt", "c/2c.txt", "e/1e.txt"],
    )
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert (
        "+f 1.txt\n+f c/1c.txt\n-f c/2c.txt\n+d d\n+f d/.1d.txt\n-d e\n-f 3.txt\n"
        in outs
    )
    assert errs == ""
    shutil.rmtree("simpletest")


def test_same_file_different_content():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    os.mkdir("simpletest")
    os.mkdir("simpletest/1")
    os.mkdir("simpletest/1/a")
    f = open("simpletest/1/a/file1", "w+")
    f.write("A")
    f.close()

    os.mkdir("simpletest/2")
    os.mkdir("simpletest/2/b")
    f = open("simpletest/2/b/file1", "w+")
    f.write("B")
    f.close()

    outs, errs = _exec("simpletest/1/a", "simpletest/2/b")
    assert "+f file1\n-f file1\n" in outs
    assert errs == ""
    shutil.rmtree("simpletest")


def test_identical():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(["1.txt", "2.txt", "c/1c.txt"], ["1.txt", "2.txt", "c/1c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert "Contents are identical" in outs
    assert errs == ""
    shutil.rmtree("simpletest")
