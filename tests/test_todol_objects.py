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
    @given(todo=st.text(), due_date=st.dates())
    def test_name(self, todo, due_date):
        assert todo == todo_objects.Todo({"todo": todo, "due_date": str(due_date)}).name

    @given(todo=st.text(), due_date=st.dates())
    def test_due_date(self, todo, due_date):
        assert (
            due_date
            == todo_objects.Todo({"todo": todo, "due_date": str(due_date)}).due_date
        )

