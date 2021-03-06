"""Abstract object repsentations of a todo."""

import datetime
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, Union

from . import _utils


class Todo(_utils.Deserializable):  # TODO: Add a delay method
    """A basic class representing a single task"""

    def __init__(self, todo_data: Dict[str, str]) -> None:
        self._internal_data: Dict[str, str] = todo_data
        self._todo_name: str = todo_data["todo"]
        self._due_date = _utils.iso_str_to_datetime(str(todo_data["due_date"]))
        self._id = todo_data.get("id", "unknown")

    def __str__(self) -> str:
        return f"{self._todo_name}, due at {self._due_date}"

    def __repr__(self) -> str:
        return f"Todo(name={self._todo_name}, due_date={self._due_date})"

    def __eq__(self, other) -> bool:  # type: ignore
        if isinstance(other, Todo):  # type: ignore
            return self._internal_data == other._internal_data
        try:
            return self._internal_data == other  # type: ignore
        except TypeError as exception:
            raise NotImplementedError(
                f"Cannot compare with {other.__name__}"  # type: ignore
            ) from exception

    @property
    def name(self) -> str:
        """The todo."""
        return self._todo_name

    @name.setter
    def name(self, new_value: str) -> None:
        self._todo_name = new_value

    def __deserialize__(self) -> Dict[str, str]:
        return self._internal_data

    @property
    def data(self) -> Dict[str, str]:
        """Read-only dictionary the internal data.

        Useful for plugin capabilities
        """
        return self._internal_data

    @property
    def id(self) -> str:  # pylint: disable=invalid-name
        """The id of the todo. Unused for now."""
        return self._id

    @property
    def due_date(self) -> datetime.date:
        """The date when the todo is due"""
        return self._due_date

    @due_date.setter
    def due_date(self, new_value: Union[datetime.date, str]) -> None:
        try:
            assert isinstance(new_value, (str, datetime.date))
            self._due_date = (
                _utils.iso_str_to_datetime(new_value)
                if isinstance(new_value, str)
                else new_value
            )
        except (TypeError, AssertionError) as exception:
            raise TypeError(
                "`new_value` must be type str or datetime.date, not %s"
                % type(new_value).__name__
            ) from exception
        except ValueError as exception:
            assert isinstance(new_value, str)
            raise ValueError(
                f"Invalid isoformat string: {new_value!r}. "
                "(Remember, it must be YYYY-MM-DD padded with zeros)"
            ) from exception


class TodoContainer(_utils.Deserializable):
    """A list-like container for todos"""

    def __init__(self, todos: Iterable[Dict[str, str]]):
        self._todos: List[Todo] = [Todo(item) for item in todos]
        self._indexed_todos: Dict[Tuple[str, datetime.date], Todo] = {
            (todo.name, todo.due_date): todo for todo in self._todos
        }

    def __repr__(self) -> str:
        return f"TodoContainer({self._todos})"

    def __getitem__(
        self, todo_name_or_id: Union[Dict[str, str], Todo, str]
    ) -> Optional[Todo]:
        """An alias for :py:meth:`.get`"""
        return self.get(todo_name_or_id)

    def __iter__(self) -> Iterator[Todo]:
        return iter(self._todos)

    def __len__(self) -> int:
        return len(self._todos)

    def __deserialize__(self) -> List[Dict[str, str]]:
        return [thing.__deserialize__() for thing in self._todos]

    def index(self, thing: Todo) -> int:
        """The index method similar to :py:obj:`list`"""
        return self._todos.index(thing)

    def pop(self, index: int = -1) -> Todo:
        """The pop method similar to :py:obj:`list`"""
        return self._todos.pop(index)

    def pop_thing(self, thing: Union[Dict[str, str], Todo]) -> Todo:
        """Find and pop a todo.

        Parameters
        ----------
        thing : Union[Dict[str, str], Todo]
            A dictionary or a :py:obj:`Todo` object to find and pop.

        Returns
        -------
        Todo
            The todo popped.

        Raises
        ------
        IndexError
            The todo does not exist or could not be found.

        """
        try:
            return self._todos.pop(
                self._todos.index(
                    self.get(  # type: ignore
                        thing.name if isinstance(thing, Todo) else Todo(thing).name
                    )
                )
            )
        except (IndexError, ValueError) as exception:
            raise IndexError("That todo doesn't exist!") from exception

    def remove(self, thing: Todo) -> None:
        """The remove method similar to :py:obj:`list`"""
        self._todos.remove(thing)

    def get(
        self, todo_name_or_dict: Union[str, Todo, Dict[str, str]], fuzzy_limit: int = 5
    ) -> Optional[Todo]:
        """Search for a todo."""
        if isinstance(todo_name_or_dict, Todo):
            assert isinstance(todo_name_or_dict, Todo)
            if todo_name_or_dict in self._todos:
                return todo_name_or_dict
            todo_name: str = todo_name_or_dict.name
        elif isinstance(todo_name_or_dict, str):
            todo_name = todo_name_or_dict
        elif isinstance(todo_name_or_dict, dict):
            try:
                todo_name = todo_name_or_dict["todo"]
            except KeyError as exception:
                raise ValueError(
                    "Invalid dictionary structure for `todo_name_or_dict`"
                ) from exception

        for metadata, todo in self._indexed_todos.items():
            if (
                isinstance(todo_name_or_dict, (Todo, dict))
                and todo_name_or_dict == todo
            ):
                return todo
            # By fuzzy matching
            if _utils.fuzzy_match(metadata[0], todo_name, limit=fuzzy_limit):
                return todo

        return None

    def add_todo(self, todo: Union[Dict[str, str], Todo]) -> None:
        """Adds a todo to the list of todos. Return the todo if it exists"""
        self._todos.append(todo if isinstance(todo, Todo) else Todo(todo))
