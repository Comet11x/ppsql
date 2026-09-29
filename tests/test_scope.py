# SPDX-FileCopyrightText: 2026-present Comet11x <comet11x@protonmail.com>
#
# SPDX-License-Identifier: MIT

import pytest

from ppsql import VariableScope


def test_set_and_get():
    scope = VariableScope("test")
    scope.set("key", "value")
    assert scope.get("key") == "value"


def test_unset_sets_none():
    scope = VariableScope("test")
    scope.set("key", "value")
    scope.unset("key")
    assert scope.get("key") is None


def test_get_falls_back_to_default():
    scope = VariableScope("test")
    assert scope.get("missing", "fallback") == "fallback"


def test_extend():
    parent = VariableScope("parent", a="1")
    child = VariableScope("child")
    assert child.extend(parent) is child
    assert child.get("a") == "1"


def test_global_scope_is_shared():
    VariableScope.global_set("global_key", "global_value")
    scope = VariableScope("test")
    assert scope.get("global_key") == "global_value"
    assert VariableScope.global_get("global_key") == "global_value"


def test_global_unset():
    VariableScope.global_set("global_key", "global_value")
    VariableScope.global_unset("global_key")
    assert VariableScope.global_get("global_key") is None


def test_local_scope_shadows_global_scope():
    VariableScope.global_set("key", "global")
    scope = VariableScope("test")
    scope.set("key", "local")
    assert scope.get("key") == "local"
    assert VariableScope.global_get("key") == "global"


def test_set_keeps_a_dollar_prefixed_value_as_is():
    scope = VariableScope("test")
    scope.set("source", "value")
    scope.set("target", "$source")
    assert scope.get("target") == "$source"


def test_scopes_are_isolated():
    first = VariableScope("first", key="1")
    second = VariableScope("second")
    assert second.get("key") is None
    assert first.get("key") == "1"


def test_scope_is_a_dict():
    scope = VariableScope("test", key="value")
    assert isinstance(scope, dict)
    assert dict(scope) == {"key": "value"}


@pytest.mark.parametrize("key", ["a", "b_1", "_c"])
def test_any_key_can_be_used(key):
    scope = VariableScope("test")
    scope.set(key, "value")
    assert scope.get(key) == "value"
