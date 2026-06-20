from __future__ import annotations


CREATE_TABLES_SQL = [
    """
    create table if not exists users (
        id integer primary key autoincrement,
        user_id text not null unique,
        email text,
        role text not null default 'user',
        plan text not null default 'free',
        created_at text not null,
        updated_at text not null,
        is_active integer not null default 1
    )
    """,
    """
    create table if not exists strategy_reports (
        id integer primary key autoincrement,
        report_id text not null unique,
        user_id text not null,
        strategy_name text not null,
        research_view text,
        quality_score real,
        quality_level text,
        generated_at text not null,
        saved_at text not null,
        report_json text not null default '{}',
        markdown text not null default '',
        created_at text not null
    )
    """,
    """
    create index if not exists idx_strategy_reports_user_saved
    on strategy_reports(user_id, saved_at)
    """,
    """
    create table if not exists api_keys (
        id integer primary key autoincrement,
        user_id text not null,
        key_id text not null unique,
        key_hash text not null,
        status text not null default 'active',
        created_at text not null,
        revoked_at text,
        usage_count integer not null default 0
    )
    """,
    """
    create index if not exists idx_api_keys_user
    on api_keys(user_id)
    """,
    """
    create table if not exists billing_plans (
        id integer primary key autoincrement,
        user_id text not null unique,
        plan_name text not null default 'free',
        status text not null default 'mock_active',
        started_at text not null,
        expires_at text
    )
    """,
    """
    create table if not exists audit_logs (
        id integer primary key autoincrement,
        user_id text not null,
        action text not null,
        resource_type text,
        resource_id text,
        created_at text not null,
        metadata_json text not null default '{}'
    )
    """,
    """
    create index if not exists idx_audit_logs_user_created
    on audit_logs(user_id, created_at)
    """,
    """
    create table if not exists user_sessions (
        id integer primary key autoincrement,
        session_id text not null unique,
        user_id text not null,
        status text not null default 'active',
        created_at text not null,
        expires_at text not null,
        revoked_at text,
        last_seen_at text,
        metadata_json text not null default '{}'
    )
    """,
    """
    create index if not exists idx_user_sessions_user
    on user_sessions(user_id, status)
    """,
    """
    create table if not exists user_permissions (
        id integer primary key autoincrement,
        user_id text not null,
        role text not null,
        permission text not null,
        resource_type text not null default '',
        created_at text not null,
        unique(user_id, permission, resource_type)
    )
    """,
    """
    create index if not exists idx_user_permissions_user
    on user_permissions(user_id, permission)
    """,
]
