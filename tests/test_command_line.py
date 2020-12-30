#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import hypothesis.strategies as st
from hypothesis import assume, given, settings
from todol._utils import sim_str

project_dir = Path(__file__).parent.parent
#######
main_path = project_dir.joinpath("todol").joinpath("__main__.py")

todol_test_dir = project_dir.joinpath("todol_test_dir")
todol_test_rc = project_dir.joinpath("todol_test_rc")


def _clean():
    if todol_test_rc.exists() and todol_test_rc.is_file():
        os.remove(todol_test_rc)
    if todol_test_dir.exists() and todol_test_dir.is_dir():
        shutil.rmtree(str(todol_test_dir))


#########
MODIFIED_ENV = copy.deepcopy(os.environ).update(
    {"RC_FILE": str(todol_test_rc), "TODOL_CONFIG_DIR": str(todol_test_dir)}
)
PYTHON = sys.executable


def _run_cmd(cmd, input_=None, check=True):
    return subprocess.run(
        cmd, cwd=str(project_dir), check=check, input=input_, env=MODIFIED_ENV
    )


def test_meta():
    assert main_path.exists() and main_path.is_file()


def test_version():
    assert _run_cmd((PYTHON, "-m", "todol", "--version")).returncode == 0


def test_help():
    for command in (None, "list", "add", "remove", "init", "finish", "complete"):
        args = [PYTHON, "-m", "todol"]
        if command:
            args.append(command)
        for color_option in (None, "--force-color", "--no-color"):
            if color_option:
                args.append(color_option)
            args.append("--help")
            assert _run_cmd(args).returncode == 0


class TestInit:  # TODO: Write tests for subcommands
    def test_no_shell(self):
        _clean()
        assert _run_cmd((PYTHON, "-m", "todol", "init", "--no-shell")).returncode == 0
        assert (
            todol_test_dir.joinpath("todos.json").exists()
            and todol_test_dir.joinpath("todos.json").is_file()
        )

    def test_init(self):
        _clean()
        assert _run_cmd((PYTHON, "-m", "todol", "init"), input_=b"y\n").returncode == 0
        assert (
            todol_test_dir.joinpath("todos.json").exists()
            and todol_test_dir.joinpath("todos.json").is_file()
        )
        assert todol_test_rc.read_text()

    def test_init_default(self):
        _clean()
        assert _run_cmd((PYTHON, "-m", "todol", "init"), input_=b"\n").returncode == 0
        assert (
            todol_test_dir.joinpath("todos.json").exists()
            and todol_test_dir.joinpath("todos.json").is_file()
        )
        assert todol_test_rc.read_text()

    def test_init_eof_cancel(self):
        _clean()
        with subprocess.Popen(
            (PYTHON, "-m", "todol", "init"),
            cwd=str(project_dir),
            env=MODIFIED_ENV,
            stdin=subprocess.PIPE,
        ) as process:
            process.stdin.close()
            assert process.wait() == 0

        assert (
            todol_test_dir.joinpath("todos.json").exists()
            and todol_test_dir.joinpath("todos.json").is_file()
        )


class TestAdd:
    @given(to_add=st.text(alphabet=st.characters(blacklist_categories=("C"))))
    @settings(deadline=None)
    def test_with_init_no_shell(self, to_add):
        assume(to_add == sim_str(to_add))
        _clean()
        assert (
            _run_cmd(
                (PYTHON, "-m", "todol", "add", repr(to_add)), input_=b"n\n"
            ).returncode
            == 0
        )
        assert (
            todol_test_dir.joinpath("todos.json").exists()
            and todol_test_dir.joinpath("todos.json").is_file()
        )
        assert json.loads(todol_test_dir.joinpath("todos.json").read_text())["todos"][
            -1
        ]["todo"] == repr(to_add)

    @given(to_add=st.text(alphabet=st.characters(blacklist_categories=("C"))))
    @settings(deadline=None)
    def test_with_init_and_shell(self, to_add):
        assume(to_add == sim_str(to_add))
        _clean()
        assert (
            _run_cmd(
                (PYTHON, "-m", "todol", "add", repr(to_add)), input_=b"y\n"
            ).returncode
            == 0
        )
        assert (
            todol_test_dir.joinpath("todos.json").exists()
            and todol_test_dir.joinpath("todos.json").is_file()
        )
        assert todol_test_rc.read_text()
        assert json.loads(todol_test_dir.joinpath("todos.json").read_text())["todos"][
            -1
        ]["todo"] == repr(to_add)


class TestFinish:
    @given(non_existing=st.text(alphabet=st.characters(blacklist_categories=("C"))))
    @settings(deadline=None)
    def test_finish_nonexisting(self, non_existing):
        assume(non_existing == sim_str(non_existing))
        _clean()
        assert (
            _run_cmd(
                (PYTHON, "-m", "todol", "finish", repr(non_existing)),
                input_=b"y\n",
                check=False,
            ).returncode
            == 1
        )
        assert (
            todol_test_dir.joinpath("todos.json").exists()
            and todol_test_dir.joinpath("todos.json").is_file()
        )
        assert todol_test_rc.read_text()
