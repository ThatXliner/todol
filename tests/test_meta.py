#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
from pathlib import Path

import toml
from todol import __version__


def test_version():
    assert (
        __version__
        == toml.loads(
            Path(__file__).parent.parent.joinpath("pyproject.toml").read_text()
        )["tool"]["poetry"]["version"]
    )
