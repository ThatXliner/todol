#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
from re import match

import hypothesis.strategies as st
import pytest
from hypothesis import assume, given
from todol import _utils, todo_objects


class TestConsistentSerializeDeserialize:
    @given(todo=st.text(), due_date=st.dates())
    def test_todo(self, todo, due_date):
        assert {"todo": todo, "due_date": str(due_date)} == _utils.deserialize(
            todo_objects.Todo({"todo": todo, "due_date": str(due_date)})
        )

    @given(
        list_of_stuff=st.lists(
            st.fixed_dictionaries({"todo": st.text(), "due_date": st.dates()})
        )
    )
    def test_container(self, list_of_stuff):
        assert list_of_stuff == _utils.deserialize(
            todo_objects.TodoContainer(list_of_stuff)
        )


class TestTodo:
    # The following test is super dumb
    @given(todo=st.text(), due_date=st.dates())
    def test_name(self, todo, due_date):
        assert todo == todo_objects.Todo({"todo": todo, "due_date": str(due_date)}).name
        assert (
            due_date
            == todo_objects.Todo({"todo": todo, "due_date": str(due_date)}).due_date
        )

    @given(
        todo=st.text(),
        another_todo=st.text(),
        due_date=st.dates(),
        another_due_date=st.dates(),
        invalid_date=st.text(),
    )
    def test_properties(
        self, todo, another_todo, due_date, another_due_date, invalid_date
    ):
        # pylint: disable=W0212
        assume(not match(r"\d{4}-\d{2}-\d{2}", invalid_date))
        assume(due_date != another_due_date)
        test_subject = todo_objects.Todo({"todo": todo, "due_date": str(due_date)})
        assert test_subject.name == todo
        assert test_subject.id == test_subject._id
        assert test_subject._internal_data == test_subject.data
        assert test_subject.data == _utils.deserialize(test_subject)
        assert (
            str(test_subject) == f"{test_subject.name}, due at {test_subject.due_date}"
        )

        with pytest.raises(AttributeError, match="can't set attribute"):
            test_subject.data = {}
            test_subject.id = "weigfejkwgewgui"

        with pytest.raises(ValueError):
            test_subject.due_date = invalid_date

        with pytest.raises(TypeError):
            test_subject.due_date = ...  # Not a string # NOTE: Can we just do this?

        test_subject.due_date = str(another_due_date)
        assert test_subject.due_date == another_due_date
        test_subject.due_date = another_due_date
        assert test_subject.due_date == another_due_date
        test_subject.name = another_todo
        assert test_subject.name == another_todo


class TestTodoContainer:
    @given(
        list_of_stuff=st.lists(
            st.fixed_dictionaries({"todo": st.text(), "due_date": st.dates()})
        ),
        thing_to_get=st.fixed_dictionaries({"todo": st.text(), "due_date": st.dates()}),
    )
    def test_get_todo(self, list_of_stuff, thing_to_get):
        test_subject = todo_objects.TodoContainer(list_of_stuff)
        assert (
            test_subject.get(thing_to_get)
            == test_subject.get(thing_to_get["todo"])
            == test_subject.get(todo_objects.Todo(thing_to_get))
        )
