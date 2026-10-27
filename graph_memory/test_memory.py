import pytest

from db import get_connection
from memory import (
    get_preferred,
    get_rejected,
    preferences_as_text,
    remember_preference,
)

USER = "sai"


@pytest.fixture
def conn(tmp_path):
    # A fresh throwaway DB per test, so the real data/graph.kuzu is never touched.
    return get_connection(tmp_path / "test.kuzu")


def test_saves_preferred_and_rejected(conn):
    remember_preference(conn, USER, "express", "fastify")

    assert get_preferred(conn, USER) == ["express"]
    assert get_rejected(conn, USER) == ["fastify"]


def test_repeating_a_fact_adds_no_duplicates(conn):
    remember_preference(conn, USER, "express", "fastify")
    remember_preference(conn, USER, "express", "fastify")

    assert get_preferred(conn, USER) == ["express"]
    assert get_rejected(conn, USER) == ["fastify"]


def test_flipping_a_preference_removes_the_old_arrows(conn):
    remember_preference(conn, USER, "express", "fastify")
    remember_preference(conn, USER, "fastify", "express")

    assert get_preferred(conn, USER) == ["fastify"]
    assert get_rejected(conn, USER) == ["express"]


def test_unrelated_preferences_survive_a_flip(conn):
    remember_preference(conn, USER, "react", "vue")
    remember_preference(conn, USER, "express", "fastify")
    remember_preference(conn, USER, "fastify", "express")

    assert "react" in get_preferred(conn, USER)
    assert "vue" in get_rejected(conn, USER)


def test_newest_preference_comes_first(conn):
    remember_preference(conn, USER, "express", "koa")
    remember_preference(conn, USER, "react", "vue")

    assert get_preferred(conn, USER) == ["react", "express"]


def test_unknown_user_has_no_preferences(conn):
    assert get_preferred(conn, "nobody") == []
    assert get_rejected(conn, "nobody") == []


def test_text_summary(conn):
    remember_preference(conn, USER, "express", "fastify")

    assert preferences_as_text(conn, USER) == (
        "sai prefers: express. sai rejects: fastify."
    )


def test_text_summary_when_empty(conn):
    assert preferences_as_text(conn, "nobody") == "No stored preferences for nobody."
