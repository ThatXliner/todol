#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C,R0201,R0903
import hypothesis.strategies as st
import pytest
from hypothesis import assume, given

from todol import _interface as interface



class TestInterface:
    @given(
        arg1=st.booleans(), arg2=st.booleans(), bad1=st.booleans(), bad2=st.booleans()
    )
    def test_mutally_exclusive(self, arg1, arg2, bad1, bad2):
        assume(arg1 ^ arg2)
        assume(bad1 and bad2)
        with pytest.raises(ValueError):
            interface.Interface(bad1, bad2)
        interface.Interface(arg1, arg2)

    @given(random_error_msg=st.text())
    def test_error_raises(self, random_error_msg):
        with pytest.raises(Exception):
            interface.error(random_error_msg)

