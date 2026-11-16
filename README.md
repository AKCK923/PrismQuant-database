# PrismQuant MongoDB Shell

A standalone MongoDB database shell for the PrismQuant project.

This repository contains **database structure only**:

- 16 collections
- JSON Schema validators
- indexes
- one time-series collection (`market_bars`)
- small fictional demo data
- a structural smoke test

It is **not** connected to A1／A2／A3／A4／A5, the web app, or any existing
application storage. It does not replace SQLite／PostgreSQL and it is not a
production deployment.

## Requirements

- MongoDB 8.0 (local install or Docker)
- Python 3.10+
- `pymongo`

## Quick start with Docker

```bash
docker compose up -d
python -m pip install -r requirements.txt
python init_db.py
python seed_demo.py
python smoke_test.py
```

Expected final line:

```text
PASS  16 collections, document validators, indexes, time-series, uniqueness
```

Open MongoDB Compass and connect to:

```text
mongodb://127.0.0.1:27017
```

Database: `prismquant`

## Quick start with a local MongoDB

If MongoDB is already running on `127.0.0.1:27017`:

```bash
python -m pip install -r requirements.txt
python init_db.py
python seed_demo.py
python smoke_test.py
```

Use a different server or database with:

```bash
python init_db.py --uri mongodb://127.0.0.1:27017 --db prismquant
python seed_demo.py --uri mongodb://127.0.0.1:27017 --db prismquant
python smoke_test.py --uri mongodb://127.0.0.1:27017 --db prismquant
```

`MONGO_URI` and `MONGO_DB` environment variables are also supported; see
`.env.example`.

## Commands

| Command | Purpose |
|---|---|
| `python init_db.py` | Create missing collections, validators, and indexes; safe to rerun |
| `python init_db.py --reset` | Drop the target database first; destructive |
| `python seed_demo.py` | Insert fictional demo data |
| `python smoke_test.py` | Verify collections, validators, indexes, time-series, uniqueness |

Do not run `--reset` against a database you care about.

## Collections

| Collection | Purpose |
|---|---|
| `users` | Accounts, roles, plans, quota |
| `instruments` | Cross-market instrument master |
| `market_bars` | OHLCV time-series, keyed by `instrument_id` |
| `a1_news_events` | Structured A1 news events |
| `news_articles` | Full article content and analysis |
| `news_events` | Versioned multi-source events |
| `a2_people` | Monitored people |
| `a2_public_records` | Public statements and analyses |
| `a5_runs` | Decision records, replay snapshots, evidence |
| `agent_context` | Per-LLM-call working memory |
| `agent_state` | Per-chat-window state |
| `agent_store` | Cross-session long-term memory, `(username, key)` unique |
| `tool_skills` | A5 tool registry |
| `paper_accounts` | Paper trading accounts |
| `paper_orders` | Paper orders and idempotency |
| `research_reports` | Versioned research reports |

## Memory model

The three memory collections are deliberately separate:

| Collection | Scope | Lifecycle |
|---|---|---|
| `agent_context` | One LLM call | No TTL; execution environment may clear it after the call |
| `agent_state` | One chat window | No TTL; removed when the chat is deleted or archived |
| `agent_store` | Cross-session | No TTL; removed when the user deletes the key or closes the account |

`agent_store` uses a unique compound index:

```text
(username, key)
```

Each document stores one JSON `value`. It is a catalogue of long-term
preferences/needs, not a copy of the conversation.

## Design notes

- `market_bars` uses `instrument_id` as its time-series `metaField`, not
  `symbol`, to avoid cross-exchange collisions.
- `a5_runs` stores the output payload and the input snapshot used at decision
  time; full articles and market bars stay in their own collections.
- `agent_state` and `agent_store` intentionally have **no TTL index**.
- JSON Schema validators cover the 15 document collections. MongoDB 8.0 does
  not support a validator on a time-series collection, so `market_bars` is
  validated at the ingestion/application layer instead.
- There are no cross-collection foreign keys; referential integrity is handled
  by the application layer.
- This shell uses a standalone MongoDB by default. Multi-document transactions
  and change streams require a replica set; see the limitation below.

## Limitations

This is a database skeleton, not a production service:

- no API
- no agent pipeline integration
- no authentication (local development only)
- no TLS
- no backup/restore policy
- no multi-document transaction guarantee on standalone MongoDB
- no change stream on standalone MongoDB

For transactions or change streams, run MongoDB as a replica set. A
single-node replica set is enough for local development.

## Repository layout

```text
.
├─ init_db.py
├─ seed_demo.py
├─ smoke_test.py
├─ schema/
│  └─ definitions.py
├─ docs/
│  ├─ collections.md
│  ├─ relationships.mmd
│  └─ relationship.png
├─ scripts/
│  ├─ start.cmd
│  ├─ start-local.cmd
│  ├─ reset.cmd
│  └─ stop.cmd
├─ docker-compose.yml
├─ requirements.txt
└─ .github/workflows/smoke.yml
```

## Publishing to GitHub

If this repository is not created yet:

```bash
git init
git add .
git commit -m "Create PrismQuant MongoDB database shell"
gh repo create prismquant-db-shell --private --source . --remote origin --push
```

Or create an empty repository on GitHub, then:

```bash
git remote add origin https://github.com/<account>/prismquant-db-shell.git
git branch -M main
git push -u origin main
```

Do not commit `.env`, database files, logs, or real user data.
