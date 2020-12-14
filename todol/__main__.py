#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initial author: Bryan Hu.

@ThatXliner.

Version: v0.1.0

The main cli entry point

"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List

from . import __version__
from . import _interface as interface
from . import _utils, todo_objects

parser = argparse.ArgumentParser(
    description="A todo list CLI tool",
    prog="todol",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--version", action="version", version="%(prog)s {}".format(__version__)
)

subparsers = parser.add_subparsers(dest="command")

list_parser = subparsers.add_parser("list", help="List todos", aliases=("l"))
list_parser.add_argument(
    "type",
    choices=("todo", "finished", "fin"),
    nargs="?",
    default="todo",
    help="The type of todo to list",
)
init_parser = subparsers.add_parser("init", help="Initialize todol")

add_parser = subparsers.add_parser("add", help="Add a todo", aliases=("a"))
add_parser.add_argument("todo", help="The todo to add.", type=_utils.sim_str)

due_dates = add_parser.add_mutually_exclusive_group()
due_dates.add_argument(  # TODO: Add time capability
    "--due",
    "--due-date",
    "-d",
    default=str(_utils.tomorrow),
    type=str,
    help="The due date in ISO 8601 format, YYYY-MM-DD (padded with zeros, if required)",
    dest="due_date",
)
due_dates.add_argument(
    "--long-term",
    "--long",
    "-l",
    action="store_true",
    help="Make the todo a long term goal",
    dest="long_term",
)

remove_parser = subparsers.add_parser(
    "remove", help="Remove todo(s) without finishing them", aliases=("r", "remove")
)
remove_parser.add_argument(
    "todo",
    help="The todo to remove. Will be fuzzy matched or matched by ID/date/etc",
)

finish_parser = subparsers.add_parser(
    "finish", help="Finish todo(s)", aliases=("f", "done")
)
finish_parser.add_argument(
    "todo",
    help="The todo to finish. Will be fuzzy matched or matched by ID/date/etc",
)
due_dates = finish_parser.add_mutually_exclusive_group()
due_dates.add_argument(  # TODO: Add time capability
    "--due",
    "--due-date",
    "-d",
    default=str(_utils.tomorrow),
    type=str,
    help="The due date in ISO 8601 format, YYYY-MM-DD (padded with zeros, if required)",
    dest="due_date",
)
due_dates.add_argument(
    "--long-term",
    "--long",
    "-l",
    action="store_true",
    help="Make the todo a long term goal",
    dest="long_term",
)

args = parser.parse_args()


