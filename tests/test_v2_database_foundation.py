from __future__ import annotations

import inspect
import json
from pathlib import Path

from fastapi.testclient import TestClient


def sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


def test_database_initializes_core_tables(tmp_path):
    from src.db.migrations import initialize_database
    from src.db.session import get_connection

    db_url = sqlite_url(tmp_path / "foundation.db")
    initialize_database(db_url)

    with get_connection(db_url) as connection:
        rows = connection.execute(
            "select name from sqlite_master where type='table' order by name"
        ).fetchall()

    table_names = {row["name"] for row in rows}
    assert {"users", "strategy_reports", "api_keys", "billing_plans", "audit_logs"}.issubset(table_names)


def test_user_repository_creates_gets_and_lists_users(tmp_path):
    from src.db.migrations import initialize_database
    from src.db.repository import UserRepository

    db_url = sqlite_url(tmp_path / "users.db")
    initialize_database(db_url)
    users = UserRepository(db_url)

    created = users.create_user("alice", email="alice@example.com", role="admin", plan="pro")
    fetched = users.get_user_by_user_id("alice")

    assert created["user_id"] == "alice"
    assert fetched["email"] == "alice@example.com"
    assert fetched["role"] == "admin"
    assert fetched["plan"] == "pro"
    assert users.list_users()[0]["user_id"] == "alice"


def test_strategy_report_repository_saves_lists_gets_and_deletes(tmp_path):
    from src.db.migrations import initialize_database
    from src.db.repository import StrategyReportRepository

    db_url = sqlite_url(tmp_path / "reports.db")
    initialize_database(db_url)
    reports = StrategyReportRepository(db_url)

    saved = reports.save_report(
        user_id="alice",
        strategy_name="trend_default",
        report_id="report-1",
        research_view="momentum",
        quality_score=88.5,
        quality_level="High",
        report_json={"ok": True},
        markdown="# Report",
    )

    assert saved["report_id"] == "report-1"
    assert reports.get_report("report-1", user_id="alice")["report_json"]["ok"] is True
    assert reports.list_reports_by_user("alice")[0]["strategy_name"] == "trend_default"
    assert reports.delete_report("report-1", user_id="alice") is True
    assert reports.list_reports_by_user("alice") == []


def test_api_key_repository_hashes_values_and_never_stores_plaintext(tmp_path):
    from src.db.migrations import initialize_database
    from src.db.repository import ApiKeyRepository

    db_url = sqlite_url(tmp_path / "keys.db")
    initialize_database(db_url)
    keys = ApiKeyRepository(db_url)

    record = keys.create_api_key_record(user_id="alice", key_id="key-1", key_value="plain-secret-value")
    listed = keys.list_api_keys_by_user("alice")

    assert record["key_hash"] != "plain-secret-value"
    assert "plain-secret-value" not in json.dumps(listed)
    assert listed[0]["key_id"] == "key-1"
    assert listed[0]["status"] == "active"
    assert keys.revoke_api_key("key-1", user_id="alice") is True
    assert keys.list_api_keys_by_user("alice")[0]["status"] == "revoked"


def test_billing_and_audit_repositories_are_user_scoped(tmp_path):
    from src.db.migrations import initialize_database
    from src.db.repository import AuditLogRepository, BillingRepository

    db_url = sqlite_url(tmp_path / "billing_audit.db")
    initialize_database(db_url)
    billing = BillingRepository(db_url)
    audit = AuditLogRepository(db_url)

    billing.set_user_plan("alice", "team", status="mock_active")
    audit.add_log("alice", action="report.created", resource_type="report", resource_id="r1", metadata={"ok": True})

    assert billing.get_user_plan("alice")["plan_name"] == "team"
    assert billing.get_user_plan("bob") is None
    assert audit.list_logs_by_user("alice")[0]["metadata_json"]["ok"] is True
    assert audit.list_logs_by_user("bob") == []


def test_archive_importer_empty_and_corrupted_archives_do_not_crash(tmp_path):
    from src.db.archive_importer import import_archived_reports_to_db
    from src.db.migrations import initialize_database

    db_url = sqlite_url(tmp_path / "archive.db")
    archive_dir = tmp_path / "reports" / "strategy_research_reports"
    archive_dir.mkdir(parents=True)
    (archive_dir / "broken.json").write_text("{not-json", encoding="utf-8")
    initialize_database(db_url)

    result = import_archived_reports_to_db(user_id="default", archive_dir=archive_dir, database_url=db_url)

    assert result["imported_count"] == 0
    assert result["skipped_count"] == 1
    assert result["warnings"]


def test_archive_importer_imports_valid_legacy_json(tmp_path):
    from src.db.archive_importer import import_archived_reports_to_db
    from src.db.migrations import initialize_database
    from src.db.repository import StrategyReportRepository

    db_url = sqlite_url(tmp_path / "archive_valid.db")
    archive_dir = tmp_path / "reports" / "strategy_research_reports"
    archive_dir.mkdir(parents=True)
    (archive_dir / "legacy.json").write_text(
        json.dumps(
            {
                "strategy_name": "legacy_strategy",
                "research_view": "summary",
                "quality_score": 77,
                "quality_level": "Medium",
                "markdown": "# Legacy",
            }
        ),
        encoding="utf-8",
    )
    initialize_database(db_url)

    result = import_archived_reports_to_db(user_id="default", archive_dir=archive_dir, database_url=db_url)
    reports = StrategyReportRepository(db_url).list_reports_by_user("default")

    assert result["imported_count"] == 1
    assert reports[0]["strategy_name"] == "legacy_strategy"


def test_v2_database_api_endpoints_return_warnings_instead_of_crashing(tmp_path, monkeypatch):
    from src.api.v2.server import create_v2_api_app
    from src.config import database_config

    db_url = sqlite_url(tmp_path / "api.db")
    monkeypatch.setattr(database_config, "DATABASE_URL", db_url)
    client = TestClient(create_v2_api_app())

    health = client.get("/api/v2/system/db-health")
    default_user = client.get("/api/v2/users/default")
    db_reports = client.get("/api/v2/reports/db-list", params={"user_id": "default"})

    assert health.status_code == 200
    assert health.json()["success"] is True
    assert health.json()["data"]["database"]["status"] == "ok"
    assert default_user.status_code == 200
    assert db_reports.status_code == 200
    assert isinstance(db_reports.json()["warning"], list)


def test_v2_database_source_keeps_safety_boundaries():
    import src.config.database_config as database_config
    import src.db.archive_importer as archive_importer
    import src.db.repository as repository

    combined = "\n".join(
        [
            inspect.getsource(database_config),
            inspect.getsource(archive_importer),
            inspect.getsource(repository),
        ]
    ).lower()
    forbidden = [
        "broker " + "api",
        "auto" + "order",
        "place_" + "order",
        "open" + "ai",
        "stripe_" + "secret",
        "password=",
        "token=",
        "eval(",
        "exec(",
    ]
    for word in forbidden:
        assert word not in combined
