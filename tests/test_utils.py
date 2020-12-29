#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
import re

import hypothesis.strategies as st
import pytest
from hypothesis import assume, example, given
from todol import _utils


class TestIsoParsing:
    @given(test_date=st.dates())
    def test_str_convert(self, test_date):
        assert _utils.iso_str_to_datetime(str(test_date)) == test_date

    @given(
        random_data=st.tuples(
            st.integers(max_value=9999),
            st.integers(max_value=99),
            st.integers(max_value=99),
        )
    )
    @example(random_data=(0, 0, 0))
    def test_raw_str_convert(self, random_data):
        assume(all((not x < 0 for x in random_data)))
        assert (
            _utils.parse_isoformat_date(
                f"{random_data[0]:04}-{random_data[1]:02}-{random_data[2]:02}"
            )
            == random_data
        )

    @given(invalid_string=st.text())
    def test_raises(self, invalid_string):
        assume(not re.match(r"\d{4}-\d{4}-\d{4}", invalid_string))
        with pytest.raises(ValueError):
            _utils.parse_isoformat_date(invalid_string)


def test_deserialize_raises(self):
    with pytest.raises(TypeError):
        _utils.deserialize(object)


@given(text=st.text())
def test_str_simularize(self, text):
    assert text.lower().strip() == _utils.sim_str(text)
