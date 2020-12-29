#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

project_dir = Path(__file__).parent.parent
CUR_PY = str(sys.executable)

todol_test_dir = project_dir.joinpath("todol_test_dir")
shutil.rmtree(str(todol_test_dir), ignore_errors=True)

todol_fake_rc_file = project_dir.joinpath("todol_test_rc_file")
if todol_fake_rc_file.exists():
    os.remove(todol_fake_rc_file)

MODIFIED_ENV = deepcopy(os.environ).update(
    {
        "TODOL_CONFIG_DIR": str(todol_test_dir),
        "RC_FILE": str(todol_fake_rc_file),
    }
)

main_path = project_dir.joinpath("todol").joinpath("__main__.py")


def _run_cmd(cmd, input_=None):
    return subprocess.run(
        cmd,
        cwd=str(main_path.parent.parent),
        check=True,
        input=input_,
        env=MODIFIED_ENV,
    )


def test_meta():
    assert main_path.exists() and main_path.is_file()


def test_version():
    assert _run_cmd([CUR_PY, "-m", "todol", "--version"]).returncode == 0


def test_help():
    for command in [None, "list", "init", "add", "remove", "finish", "complete"]:
        for color_option in [None, "--force-color", "--no-color"]:  # Test color options
            args = [CUR_PY, "-m", "todol"]
            if command:
                args.append(command)
            args.append("--help")
            if color_option:
                args.append(color_option)
            assert _run_cmd(args).returncode == 0


class TestInit:  # TODO: Write tests for subcommands
    def test_no_shell(self):
        assert _run_cmd([CUR_PY, "-m", "todol", "init", "--no-shell"]).returncode == 0

    def test_add_shell(self):  # TODO(ThatXliner): Add an --only-shell option
        assert _run_cmd([CUR_PY, "-m", "todol", "init"], input_=b"y\n").returncode == 0
