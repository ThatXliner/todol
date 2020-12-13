#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
import subprocess
import sys
from pathlib import Path

main_path = Path(__file__).parent.parent.joinpath("todol").joinpath("__main__.py")
run_todol = [sys.executable, "-m", "todol"]


def _run_cmd(cmd, input_=None):
    return subprocess.run(
        cmd, cwd=str(main_path.parent.parent), check=True, input=input_
    )


def test_meta():
    assert main_path.exists() and main_path.is_file()


def test_version():
    assert _run_cmd([sys.executable, "-m", "todol", "--version"]).returncode == 0


class TestHelp:
    def test_main(self):
        assert _run_cmd([sys.executable, "-m", "todol", "--help"]).returncode == 0

    def test_list(self):
        assert (
            _run_cmd([sys.executable, "-m", "todol", "list", "--help"]).returncode == 0
        )

    def test_add(self):
        assert (
            _run_cmd([sys.executable, "-m", "todol", "add", "--help"]).returncode == 0
        )

    def test_remove(self):
        assert (
            _run_cmd([sys.executable, "-m", "todol", "remove", "--help"]).returncode
            == 0
        )

    def test_init(self):
        assert (
            _run_cmd([sys.executable, "-m", "todol", "init", "--help"]).returncode == 0
        )

    def test_finish(self):
        assert (
            _run_cmd([sys.executable, "-m", "todol", "finish", "--help"]).returncode
            == 0
        )


# class TestInit:  # TODO: Write tests for subcommands
#     ...
