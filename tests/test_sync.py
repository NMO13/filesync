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
            outs, errs = proc.communicate(timeout=120, input=b"y")
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        outs = outs.decode("utf-8").replace("\r", "")
        errs = errs.decode("utf-8").replace("\r", "")
        return outs, errs


def test_sync_dir():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure([], [])
    os.mkdir("simpletest/1/a/x/")
    _exec("simpletest/1/a", "simpletest/2/a")
    assert os.path.exists("simpletest/2/a/x/")
    shutil.rmtree("simpletest")


def test_sync_dirs():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure([], [])
    os.mkdir("simpletest/1/a/x/")
    os.mkdir("simpletest/1/a/x/x2")
    os.mkdir("simpletest/1/a/y/")
    _exec("simpletest/1/a", "simpletest/2/a")
    assert os.path.exists("simpletest/2/a/x/")
    assert os.path.exists("simpletest/2/a/x/x2")
    assert os.path.exists("simpletest/2/a/y/")
    shutil.rmtree("simpletest")


def test_sync_files():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(
        ["1.txt", "2.txt", "c/1c.txt", "c/d/4.txt"], ["2.txt", "3.txt", "c/2c.txt"]
    )
    _exec("simpletest/1/a", "simpletest/2/a")
    assert os.path.exists("simpletest/2/a/c/d/4.txt")
    assert os.path.exists("simpletest/2/a/1.txt")
    assert os.path.exists("simpletest/2/a/2.txt")
    assert not os.path.exists("simpletest/2/a/3.txt")
    assert os.path.exists("simpletest/2/a/c/1c.txt")
    assert not os.path.exists("simpletest/2/a/c/2c.txt")
    shutil.rmtree("simpletest")


def test_sync_same_name():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass
    create_structure(["1.txt", "2.txt"], ["1.txt", "2.txt"])
    f = open("simpletest/1/a/1.txt", "w+")
    f.write("A")
    f.close()
    f = open("simpletest/1/a/2.txt", "w+")
    f.write("A")
    f.close()
    _exec("simpletest/1/a", "simpletest/2/a")
    assert os.path.exists("simpletest/2/a/1.txt")
    assert os.path.exists("simpletest/2/a/2.txt")
    shutil.rmtree("simpletest")


def test_sync_diff():
    from main import analyse_diffs

    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    create_structure(
        ["1.txt", "c/2.txt", "d/3.txt", "k/e/4.txt"],
        ["1.txt", "2.txt", "3.txt", "g/h/5.txt"],
    )
    analyse_diffs("simpletest/1/a", "simpletest/2/a", False)

    _exec("simpletest/1/a", "simpletest/2/a")
    assert os.path.exists("simpletest/2/a/c/2.txt")
    assert os.path.exists("simpletest/2/a/d/3.txt")
    assert os.path.exists("simpletest/2/a/k/e/4.txt")
    assert not os.path.exists("simpletest/2/a/2.txt")
    assert not os.path.exists("simpletest/2/a/3.txt")
    assert not os.path.exists("simpletest/2/a/g")

    shutil.rmtree("simpletest")
