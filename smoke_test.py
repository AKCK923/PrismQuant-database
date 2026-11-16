#!/usr/bin/env python3
"""Structural smoke test for the PrismQuant MongoDB shell."""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError, WriteError

from schema import COLLECTIONS, INDEXES, TIMESERIES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify collections, validators, indexes, and uniqueness.")
    parser.add_argument("--uri", default=os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017"))
    parser.add_argument("--db", default=os.getenv("MONGO_DB", "prismquant"))
    return parser.parse_args()


def check_collections(db) -> None:
    actual = set(db.list_collection_names())
    missing = sorted(set(COLLECTIONS) - actual)
    assert not missing, f"missing collections: {missing}"


def check_timeseries(db) -> None:
    info = list(db.list_collections(filter={"name": "market_bars"}))[0]
    assert info.get("type") == "timeseries", "market_bars is not a time-series collection"
    ts = info.get("options", {}).get("timeseries", {})
    assert ts.get("timeField") == "ts", "market_bars.timeField must be ts"
    assert ts.get("metaField") == "instrument_id", "market_bars.metaField must be instrument_id"


def check_validators(db) -> None:
    for name in COLLECTIONS:
        if name in TIMESERIES:
            # MongoDB 8.0 does not support validators on time-series collections.
            continue
        info = list(db.list_collections(filter={"name": name}))[0]
        validator = info.get("options", {}).get("validator")
        assert validator and "$jsonSchema" in validator, f"{name} has no JSON Schema validator"


def check_indexes(db) -> None:
    for name, specs in INDEXES.items():
        existing = db[name].index_information()
        for index_name, keys, options in specs:
            assert index_name in existing, f"missing index: {name}.{index_name}"
            if options.get("unique"):
                assert existing[index_name].get("unique") is True, f"not unique: {name}.{index_name}"


def check_no_ttl(db) -> None:
    for name in ("agent_state", "agent_store"):
        for index_name, info in db[name].index_information().items():
            assert "expireAfterSeconds" not in info, f"unexpected TTL on {name}.{index_name}"


def check_validator_rejects_bad_doc(db) -> None:
    try:
        db.users.insert_one({"user_id": "smoke-invalid-user"})
    except WriteError:
        return
    finally:
        db.users.delete_one({"user_id": "smoke-invalid-user"})
    raise AssertionError("users validator accepted a document without required fields")


def check_unique_agent_store(db) -> None:
    now = datetime.now(timezone.utc)
    doc = {
        "store_id": "smoke-store-1",
        "username": "__smoke__",
        "key": "preference.test",
        "value": {"ok": True},
        "value_type": "preference",
        "version": 1,
        "created_at": now,
        "updated_at": now,
    }
    db.agent_store.delete_many({"username": "__smoke__"})
    db.agent_store.insert_one(doc)
    duplicate = dict(doc, store_id="smoke-store-2")
    try:
        db.agent_store.insert_one(duplicate)
    except DuplicateKeyError:
        pass
    else:
        raise AssertionError("agent_store accepted duplicate (username, key)")
    finally:
        db.agent_store.delete_many({"username": "__smoke__"})


def main() -> int:
    args = parse_args()
    client = MongoClient(args.uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        db = client[args.db]
        check_collections(db)
        check_timeseries(db)
        check_validators(db)
        check_indexes(db)
        check_no_ttl(db)
        check_validator_rejects_bad_doc(db)
        check_unique_agent_store(db)
        print(f"PASS  {len(COLLECTIONS)} collections, document validators, indexes, time-series, uniqueness")
        return 0
    except (AssertionError, PyMongoError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
