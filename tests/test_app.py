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
    assert outs == "+d simpletest/1/a/a1\n-d simpletest/2/b/b1\n"
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

def test_simple_diff_common_files():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure(["1.txt", "2.txt"], ["2.txt", "3.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == "+f simpletest/1/a/1.txt\n-f simpletest/2/a/3.txt\n"
    assert errs == ""
    shutil.rmtree("simpletest")

def test_simple_diff_common_dirs():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure(["1.txt", "2.txt", "c/1c.txt"], ["2.txt", "3.txt", "c/1c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == "+f simpletest/1/a/1.txt\n-f simpletest/2/a/3.txt\n"
    assert errs == ""
    shutil.rmtree("simpletest")

def test_simple_diff_divergent_dirs():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure(["1.txt", "2.txt", "c/1c.txt"], ["2.txt", "3.txt", "c/2c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == "+f simpletest/1/a/1.txt\n+f simpletest/1/a/c/1c.txt\n-f simpletest/2/a/c/2c.txt\n-f simpletest/2/a/3.txt\n"
    assert errs == ""
    shutil.rmtree("simpletest")

def test_empty_src():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure([], ["2.txt", "3.txt", "c/2c.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == "-f simpletest/2/a/2.txt\n-d simpletest/2/a/c\n-f simpletest/2/a/3.txt\n"
    assert errs == ""
    shutil.rmtree("simpletest")

def test_empty_dest():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure(["2.txt", "3.txt", "c/2c.txt"], [])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == "+f simpletest/1/a/2.txt\n+d simpletest/1/a/c\n+f simpletest/1/a/c/2c.txt\n+f simpletest/1/a/3.txt\n"
    assert errs == ""
    shutil.rmtree("simpletest")

def test_hidden_files():
    try:
        shutil.rmtree("simpletest")
    except FileNotFoundError:
        pass

    _create_structure(["1.txt", "2.txt", "c/1c.txt", "d/.1d.txt"], ["2.txt", "3.txt", "c/2c.txt", "e/1e.txt"])
    outs, errs = _exec("simpletest/1/a", "simpletest/2/a")

    assert outs == "+f simpletest/1/a/1.txt\n+f simpletest/1/a/c/1c.txt\n-f simpletest/2/a/c/2c.txt\n+d simpletest/1/a/d\n+f simpletest/1/a/d/.1d.txt\n-d simpletest/2/a/e\n-f simpletest/2/a/3.txt\n"
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
    assert outs == "+f simpletest/1/a/file1\n-f simpletest/2/b/file1\n"
    assert errs == ""
    shutil.rmtree("simpletest")