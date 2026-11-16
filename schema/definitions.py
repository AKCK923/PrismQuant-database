"""PrismQuant MongoDB schema definitions.

This module is the single source of truth for the database shell:
collections, JSON Schema validators, and indexes.

It is intentionally independent from the application repositories.
"""

COLLECTIONS = [
    "users",
    "instruments",
    "market_bars",
    "a1_news_events",
    "news_articles",
    "news_events",
    "a2_people",
    "a2_public_records",
    "a5_runs",
    "agent_context",
    "agent_state",
    "agent_store",
    "tool_skills",
    "paper_accounts",
    "paper_orders",
    "research_reports",
]

# market_bars is the only time-series collection.
TIMESERIES = {
    "market_bars": {
        "timeField": "ts",
        "metaField": "instrument_id",
        "granularity": "seconds",
    }
}

VALIDATORS = {
    "users": {
        "bsonType": "object",
        "required": [
            "user_id", "username", "email", "password_hash", "role",
            "plan", "plan_status", "quota", "created_at",
        ],
        "properties": {
            "user_id": {"bsonType": "string"},
            "username": {"bsonType": "string"},
            "email": {"bsonType": "string"},
            "password_hash": {"bsonType": "string"},
            "display_name": {"bsonType": "string"},
            "role": {
                "bsonType": "string",
                "enum": ["subscriber", "analyst", "risk_manager", "admin"],
            },
            "plan": {
                "bsonType": "string",
                "enum": ["Basic", "Standard", "Professional"],
            },
            "plan_status": {
                "bsonType": "string",
                "enum": ["active", "past_due", "cancelled"],
            },
            "quota": {"bsonType": "object"},
            "created_at": {"bsonType": "date"},
            "last_login_at": {"bsonType": "date"},
        },
    },
    "instruments": {
        "bsonType": "object",
        "required": [
            "instrument_id", "symbol", "name", "asset_class", "exchange",
            "currency", "timezone", "active",
        ],
        "properties": {
            "instrument_id": {"bsonType": "string"},
            "symbol": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "asset_class": {
                "bsonType": "string",
                "enum": ["equity", "futures", "crypto", "fx"],
            },
            "exchange": {"bsonType": "string"},
            "currency": {"bsonType": "string"},
            "timezone": {"bsonType": "string"},
            "active": {"bsonType": "bool"},
        },
    },
    "market_bars": {
        "bsonType": "object",
        "required": [
            "ts", "instrument_id", "timeframe", "open", "high", "low", "close",
            "volume", "source", "ingested_at",
        ],
        "properties": {
            "ts": {"bsonType": "date"},
            "instrument_id": {"bsonType": "string"},
            "timeframe": {"bsonType": "string"},
            "open": {"bsonType": "decimal"},
            "high": {"bsonType": "decimal"},
            "low": {"bsonType": "decimal"},
            "close": {"bsonType": "decimal"},
            "volume": {"bsonType": "decimal"},
            "source": {"bsonType": "string"},
            "ingested_at": {"bsonType": "date"},
        },
    },
    "a1_news_events": {
        "bsonType": "object",
        "required": [
            "event_id", "title", "summary", "sentiment", "topics",
            "instruments", "confidence", "source", "url", "published_at",
            "sampled", "content_hash", "created_at",
        ],
        "properties": {
            "event_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "summary": {"bsonType": "string"},
            "sentiment": {
                "bsonType": "string",
                "enum": ["bullish", "bearish", "neutral"],
            },
            "topics": {"bsonType": "array", "items": {"bsonType": "string"}},
            "instruments": {"bsonType": "array", "items": {"bsonType": "string"}},
            "confidence": {"bsonType": "decimal"},
            "source": {"bsonType": "string"},
            "url": {"bsonType": "string"},
            "published_at": {"bsonType": "date"},
            "sampled": {"bsonType": "bool"},
            "content_hash": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
        },
    },
    "news_articles": {
        "bsonType": "object",
        "required": [
            "article_id", "canonical_url", "source", "title", "summary",
            "content", "published_at", "first_seen", "last_seen", "content_hash",
            "status", "search_tokens",
        ],
        "properties": {
            "article_id": {"bsonType": "string"},
            "canonical_url": {"bsonType": "string"},
            "source": {"bsonType": "object"},
            "title": {"bsonType": "string"},
            "summary": {"bsonType": "string"},
            "content": {"bsonType": "string"},
            "published_at": {"bsonType": "date"},
            "first_seen": {"bsonType": "date"},
            "last_seen": {"bsonType": "date"},
            "content_hash": {"bsonType": "string"},
            "status": {
                "bsonType": "string",
                "enum": ["pending", "analyzed", "error"],
            },
            "analysis": {"bsonType": "object"},
            "search_tokens": {"bsonType": "array", "items": {"bsonType": "string"}},
        },
    },
    "news_events": {
        "bsonType": "object",
        "required": [
            "event_id", "title", "status", "latest_version", "revisions",
            "created_by", "created_at", "updated_at",
        ],
        "properties": {
            "event_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "status": {
                "bsonType": "string",
                "enum": ["draft", "reviewed", "archived"],
            },
            "latest_version": {"bsonType": "int"},
            "revisions": {"bsonType": "array", "items": {"bsonType": "object"}},
            "created_by": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    },
    "a2_people": {
        "bsonType": "object",
        "required": [
            "person_id", "name_original", "country_codes",
            "monitoring_enabled", "created_at", "updated_at",
        ],
        "properties": {
            "person_id": {"bsonType": "string"},
            "name_original": {"bsonType": "string"},
            "name_zh": {"bsonType": "string"},
            "aliases": {"bsonType": "array", "items": {"bsonType": "string"}},
            "country_codes": {"bsonType": "array", "items": {"bsonType": "string"}},
            "monitoring_enabled": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    },
    "a2_public_records": {
        "bsonType": "object",
        "required": [
            "record_id", "person_id", "title", "body_text", "source_name",
            "publisher_name", "original_url", "published_at", "language",
            "verification_status", "search_tokens",
        ],
        "properties": {
            "record_id": {"bsonType": "string"},
            "person_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "body_text": {"bsonType": "string"},
            "source_name": {"bsonType": "string"},
            "publisher_name": {"bsonType": "string"},
            "original_url": {"bsonType": "string"},
            "published_at": {"bsonType": "date"},
            "language": {"bsonType": "string"},
            "verification_status": {
                "bsonType": "string",
                "enum": ["needs_review", "verified", "archive_only"],
            },
            "analysis": {"bsonType": "object"},
            "analyses": {"bsonType": "array", "items": {"bsonType": "object"}},
            "search_tokens": {"bsonType": "array", "items": {"bsonType": "string"}},
        },
    },
    "a5_runs": {
        "bsonType": "object",
        "required": [
            "run_id", "user_id", "chat_id", "kind", "mode", "topology",
            "prompt_variant", "latency_ms", "confidence", "guard_passed",
            "payload", "snapshot", "tool_names", "created_at",
        ],
        "properties": {
            "run_id": {"bsonType": "string"},
            "user_id": {"bsonType": "string"},
            "chat_id": {"bsonType": "string"},
            "kind": {
                "bsonType": "string",
                "enum": ["brief", "probe", "ask", "chat"],
            },
            "question": {"bsonType": "string"},
            "mode": {
                "bsonType": "string",
                "enum": ["rule", "shared", "lens", "split"],
            },
            "topology": {"bsonType": "string"},
            "prompt_variant": {"bsonType": "string"},
            "latency_ms": {"bsonType": "int"},
            "confidence": {"bsonType": "object"},
            "guard_passed": {"bsonType": "bool"},
            "payload": {"bsonType": "object"},
            "snapshot": {"bsonType": "object"},
            "tool_names": {"bsonType": "array", "items": {"bsonType": "string"}},
            "created_at": {"bsonType": "date"},
            "replay_of": {"bsonType": "string"},
        },
    },
    "agent_context": {
        "bsonType": "object",
        "required": [
            "context_id", "run_id", "chat_id", "messages", "token_count",
            "created_at",
        ],
        "properties": {
            "context_id": {"bsonType": "string"},
            "run_id": {"bsonType": "string"},
            "chat_id": {"bsonType": "string"},
            "messages": {"bsonType": "array", "items": {"bsonType": "object"}},
            "retrieved_keys": {"bsonType": "array", "items": {"bsonType": "string"}},
            "tool_observations": {"bsonType": "array", "items": {"bsonType": "object"}},
            "token_count": {"bsonType": "int"},
            "created_at": {"bsonType": "date"},
        },
    },
    "agent_state": {
        "bsonType": "object",
        "required": [
            "chat_id", "username", "messages", "working", "status",
            "created_at", "updated_at", "last_activity_at",
        ],
        "properties": {
            "chat_id": {"bsonType": "string"},
            "username": {"bsonType": "string"},
            "messages": {"bsonType": "array", "items": {"bsonType": "object"}},
            "working": {"bsonType": "object"},
            "active_run_id": {"bsonType": "string"},
            "status": {"bsonType": "string", "enum": ["open", "archived"]},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
            "last_activity_at": {"bsonType": "date"},
        },
    },
    "agent_store": {
        "bsonType": "object",
        "required": [
            "store_id", "username", "key", "value", "value_type",
            "version", "created_at", "updated_at",
        ],
        "properties": {
            "store_id": {"bsonType": "string"},
            "username": {"bsonType": "string"},
            "key": {"bsonType": "string"},
            "value": {"bsonType": "object"},
            "value_type": {
                "bsonType": "string",
                "enum": ["preference", "need", "habit", "fact"],
            },
            "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
            "source_run_id": {"bsonType": "string"},
            "version": {"bsonType": "int"},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    },
    "tool_skills": {
        "bsonType": "object",
        "required": [
            "name", "description", "input_schema", "output_schema",
            "endpoint", "enabled", "version", "updated_at",
        ],
        "properties": {
            "name": {"bsonType": "string"},
            "description": {"bsonType": "string"},
            "input_schema": {"bsonType": "object"},
            "output_schema": {"bsonType": "object"},
            "endpoint": {"bsonType": "string"},
            "enabled": {"bsonType": "bool"},
            "version": {"bsonType": "int"},
            "updated_at": {"bsonType": "date"},
        },
    },
    "paper_accounts": {
        "bsonType": "object",
        "required": [
            "account_id", "user_id", "broker", "mode", "cash", "equity",
            "positions", "version", "updated_at",
        ],
        "properties": {
            "account_id": {"bsonType": "string"},
            "user_id": {"bsonType": "string"},
            "broker": {"bsonType": "string"},
            "mode": {"bsonType": "string", "enum": ["paper", "live"]},
            "cash": {"bsonType": "decimal"},
            "equity": {"bsonType": "decimal"},
            "positions": {"bsonType": "array", "items": {"bsonType": "object"}},
            "version": {"bsonType": "int"},
            "updated_at": {"bsonType": "date"},
        },
    },
    "paper_orders": {
        "bsonType": "object",
        "required": [
            "order_id", "account_id", "symbol", "side", "qty", "order_type",
            "status", "idempotency_key", "filled_qty", "created_at",
        ],
        "properties": {
            "order_id": {"bsonType": "string"},
            "account_id": {"bsonType": "string"},
            "intent_id": {"bsonType": "string"},
            "symbol": {"bsonType": "string"},
            "side": {"bsonType": "string", "enum": ["buy", "sell"]},
            "qty": {"bsonType": "decimal"},
            "order_type": {
                "bsonType": "string",
                "enum": ["market", "limit"],
            },
            "limit_price": {"bsonType": "decimal"},
            "status": {
                "bsonType": "string",
                "enum": ["preview", "submitted", "filled", "cancelled", "unknown"],
            },
            "broker_order_id": {"bsonType": "string"},
            "idempotency_key": {"bsonType": "string"},
            "filled_qty": {"bsonType": "int"},
            "created_at": {"bsonType": "date"},
        },
    },
    "research_reports": {
        "bsonType": "object",
        "required": [
            "report_id", "user_id", "title", "status", "current_version",
            "revisions", "tags", "created_at", "updated_at",
        ],
        "properties": {
            "report_id": {"bsonType": "string"},
            "user_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "status": {
                "bsonType": "string",
                "enum": ["draft", "published", "archived"],
            },
            "current_version": {"bsonType": "int"},
            "revisions": {"bsonType": "array", "items": {"bsonType": "object"}},
            "tags": {"bsonType": "array", "items": {"bsonType": "string"}},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    },
}

# Each entry is: name, key list, options.
INDEXES = {
    "users": [
        ("uq_users_username", [("username", 1)], {"unique": True}),
        ("uq_users_email", [("email", 1)], {"unique": True}),
        ("ix_users_role", [("role", 1)], {}),
        ("ix_users_plan_status", [("plan_status", 1)], {}),
    ],
    "instruments": [
        ("uq_instruments_id", [("instrument_id", 1)], {"unique": True}),
        ("uq_instruments_symbol_exchange", [("symbol", 1), ("exchange", 1)], {"unique": True}),
        ("ix_instruments_asset_class", [("asset_class", 1)], {}),
        ("ix_instruments_active", [("active", 1)], {}),
    ],
    "market_bars": [
        ("ix_bars_instrument_tf_ts", [("instrument_id", 1), ("timeframe", 1), ("ts", -1)], {}),
    ],
    "a1_news_events": [
        ("uq_a1_content_hash", [("content_hash", 1)], {"unique": True}),
        ("ix_a1_published_at", [("published_at", -1)], {}),
        ("ix_a1_instruments_published", [("instruments", 1), ("published_at", -1)], {}),
    ],
    "news_articles": [
        ("uq_articles_canonical_url", [("canonical_url", 1)], {"unique": True}),
        ("uq_articles_content_hash", [("content_hash", 1)], {"unique": True}),
        ("ix_articles_published_at", [("published_at", -1)], {}),
        ("ix_articles_search_tokens", [("search_tokens", 1)], {}),
    ],
    "news_events": [
        ("uq_news_events_event_id", [("event_id", 1)], {"unique": True}),
        ("ix_news_events_updated_at", [("updated_at", -1)], {}),
        ("ix_news_events_created_by", [("created_by", 1)], {}),
    ],
    "a2_people": [
        ("uq_a2_people_person_id", [("person_id", 1)], {"unique": True}),
        ("ix_a2_people_name_zh", [("name_zh", 1)], {}),
        ("ix_a2_people_aliases", [("aliases", 1)], {}),
        ("ix_a2_people_monitoring", [("monitoring_enabled", 1)], {}),
    ],
    "a2_public_records": [
        ("uq_a2_records_record_id", [("record_id", 1)], {"unique": True}),
        ("ix_a2_records_person_published", [("person_id", 1), ("published_at", -1)], {}),
        ("ix_a2_records_search_tokens", [("search_tokens", 1)], {}),
    ],
    "a5_runs": [
        ("uq_a5_runs_run_id", [("run_id", 1)], {"unique": True}),
        ("ix_a5_runs_chat_id", [("chat_id", 1)], {}),
        ("ix_a5_runs_created_at", [("created_at", -1)], {}),
        ("ix_a5_runs_tool_names", [("tool_names", 1)], {}),
    ],
    "agent_context": [
        ("ix_agent_context_run_id", [("run_id", 1)], {}),
        ("ix_agent_context_chat_id", [("chat_id", 1)], {}),
    ],
    "agent_state": [
        ("ix_agent_state_username_updated", [("username", 1), ("updated_at", -1)], {}),
        ("ix_agent_state_status", [("status", 1)], {}),
    ],
    "agent_store": [
        ("uq_agent_store_username_key", [("username", 1), ("key", 1)], {"unique": True}),
        ("ix_agent_store_tags", [("tags", 1)], {}),
        ("ix_agent_store_value_type", [("value_type", 1)], {}),
        ("ix_agent_store_source_run", [("source_run_id", 1)], {}),
    ],
    "tool_skills": [
        ("uq_tool_skills_name", [("name", 1)], {"unique": True}),
        ("ix_tool_skills_enabled", [("enabled", 1)], {}),
    ],
    "paper_accounts": [
        ("uq_paper_accounts_account_id", [("account_id", 1)], {"unique": True}),
        ("ix_paper_accounts_user_id", [("user_id", 1)], {}),
    ],
    "paper_orders": [
        ("uq_paper_orders_idempotency", [("idempotency_key", 1)], {"unique": True}),
        ("ix_paper_orders_account_created", [("account_id", 1), ("created_at", -1)], {}),
        ("ix_paper_orders_status", [("status", 1)], {}),
    ],
    "research_reports": [
        ("uq_research_reports_report_id", [("report_id", 1)], {"unique": True}),
        ("ix_research_reports_updated_at", [("updated_at", -1)], {}),
        ("ix_research_reports_tags", [("tags", 1)], {}),
    ],
}
