#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C
# type: ignore
"""A pyinvoke script (replacing GNU Make)"""

import glob
import os
import shutil
from pathlib import Path

from invoke import task

here = Path(__file__).parent


@task
def test(command, coverage=True, verbosity=3, color=True):
    to_run = "poetry run pytest tests/ "
    if coverage:
        to_run += "--cov=todol --cov-report xml "
    if color:
        to_run += "--color=yes "
    if verbosity:
        if 0 < verbosity >= 3:
            to_run += "-" + ("v" * verbosity) + " "
        else:
            raise ValueError("Verbosity must be at most 3")
    command.run(to_run)


@task
def clean(_, caches=True, hypo=True, cov=True):
    to_destroy = []
    to_destroy.extend([Path(globbed) for globbed in glob.iglob("todol_test_*")])
    if caches:
        _ = list(here.rglob("__pycache__"))
        if here.joinpath(".pytest_cache").exists():
            _.append(here.joinpath(".pytest_cache"))
        to_destroy.extend(_)
    if hypo:
        if here.joinpath(".hypothesis").exists():
            to_destroy.append(here.joinpath(".hypothesis"))
    if cov:
        to_destroy.extend([Path(globbed) for globbed in glob.iglob(".coverage*")])
        to_destroy.extend([Path(globbed) for globbed in glob.iglob("coverage*")])
    for thing in to_destroy:
        if thing.is_dir():
            shutil.rmtree(str(thing))
        else:
            os.remove(thing)
