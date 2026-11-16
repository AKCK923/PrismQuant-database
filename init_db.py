#!/usr/bin/env python3
"""Create the PrismQuant MongoDB shell.

The script creates the database, collections, JSON Schema validators, and
indexes. It is idempotent by default. Use --reset only when you really want
to drop the target database first.
"""
from __future__ import annotations

import argparse
import os
import sys

from pymongo import MongoClient
from pymongo.errors import CollectionInvalid, OperationFailure, PyMongoError

from schema import COLLECTIONS, INDEXES, TIMESERIES, VALIDATORS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create PrismQuant MongoDB collections, validators, and indexes.")
    parser.add_argument(
        "--uri",
        default=os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017"),
        help="MongoDB connection URI (default: env MONGO_URI or mongodb://127.0.0.1:27017)",
    )
    parser.add_argument(
        "--db",
        default=os.getenv("MONGO_DB", "prismquant"),
        help="Database name (default: env MONGO_DB or prismquant)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop the target database before creating collections. Destructive.",
    )
    return parser.parse_args()


def collection_type(db, name: str) -> str | None:
    for info in db.list_collections(filter={"name": name}):
        return info.get("type", "collection")
    return None


def validator_options(name: str) -> dict:
    return {
        "validator": {"$jsonSchema": VALIDATORS[name]},
        "validationLevel": "strict",
        "validationAction": "error",
    }


def create_or_update_collections(db) -> None:
    existing = set(db.list_collection_names())

    for name in COLLECTIONS:
        if name in TIMESERIES:
            if name in existing:
                actual_type = collection_type(db, name)
                if actual_type != "timeseries":
                    raise RuntimeError(
                        f"{name} already exists as {actual_type!r}, but must be a time-series collection. "
                        "Run with --reset or drop it manually."
                    )
                print(f"OK    time-series exists: {name}")
            else:
                db.create_collection(name, timeseries=TIMESERIES[name])
                print(f"OK    created time-series: {name}")
            # MongoDB 8.0 does not allow a validator on a time-series collection.
            continue

        options = validator_options(name)
        if name in existing:
            try:
                db.command("collMod", name, **validator_options(name))
            except OperationFailure as exc:
                print(f"WARN  could not update validator for {name}: {exc}")
            print(f"OK    collection exists: {name}")
            continue

        try:
            db.create_collection(name, **options)
            print(f"OK    created collection: {name}")
        except CollectionInvalid as exc:
            raise RuntimeError(f"could not create {name}: {exc}") from exc


def create_indexes(db) -> None:
    for name, specs in INDEXES.items():
        for index_name, keys, options in specs:
            kwargs = dict(options)
            kwargs["name"] = index_name
            db[name].create_index(keys, **kwargs)
            suffix = " (unique)" if options.get("unique") else ""
            print(f"OK    index: {name}.{index_name}{suffix}")


def warn_legacy_collections(db) -> None:
    expected = set(COLLECTIONS)
    actual = set(db.list_collection_names())
    legacy = sorted(c for c in actual - expected if not c.startswith("system."))
    if legacy:
        print("WARN  extra collections not in this shell: " + ", ".join(legacy))
        print("      use --reset if you want a clean database")


def main() -> int:
    args = parse_args()
    client = MongoClient(args.uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
        db = client[args.db]

        if args.reset:
            print(f"RESET dropping database: {args.db}")
            client.drop_database(args.db)

        print(f"TARGET {args.uri} / {args.db}")
        create_or_update_collections(db)
        create_indexes(db)
        warn_legacy_collections(db)

        print("")
        print(f"DONE  {len(COLLECTIONS)} collections, {sum(len(v) for v in INDEXES.values())} indexes")
        print("NEXT  python seed_demo.py && python smoke_test.py")
        return 0
    except (PyMongoError, RuntimeError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
