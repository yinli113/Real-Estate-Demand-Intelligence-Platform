# Geo Risk Intelligence Pipeline

# TL;DR

Fabric-first **Bronze → Silver → Gold** pipeline that enriches web/login events with [IPstack](https://ipstack.com/) geo data, builds fraud and customer-360 Gold tables, and feeds Power BI. Phase 1 uses **batch historical data (last 30 days)**, **dev/test/prod** environments, and **mock IPstack** for local runs.

## Architecture

```
CSV (Lakehouse Files) → bronze_events → IPstack → silver_* → gold_* → Power BI
```

| Layer | Tables |
|-------|--------|
| Bronze | `bronze_events`, `bronze_ipstack_raw`, `bronze_ipstack_errors` |
| Silver | `silver_ip_dim`, `silver_events_enriched` |
| Gold | `gold_geo_traffic_daily`, `gold_fraud_signals`, `gold_customer_features` |

Notebook layout matches [databricks_vic_traffic](https://github.com/yinli113/databricks_vic_traffic/tree/main/notebooks):

| # | Notebook |
|---|----------|
| 1 | `1_config.ipynb` — `Config`, env widgets |
| 2 | `2_setup.ipynb` — create Delta tables |
| 3 | `3_cleanup_old_tables.ipynb` — 30-day retention |
| 4 | `4_bronze_loader.ipynb` — ingest CSV |
| 5 | `5_silver_loader.ipynb` — IPstack + join |
| 6 | `6_gold_loader.ipynb` — analytics tables |

## Environments

Defined in [`config/environments.yaml`](config/environments.yaml):

| ENV | Lakehouse | Mock IPstack | Sample file |
|-----|-----------|--------------|-------------|
| dev | `lh_geo_risk_dev` | true | `events_100.csv` |
| test | `lh_geo_risk_test` | true | `events_5k.csv` |
| prod | `lh_geo_risk_prod` | false | `events_raw.csv` |

## Quick start (Fabric)

1. Create Lakehouse per env (e.g. `lh_geo_risk_dev`).
2. Upload `data/sample/events_100.csv` → `Files/raw/sample/events_100.csv`.
3. Upload `data/fixtures/ipstack/*.json` → `Files/fixtures/ipstack/`.
4. Import notebooks from `notebooks/`.
5. Create Variable Library — see [`fabric/variable_library.md`](fabric/variable_library.md).
6. Run: `2_setup` → `4_bronze` → `5_silver` → `6_gold` (widgets: `ENV=dev`, `MOCK_IPSTACK=true`).
7. Connect Power BI — see [`powerbi/README.md`](powerbi/README.md).

## Parameters (widgets / pipeline)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ENV` | dev | dev \| test \| prod |
| `LAKEHOUSE` | from yaml | Override lakehouse name |
| `MOCK_IPSTACK` | true | Use fixture JSON instead of API |
| `LOOKBACK_DAYS` | 30 | Only ingest last N days |
| `SOURCE_FILE` | events_100.csv | CSV under `Files/raw/sample/` |

## Secrets

- Set `IPSTACK_ACCESS_KEY` in Fabric Variable Library (prod) or `.env` locally.
- Never commit API keys.

## Phase 1 test checklist

- [ ] `MOCK_IPSTACK=true` — all Gold tables populated
- [ ] Live API on 5 IPs — `bronze_ipstack_raw` has JSON
- [ ] `gold_fraud_signals.flag_suspicious` true for VPN session `sess-velocity-001`
- [ ] Power BI shows country map and spend by region

## License

MIT
