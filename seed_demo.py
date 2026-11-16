#!/usr/bin/env python3
"""Insert a small, fictional demo dataset into the PrismQuant shell.

All names, prices, news, and identifiers are fake. The script is safe to run
more than once: normal collections are upserted by their natural key, and demo
market bars are replaced by source="demo".
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

from bson.decimal128 import Decimal128
from pymongo import MongoClient
from pymongo.errors import PyMongoError

DEMO_USER = "u-demo"
DEMO_CHAT = "chat-demo-1"
DEMO_RUN = "run-demo-1"
DEMO_INSTRUMENTS = ["US.NVDA", "HK.0700"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed fictional demo data.")
    parser.add_argument("--uri", default=os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017"))
    parser.add_argument("--db", default=os.getenv("MONGO_DB", "prismquant"))
    return parser.parse_args()


def dec(value: str) -> Decimal128:
    return Decimal128(value)


def upsert(coll, key: dict, doc: dict) -> None:
    coll.replace_one(key, doc, upsert=True)


def main() -> int:
    args = parse_args()
    client = MongoClient(args.uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        db = client[args.db]
        now = datetime(2026, 11, 13, 1, 0, tzinfo=timezone.utc)
        day = datetime(2026, 11, 12, tzinfo=timezone.utc)

        upsert(db.users, {"user_id": DEMO_USER}, {
            "user_id": DEMO_USER,
            "username": "demo",
            "email": "demo@example.com",
            "password_hash": "argon2id$demo$not-a-real-hash",
            "display_name": "Demo User",
            "role": "subscriber",
            "plan": "Basic",
            "plan_status": "active",
            "quota": {"backtests": 10, "people": 20, "ai_analyses": 50},
            "created_at": now,
            "last_login_at": now,
        })

        upsert(db.instruments, {"instrument_id": "US.NVDA"}, {
            "instrument_id": "US.NVDA",
            "symbol": "NVDA",
            "name": "NVIDIA Corp. (demo)",
            "asset_class": "equity",
            "exchange": "NASDAQ",
            "currency": "USD",
            "timezone": "America/New_York",
            "active": True,
        })
        upsert(db.instruments, {"instrument_id": "HK.0700"}, {
            "instrument_id": "HK.0700",
            "symbol": "0700",
            "name": "Tencent Holdings (demo)",
            "asset_class": "equity",
            "exchange": "HKEX",
            "currency": "HKD",
            "timezone": "Asia/Hong_Kong",
            "active": True,
        })

        # Time-series collections do not support replace_one; replace the demo slice.
        db.market_bars.delete_many({"source": "demo"})
        bars = []
        for i, close in enumerate(["180.10", "181.40", "179.80", "182.20"]):
            bars.append({
                "ts": day.replace(hour=1 + i),
                "instrument_id": "US.NVDA",
                "timeframe": "1d",
                "open": dec(close),
                "high": dec(close),
                "low": dec(close),
                "close": dec(close),
                "volume": dec("1000000"),
                "source": "demo",
                "ingested_at": now,
            })
        for i, close in enumerate(["420.00", "421.50"]):
            bars.append({
                "ts": day.replace(hour=1 + i),
                "instrument_id": "HK.0700",
                "timeframe": "1d",
                "open": dec(close),
                "high": dec(close),
                "low": dec(close),
                "close": dec(close),
                "volume": dec("500000"),
                "source": "demo",
                "ingested_at": now,
            })
        db.market_bars.insert_many(bars)

        upsert(db.news_articles, {"article_id": "art-demo-1"}, {
            "article_id": "art-demo-1",
            "canonical_url": "https://example.com/demo/nvda-supply",
            "source": {"source_id": "demo-wire", "source_name": "Demo Wire", "source_kind": "rss"},
            "title": "Demo: chip supplier expands capacity",
            "summary": "A fictional supply-chain headline for the shell demo.",
            "content": "This is fictional demo content. It is not a real news article.",
            "published_at": day.replace(hour=23),
            "first_seen": now,
            "last_seen": now,
            "content_hash": "demo-article-hash-1",
            "status": "analyzed",
            "analysis": {"sentiment": "bullish", "topics": ["semiconductors"], "confidence": 0.71},
            "search_tokens": ["晶片", "供應", "nvda", "semiconductor"],
        })

        upsert(db.a1_news_events, {"event_id": "a1-demo-1"}, {
            "event_id": "a1-demo-1",
            "title": "Demo: chip supplier expands capacity",
            "summary": "Fictional A1 event used by the database shell.",
            "sentiment": "bullish",
            "topics": ["semiconductors"],
            "instruments": ["US.NVDA"],
            "confidence": dec("0.71"),
            "source": "Demo Wire",
            "url": "https://example.com/demo/nvda-supply",
            "published_at": day.replace(hour=23),
            "sampled": True,
            "content_hash": "demo-a1-hash-1",
            "created_at": now,
        })

        upsert(db.news_events, {"event_id": "evt-demo-1"}, {
            "event_id": "evt-demo-1",
            "title": "Demo: semiconductor supply event",
            "status": "reviewed",
            "latest_version": 1,
            "revisions": [{
                "version": 1,
                "input_hash": "demo-event-input-1",
                "article_ids": ["art-demo-1"],
                "brief": "Fictional event brief for the shell demo.",
                "metadata": {"source_count": 1},
                "created_at": now,
            }],
            "created_by": DEMO_USER,
            "created_at": now,
            "updated_at": now,
        })

        upsert(db.a2_people, {"person_id": "p-demo-1"}, {
            "person_id": "p-demo-1",
            "name_original": "Demo Person",
            "name_zh": "示例人物",
            "aliases": ["Demo P."],
            "country_codes": ["US"],
            "monitoring_enabled": True,
            "created_at": now,
            "updated_at": now,
        })

        upsert(db.a2_public_records, {"record_id": "rec-demo-1"}, {
            "record_id": "rec-demo-1",
            "person_id": "p-demo-1",
            "title": "Demo public statement",
            "body_text": "This is a fictional public statement for the shell demo.",
            "source_name": "Demo Public Record",
            "publisher_name": "Demo Agency",
            "original_url": "https://example.com/demo/statement",
            "published_at": day.replace(hour=22),
            "language": "en",
            "verification_status": "verified",
            "analysis": {
                "entities": ["Demo Corp"],
                "markets": ["US"],
                "direction": "neutral",
                "confidence": 0.55,
                "summary": "Fictional analysis.",
            },
            "analyses": [{"version": 1, "summary": "Fictional analysis."}],
            "search_tokens": ["demo", "statement", "policy"],
        })

        upsert(db.a5_runs, {"run_id": DEMO_RUN}, {
            "run_id": DEMO_RUN,
            "user_id": DEMO_USER,
            "chat_id": DEMO_CHAT,
            "kind": "brief",
            "question": "Demo morning brief",
            "mode": "rule",
            "topology": "shared",
            "prompt_variant": "demo-v1",
            "latency_ms": 1200,
            "confidence": {"score": 0.62, "level": "medium", "reasons": ["demo data"]},
            "guard_passed": True,
            "payload": {
                "headline": "Demo brief headline",
                "evidence": [{"id": "N1", "agent": "A1", "title": "Demo event"}],
            },
            "snapshot": {
                "a1": {"events": ["a1-demo-1"]},
                "a2": {"records": ["rec-demo-1"]},
            },
            "tool_names": ["get_quote"],
            "created_at": now,
        })

        upsert(db.agent_context, {"context_id": "ctx-demo-1"}, {
            "context_id": "ctx-demo-1",
            "run_id": DEMO_RUN,
            "chat_id": DEMO_CHAT,
            "messages": [
                {"role": "system", "content": "You are A5."},
                {"role": "user", "content": "Demo morning brief"},
            ],
            "retrieved_keys": ["preference.risk_level"],
            "tool_observations": [{"tool": "get_quote", "status": "ok"}],
            "token_count": 420,
            "created_at": now,
        })

        upsert(db.agent_state, {"chat_id": DEMO_CHAT}, {
            "chat_id": DEMO_CHAT,
            "username": "demo",
            "messages": [
                {"role": "user", "content": "Demo morning brief"},
                {"role": "assistant", "content": "This is a fictional demo answer."},
            ],
            "working": {"last_topic": "semiconductors", "pending_intent": None},
            "active_run_id": DEMO_RUN,
            "status": "open",
            "created_at": now,
            "updated_at": now,
            "last_activity_at": now,
        })

        for store_id, key, value, value_type, tags in [
            ("store-demo-1", "preference.risk_level", {"level": "moderate"}, "preference", ["risk"]),
            ("store-demo-2", "preference.language", {"value": "zh-HK"}, "preference", ["language"]),
        ]:
            upsert(db.agent_store, {"username": "demo", "key": key}, {
                "store_id": store_id,
                "username": "demo",
                "key": key,
                "value": value,
                "value_type": value_type,
                "tags": tags,
                "source_run_id": DEMO_RUN,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            })

        upsert(db.tool_skills, {"name": "get_quote"}, {
            "name": "get_quote",
            "description": "Return a fictional quote for a demo instrument.",
            "input_schema": {"type": "object", "properties": {"symbol": {"type": "string"}}},
            "output_schema": {"type": "object", "properties": {"last": {"type": "number"}}},
            "endpoint": "http://127.0.0.1:8001/quote",
            "enabled": True,
            "version": 1,
            "updated_at": now,
        })

        upsert(db.paper_accounts, {"account_id": "acct-demo-1"}, {
            "account_id": "acct-demo-1",
            "user_id": DEMO_USER,
            "broker": "futu_simulate",
            "mode": "paper",
            "cash": dec("100000.00"),
            "equity": dec("100000.00"),
            "positions": [{
                "symbol": "US.NVDA",
                "qty": dec("10"),
                "avg_price": dec("180.10"),
                "market_value": dec("1801.00"),
            }],
            "version": 1,
            "updated_at": now,
        })

        upsert(db.paper_orders, {"order_id": "ord-demo-1"}, {
            "order_id": "ord-demo-1",
            "account_id": "acct-demo-1",
            "intent_id": "intent-demo-1",
            "symbol": "US.NVDA",
            "side": "buy",
            "qty": dec("10"),
            "order_type": "market",
            "status": "filled",
            "broker_order_id": "broker-demo-1",
            "idempotency_key": "demo-order-1",
            "filled_qty": 10,
            "created_at": now,
        })

        upsert(db.research_reports, {"report_id": "report-demo-1"}, {
            "report_id": "report-demo-1",
            "user_id": DEMO_USER,
            "title": "Demo research report",
            "status": "published",
            "current_version": 1,
            "revisions": [{
                "version": 1,
                "content": "Fictional report content.",
                "evidence": [{"run_id": DEMO_RUN, "event_id": "evt-demo-1"}],
                "created_at": now,
            }],
            "tags": ["demo", "semiconductors"],
            "created_at": now,
            "updated_at": now,
        })

        print("SEED  demo data inserted")
        print("      user=demo password is not a real credential; replace before any real use")
        return 0
    except PyMongoError as exc:
        print(f"FAIL  {exc}")
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
