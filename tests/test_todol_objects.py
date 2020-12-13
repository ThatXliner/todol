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
    # The following 2 tests are super dumb
    # They may deem useful as basic sanity checks, though
    @given(todo=st.text(), due_date=st.dates())
    def test_name(self, todo, due_date):
        assert todo == todo_objects.Todo({"todo": todo, "due_date": str(due_date)}).name

    @given(todo=st.text(), due_date=st.dates())
    def test_due_date(self, todo, due_date):
        assert (
            due_date
            == todo_objects.Todo({"todo": todo, "due_date": str(due_date)}).due_date
        )

    @given(
        todo=st.text(),
        due_date=st.dates(),
        another_due_date=st.dates(),
        invalid_date=st.text(),
    )
    def test_properties(self, todo, due_date, another_due_date, invalid_date):
        # pylint: disable=W0212
        assume(not match(r"\d{4}-\d{2}-\d{2}", invalid_date))
        assume(str(due_date) != str(another_due_date))
        test_subject = todo_objects.Todo({"todo": todo, "due_date": str(due_date)})
        assert test_subject.id == test_subject._id
        assert test_subject._internal_data == test_subject.data
        assert test_subject.data == _utils.deserialize(test_subject)

        with pytest.raises(AttributeError, match="can't set attribute"):
            test_subject.data = {}
            test_subject.id = "weigfejkwgewgui"

        with pytest.raises(ValueError):
            test_subject.due_date = invalid_date

        test_subject.due_date = str(another_due_date)
        assert str(test_subject.due_date) == str(another_due_date)