"""本番→開発の複製スクリプトの対象判定・目次の加工・外部サーバー切替計画・中止条件を確認する。"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from access_postgres_normalization import refresh_dev_from_prod as refresh
from access_postgres_normalization.dev_db import DevConnectionError
from access_postgres_normalization.refresh_dev_from_prod import (
    PROD_HOST,
    ConnectionSettings,
    DumpedDatabase,
    RefreshError,
    Tools,
    UserMapping,
)

DEV = ConnectionSettings("192.168.1.120", "postgres", "dev-pw")
PROD = ConnectionSettings(PROD_HOST, "postgres", "prod-pw")

TOC = """;
; Archive created at 2026-11-20
2; 3079 32352 EXTENSION - postgres_fdw
2136; 1417 32360 SERVER - appearance_inspection_srv postgres
3596; 0 0 USER MAPPING - USER MAPPING postgres SERVER appearance_inspection_srv postgres
3597; 0 0 USER MAPPING - USER MAPPING "arai-db-admin" SERVER arai_masters_srv postgres
246; 1259 32366 FOREIGN TABLE fdw_appearance numeric_inspection_records postgres
"""


def test_targets_are_databases_on_both_sides_except_postgres():
    targets = refresh.select_targets(["a", "b", "postgres", "prod_only"], ["b", "a", "postgres", "dev_only"])
    assert targets == ["a", "b"]


def test_split_toc_disables_user_mappings_and_keeps_everything_else():
    toc_text, mappings = refresh.split_toc(TOC)
    assert mappings == (UserMapping("postgres", "appearance_inspection_srv"),
                        UserMapping("arai-db-admin", "arai_masters_srv"))
    active = [line for line in toc_text.splitlines() if not line.startswith(";")]
    assert not any("USER MAPPING" in line for line in active)
    assert any("FOREIGN TABLE" in line for line in active)
    assert any("SERVER - appearance_inspection_srv" in line for line in active)


def test_plan_switches_only_prod_facing_servers_and_known_roles():
    servers = [("prod_srv", [f"host={PROD_HOST}", "port=5432"]),
               ("other_srv", ["host=10.0.0.5", "dbname=x"])]
    mappings = (UserMapping("postgres", "prod_srv"), UserMapping("missing_role", "prod_srv"),
                UserMapping("public", "prod_srv"), UserMapping("postgres", "other_srv"))
    plan = refresh.plan_fdw_switch(servers, mappings, {"postgres"})
    assert plan.servers_to_switch == ("prod_srv",)
    assert plan.mappings_to_create == (UserMapping("postgres", "prod_srv"), UserMapping("public", "prod_srv"))
    assert len(plan.warnings) == 3


def test_dump_reads_prod_read_only_and_restore_writes_dev_without_secrets():
    tools = Tools()
    dumped = DumpedDatabase("order_management", Path("o.dump"), Path("o.toc"), ())
    dump_args = refresh.pg_dump_args(tools, PROD, "order_management", Path("o.dump"))
    restore_args = refresh.pg_restore_args(tools, DEV, dumped)
    assert dump_args[dump_args.index("-h") + 1] == PROD_HOST
    assert restore_args[restore_args.index("-h") + 1] == DEV.host
    assert PROD_HOST not in restore_args
    assert {"--no-owner", "--no-privileges", "--exit-on-error", "-L"} <= set(restore_args)
    assert not any("pw" in arg for arg in dump_args + restore_args)
    assert "default_transaction_read_only=on" in refresh.prod_environment(PROD)["PGOPTIONS"]


def _clear_password_variables(monkeypatch):
    monkeypatch.setenv("NORMALIZATION_DEV_USER", "postgres")
    monkeypatch.delenv("NORMALIZATION_DEV_PASSWORD", raising=False)
    monkeypatch.delenv("NORMALIZATION_PROD_PASSWORD", raising=False)
    monkeypatch.delenv("NORMALIZATION_PROD_USER", raising=False)


def test_passwords_are_prompted_when_not_given(monkeypatch):
    _clear_password_variables(monkeypatch)
    prompts = []

    def prompt(message):
        prompts.append(message)
        return "dev-pw" if "開発" in message else "prod-pw"

    dev, prod = refresh.load_settings(None, None, prompt)
    assert (dev.password, prod.password) == ("dev-pw", "prod-pw")
    assert "192.168.1.120" in prompts[0] and PROD_HOST in prompts[1]


def test_file_and_variable_take_precedence_over_prompt(monkeypatch, tmp_path):
    _clear_password_variables(monkeypatch)
    monkeypatch.setenv("NORMALIZATION_PROD_PASSWORD", "prod-pw")
    password_file = tmp_path / "dev.txt"
    password_file.write_text("dev-pw\n", encoding="utf-8")

    def prompt(message):
        raise AssertionError("入力を求めてはいけない")

    dev, prod = refresh.load_settings(str(password_file), None, prompt)
    assert (dev.password, prod.password) == ("dev-pw", "prod-pw")


@pytest.mark.parametrize("prompt_result", ["", EOFError()])
def test_empty_or_unavailable_prompt_is_rejected(monkeypatch, prompt_result):
    _clear_password_variables(monkeypatch)

    def prompt(message):
        if isinstance(prompt_result, Exception):
            raise prompt_result
        return prompt_result

    with pytest.raises(DevConnectionError):
        refresh.load_settings(None, None, prompt)


def test_dev_host_must_not_be_prod(monkeypatch):
    monkeypatch.setenv("NORMALIZATION_DEV_HOST", PROD_HOST)
    monkeypatch.setenv("NORMALIZATION_DEV_USER", "postgres")
    with pytest.raises(DevConnectionError):
        refresh.load_settings(None, None)


def test_dump_failure_stops_before_touching_dev(monkeypatch, tmp_path):
    def runner(args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="boom")

    def must_not_restore(*args, **kwargs):
        raise AssertionError("取得に失敗したら復元してはいけない")

    monkeypatch.setattr(refresh, "restore_all", must_not_restore)
    with pytest.raises(RefreshError):
        refresh.refresh(["a", "b"], DEV, PROD, Tools(), runner)


def test_dump_all_writes_filtered_toc(tmp_path):
    def runner(args, **kwargs):
        return SimpleNamespace(returncode=0, stdout=TOC if "-l" in args else "", stderr="")

    dumped = refresh.dump_all(["delivery_label_db"], tmp_path, PROD, Tools(), runner)
    assert len(dumped[0].user_mappings) == 2
    assert "\n3596;" not in dumped[0].toc_path.read_text(encoding="utf-8")


def test_main_without_execute_changes_nothing(monkeypatch):
    monkeypatch.setenv("NORMALIZATION_DEV_USER", "postgres")
    monkeypatch.setenv("NORMALIZATION_DEV_PASSWORD", "dev-pw")
    monkeypatch.setenv("NORMALIZATION_PROD_PASSWORD", "prod-pw")
    monkeypatch.setattr(refresh, "list_both", lambda dev, prod: (["a", "postgres"], ["a", "dev_only"]))

    def must_not_refresh(*args, **kwargs):
        raise AssertionError("--execute なしで複製してはいけない")

    monkeypatch.setattr(refresh, "refresh", must_not_refresh)
    assert refresh.main([]) == 0
