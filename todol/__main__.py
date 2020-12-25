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
import sys
from pathlib import Path
from typing import Dict, List

from . import __version__
from . import _interface as intf
from . import _utils, todo_objects
from ._opts import color_options

parser = argparse.ArgumentParser(
    description="A todo list CLI tool",
    prog="todol",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    parents=[color_options],
)
parser.add_argument(
    "--version", action="version", version="%(prog)s {}".format(__version__)
)

subparsers = parser.add_subparsers(dest="command")

list_parser = subparsers.add_parser(
    "list", help="List todos", aliases=("l"), parents=[color_options]
)
list_parser.add_argument(
    "type",
    choices=("todo", "finished", "fin"),
    nargs="?",
    default="todo",
    help="The type of todo to list",
)
init_parser = subparsers.add_parser(
    "init", help="Initialize todol", parents=[color_options]
)
init_parser.add_argument(
    "--no-shell",
    action="store_true",
    help="Don't inject a todo-listing command to your shell's rc file",
    dest="no_shell",
)

add_parser = subparsers.add_parser(
    "add", help="Add a todo", aliases=("a"), parents=[color_options]
)
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
    "remove",
    help="Remove todo(s) without finishing them",
    aliases=("r", "remove"),
    parents=[color_options],
)
remove_parser.add_argument(
    "todo",
    help="The todo to remove. Will be fuzzy matched or matched by ID/date/etc",
)

finish_parser = subparsers.add_parser(
    "finish", help="Finish todo(s)", aliases=("f", "do"), parents=[color_options]
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

completion_parser = subparsers.add_parser(
    "complete",
    help="Generate shell completion. The pycomplete library must be installed, though.",
    aliases=("c", "completion"),
)
completion_parser.add_argument(
    "shell",
    nargs="?",
    choices=("zsh", "bash", "fish", "powershell"),
    default=_utils.users_shell,
)
parser.set_defaults(no_shell=False)  # See line 232
args = parser.parse_args()


def main() -> None:  # TODO: REFACTOR this to an object
    """The main entry point function."""

    todol_dir = Path("~/.config/todol").expanduser()
    todo_index = todol_dir.joinpath("todos.json")
    interface = intf.Color(no_color=args.no_color, force_color=args.force_color)  # type: ignore

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
        print("-" * int(interface.COLUMNS / 3))
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
        print("-" * int(interface.COLUMNS / 3))
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

    def command_remove() -> int:
        todos = _get_todo_data()
        assert isinstance(args.todo, str)  # type: ignore

        interface.info(f"Removing todo {args.todo!r}...")
        todo_obj = todo_objects.TodoContainer(todos["todos"])

        try:
            todo_obj.pop_thing({"todo": args.todo, "due_date": args.due_date})  # type: ignore
        except IndexError:
            interface.error("Could not find todo!")
            return 1
        else:
            todos["todos"] = _utils.deserialize(todo_obj)  # type: ignore
            # Actually add it to the index
            todo_index.write_text(json.dumps(todos))
            interface.success("Done!")
            return 0

    def command_finish() -> int:
        todos = _get_todo_data()
        assert isinstance(args.todo, str)  # type: ignore

        interface.info(f"Finishing todo {args.todo!r}...")

        todo_obj = todo_objects.TodoContainer(todos["todos"])
        finished_obj = todo_objects.TodoContainer(todos["finished"])
        try:
            finished_obj.add_todo(
                todo_obj.pop_thing({"todo": args.todo, "due_date": args.due_date})  # type: ignore
            )
        except IndexError:
            interface.error("Could not find todo!")
            return 1
        else:
            todos["finished"] = _utils.deserialize(finished_obj)  # type: ignore
            todos["todos"] = _utils.deserialize(todo_obj)  # type: ignore

            # Actually add it to the index
            todo_index.write_text(json.dumps(todos))
            interface.success("Done!")
            return 0

    def command_init() -> int:
        """Initialize todol for the current user."""

        if not (todol_dir.is_dir() and todol_dir.exists()):
            interface.info(f"Creating todol directory at {todol_dir}...")
            todol_dir.mkdir(parents=True)  # Also make ~/.config if it doesn't exist
            interface.success()

        if not (todo_index.is_file() and todo_index.exists()):
            interface.info("Creating todol index...")
            todo_index.touch()  # Create todol.json
            interface.success()

        if not todo_index.read_text():  # Empty
            todo_index.write_text(R'{"todos":[], "finished":[]}')

        todos: Dict[str, List[str]] = json.loads(todo_index.read_text())
        if not todos:  # Empty
            todos["todos"] = []
            todos["finished"] = []
            todos["long_term"] = []

        if not args.no_shell:  # type: ignore  # default to False
            _utils.initialize_shell(__version__)
        interface.success("\N{SPARKLES} Initialized todol!")
        return 0

    def command_complete() -> int:
        try:
            import pycomplete  # type:ignore # pylint: disable=C0415
        except ModuleNotFoundError:
            interface.error(
                "Pycomplete not installed! "
                "Please install the extra via `pip install todol[complete]`"
            )
            return 1
        else:
            completer = pycomplete.Completer(parser)  # type: ignore
            print(completer.render(args.shell))  # type: ignore
            return 0

    subcommands_map = {
        "list": command_list,
        "l": command_list,
        "add": command_add,
        "a": command_add,
        "remove": command_remove,
        "r": command_remove,
        "finish": command_finish,
        "f": command_finish,
        "do": command_finish,
        "init": command_init,
        "complete": command_complete,
        "c": command_complete,
    }
    sys.exit(subcommands_map.get(args.command, parser.print_help)() or 0)  # type: ignore


if __name__ == "__main__":
    main()
