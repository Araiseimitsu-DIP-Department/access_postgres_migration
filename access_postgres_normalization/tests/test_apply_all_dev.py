"""一括適用スクリプトの手順の組み立て・中止・接続先の制限を確認する。"""

from types import SimpleNamespace

import pytest

from access_postgres_normalization import apply_all_dev
from access_postgres_normalization.apply_all_dev import SQL_STEPS, build_commands, run_commands
from access_postgres_normalization.dev_db import DevConnectionError

SETTINGS = {"host": "192.168.1.120", "user": "postgres", "password": "secret-pw"}


def test_up_runs_repair_then_all_sql_in_order():
    commands = build_commands(SETTINGS, down=False, psql="psql", python="python")
    assert commands[0].args[-1] == "--apply"
    labels = [c.label for c in commands[1:]]
    assert labels == [f"{s.name}_up.sql" for s in SQL_STEPS]


def test_all_sql_files_exist():
    for step in SQL_STEPS:
        assert step.path("up").exists()
        assert step.path("down").exists()


def test_down_runs_sql_in_reverse_without_repair_or_password():
    commands = build_commands(SETTINGS, down=True, psql="psql")
    assert [c.label for c in commands] == [f"{s.name}_down.sql" for s in reversed(SQL_STEPS)]
    assert all(not any("devpw=" in a for a in c.args) for c in commands)


def test_password_is_passed_only_where_needed_and_masked_in_display():
    commands = {c.label: c for c in build_commands(SETTINGS, down=False, psql="psql")}
    with_pw = commands["product_master/04_subcon_manager_up.sql"]
    assert "devpw=secret-pw" in with_pw.args
    assert "secret-pw" not in with_pw.display()
    assert not any("devpw=" in a for a in commands["materials/02_inspection_checks_up.sql"].args)


def test_missing_password_is_rejected():
    with pytest.raises(DevConnectionError):
        build_commands({"host": "192.168.1.120", "user": "postgres"}, down=False)


def test_run_stops_at_first_failure():
    commands = build_commands(SETTINGS, down=True, psql="psql")
    calls = []

    def runner(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=3 if len(calls) == 2 else 0)

    assert run_commands(commands, {}, runner) == 3
    assert len(calls) == 2


def test_main_refuses_non_dev_host_without_running(monkeypatch):
    monkeypatch.setenv("NORMALIZATION_DEV_HOST", "192.168.1.121")
    monkeypatch.setenv("NORMALIZATION_DEV_USER", "postgres")
    monkeypatch.setenv("NORMALIZATION_DEV_PASSWORD", "x")

    def runner(*args, **kwargs):
        raise AssertionError("実行してはいけない")

    assert apply_all_dev.main(["--execute"], runner=runner) == 1


def test_main_without_execute_does_not_run(monkeypatch):
    monkeypatch.setenv("NORMALIZATION_DEV_HOST", "192.168.1.120")
    monkeypatch.setenv("NORMALIZATION_DEV_USER", "postgres")
    monkeypatch.setenv("NORMALIZATION_DEV_PASSWORD", "x")

    def runner(*args, **kwargs):
        raise AssertionError("実行してはいけない")

    assert apply_all_dev.main([], runner=runner) == 0
