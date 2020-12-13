#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
import hypothesis.strategies as st
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


class TestMisc:
    @given(text=st.text())
    def test_str_simularize(self, text):
        assert text.lower().strip() == _utils.sim_str(text)

    @given(text=st.text())
    def test_str_convert(self, text):
        assume(text != _utils.sim_str(text))
        assert _utils.sim_str(text) != text