def main() -> None:
    """The main entry point function."""

    todol_dir = Path("~/.config/todol").expanduser()
    todo_index = todol_dir.joinpath("todos.json")

    def _get_todo_data() -> Dict[str, List[Dict[str, str]]]:
        try:
            todos: Dict[str, List[Dict[str, str]]] = json.loads(todo_index.read_text())
        except OSError:  # It doesn't exist
            interface.error("Todol is not initialized!")
            command_init()
            todos = json.loads(todo_index.read_text())
        assert isinstance(todos, dict)
        return todos

    def command_list() -> int:
        todos = _get_todo_data()
        if args.type == "todo":  # type: ignore
            if not todos["todos"]:
                print("\N{PARTY POPPER} No todos!")
            for item in todo_objects.TodoContainer(todos["todos"]):
                print(
                    f" - {interface.BLUE}{item.name!r}{interface.RESET}, "
                    f"{interface.RED}due at {interface.YELLOW}{item.due_date}{interface.RESET}"
                )
        elif args.type == "finished":  # type: ignore
            for item in todo_objects.TodoContainer(todos["finished"]):
                print(f" - {interface.BLUE}{item.name!r}{interface.RESET}")
        return 0

    def command_add() -> int:
        todos = _get_todo_data()
        assert isinstance(args.todo, str)  # type: ignore

        interface.info(f"Adding todo {args.todo!r} to the list of todos...")
        todo_obj = todo_objects.TodoContainer(todos["todos"])
        todo_obj.add_todo({"todo": args.todo, "due_date": args.due_date})  # type: ignore
        todos["todos"] = _utils.deserialize(todo_obj)  # type: ignore

        # Actually add it to the the list of todos
        todo_index.write_text(json.dumps(todos))
        interface.success("Done!")
        return 0

        interface.error("Not implemented yet")
        return 1

    def command_finish() -> int:
        todos = _get_todo_data()
        assert isinstance(args.todo, str)  # type: ignore

        interface.info(f"Finishing todo {args.todo!r}...")

        todo_obj = todo_objects.TodoContainer(todos["todos"])
        finished_obj = todo_objects.TodoContainer(todos["finished"])

        finished_obj.add_todo(
            todo_obj.pop_thing({"todo": args.todo, "due_date": args.due_date})  # type: ignore
        )

        todos["finished"] = _utils.deserialize(finished_obj)  # type: ignore
        todos["todos"] = _utils.deserialize(todo_obj)  # type: ignore

        # Actually add it to the index
        todo_index.write_text(json.dumps(todos))
        interface.success("Done!")
        return 0

    def command_init() -> int:
        """Initialize todol for the current user."""

        def _initialize_shell() -> None:
            to_inject = (
                f"# >>> Section managed/injected by Todol {__version__}>>>\n"
                + f"{sys.executable} -m {Path(__file__).parent} list\n"
                + "# <<<<<<\n"
            )
            # Get the shell (and default to bash)
            shell = Path(
                os.environ.get("SHELL", (shutil.which("bash") or "/bin/bash"))
            ).name

            # Calculate the rc file
            rc_file_path = Path(f"~/.{shell}rc").expanduser()
            if not (rc_file_path.exists() and rc_file_path.is_file()):
                rc_file_path.touch()

            # Get rc file contents
            to_append = rc_file_path.read_text()

            print(
                "Would you also like to "
                f"{interface.BOLD}see your todos{interface.RESET} "
                "at the start of every shell session?"
            )

            # Shell injection logic
            if not to_append.startswith(to_inject) and _utils.yes_or_no():

                # Append the following to the rc file:
                # # >>> Section managed/injected by Todol [PROGRAM VERSION] >>>
                # [PYTHON EXECUTABLE] [THIS FILE] list
                # # <<<<<<
                interface.info(f"Injecting to {rc_file_path}...")

                assert not to_append.startswith(to_inject)

                # Inject!
                rc_file_path.write_text(to_inject + to_append)

                interface.success()

                # Why at the top of the file?
                # To make sure that the command is properly executed
                # so things like Powerlevel10k's "instant prompt"
                # won't get bothered.
                # We also use sys.executable and __file__
                # to throw all that $PATH mess out the window
            else:
                interface.success("Cancelled!")

        def _initialize_directory() -> None:
            if not (todol_dir.is_dir() and todol_dir.exists()):
                interface.info(f"Creating todol directory at {todol_dir}...")
                todol_dir.mkdir(parents=True)  # Also make ~/.config if it doesn't exist
                interface.success()

        def _initialize_index() -> None:
            if not (todo_index.is_file() and todo_index.exists()):
                interface.info("Creating todol index...")
                todo_index.touch()  # Create todol.json
                interface.success()
            if not todo_index.read_text():
                todo_index.write_text(R'{"todos":[], "finished":[]}')
            todos: Dict[str, List[str]] = json.loads(todo_index.read_text())
            if not todos:  # Empty
                todos["todos"] = []
                todos["finished"] = []
                todos["long_term"] = []

        _initialize_directory()
        _initialize_index()
        _initialize_shell()

        interface.success("\N{SPARKLES} Initialized todol!")
        return 0

    subcommands_map = {
        "list": command_list,
        "add": command_add,
        "remove": command_remove,
        "finish": command_finish,
        "init": command_init,
    }
    sys.exit(subcommands_map.get(args.command, parser.print_help)() or 0)  # type: ignore


if __name__ == "__main__":
    main()
