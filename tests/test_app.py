import sys, subprocess
import os
import shutil

def _exec(src, dest):
    with subprocess.Popen([sys.executable, "../main.py", src, dest], stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        try:
            outs, errs = proc.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        outs = outs.decode("utf-8").replace('\r', '')
        errs = errs.decode("utf-8").replace('\r', '')
        return outs, errs


def _create_structure(src_files, dest_files):
    os.mkdir("simpletest")
    os.mkdir("simpletest/1")
    os.mkdir("simpletest/1/a")
    for file in src_files:
        if os.path.dirname(file):
            os.mkdir(os.path.join("simpletest/1/a", os.path.dirname(file)))
        open(os.path.join("simpletest/1/a", file), 'a').close()

    os.mkdir("simpletest/2")
    os.mkdir("simpletest/2/a")
    for file in dest_files:
        if os.path.dirname(file):
            os.mkdir(os.path.join("simpletest/2/a", os.path.dirname(file)))
        open(os.path.join("simpletest/2/a", file), 'a').close()

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

def test_simple_diff_common_files():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure(["1.txt", "2.txt"], ["2.txt", "3.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == '+f 1.txt\n-f 3.txt\n'
    assert errs == ""
    shutil.rmtree("simpletest")

def test_simple_diff_common_dirs():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure(["1.txt", "2.txt", "c/1c.txt"], ["2.txt", "3.txt", "c/1c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == '+f 1.txt\n-f 3.txt\n'
    assert errs == ""
    shutil.rmtree("simpletest")

def test_hidden_files():
    pass

def test_same_file_different_content():
    pass