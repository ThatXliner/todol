#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C
# type: ignore
"""A pyinvoke script (replacing GNU Make)"""

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
    if caches:
        _ = list(here.rglob("__pycache__"))
        if here.joinpath(".pytest_cache").exists():
            _.append(here.joinpath(".pytest_cache"))
        to_destroy.extend(_)
    if hypo:
        if here.joinpath(".hypothesis").exists():
            to_destroy.append(here.joinpath(".hypothesis"))
    if cov:
        if here.joinpath(".coverage").exists():
            to_destroy.append(here.joinpath(".coverage"))
    for thing in to_destroy:
        if thing.is_dir():
            # print(f"Will remove dir {thing}")
            shutil.rmtree(str(thing))
        else:
            os.remove(thing)
            # print(f"Will remove file {thing}")
