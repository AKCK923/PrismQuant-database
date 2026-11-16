# Collection Reference

This is a short reference for the 16 collections in the shell. The executable
source of truth is `schema/definitions.py`.

## users

Account, role, plan, quota, and login metadata. `username` and `email` are
unique. Passwords are represented by a hash field; the demo value is not a real
credential.

## instruments

Cross-market instrument master. `instrument_id` is the stable key and
`(symbol, exchange)` is unique.

## market_bars

Time-series OHLCV data. `timeField` is `ts`; `metaField` is `instrument_id`.
`instrument_id` is used instead of `symbol` so the same ticker on different
exchanges cannot collide.

## a1_news_events

Structured events produced by A1. `content_hash` is unique for deduplication;
`instruments`, `topics`, and `search_tokens` are arrays.

## news_articles

Full article body and analysis. `canonical_url` and `content_hash` are unique.
`search_tokens` is pre-tokenised text for multikey search.

## news_events

Versioned multi-source events. `event_id` is unique; `revisions` keeps the
article set and brief for each version; `latest_version` points to the newest
revision.

## a2_people

Monitored people and organisations. `aliases` and `country_codes` are arrays.

## a2_public_records

Public statements and their analyses. `analysis` embeds the latest analysis;
`analyses` keeps historical summaries.

## a5_runs

The decision record. `run_id` is unique; `user_id` and `chat_id` link the run
to its owner and chat window. `payload` is the output; `snapshot` is the input
used at decision time; `tool_names` records which tools were used.

## agent_context

One LLM call's working memory: messages, retrieved `agent_store` keys, tool
observations, and token count. No TTL.

## agent_state

One chat window's mutable state: messages, working variables, pending intent,
active run, and status. No TTL; removed only when the chat is deleted or
archived.

## agent_store

Cross-session long-term memory catalogue. Unique `(username, key)`; each key
maps to one JSON `value`. No TTL; removed when the user deletes the key or the
account is closed.

## tool_skills

A5 tool registry. `name` is unique; `input_schema` and `output_schema` are JSON
Schema objects.

## paper_accounts

Paper trading account. Cash and positions are kept in one document for atomic
single-document updates; `version` supports optimistic locking.

## paper_orders

Paper order records. `idempotency_key` is unique so retries do not create
duplicate orders; `account_id` links the order to its account.

## research_reports

Versioned research reports. `revisions` stores content and evidence;
`current_version` points to the newest revision.
