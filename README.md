# Real Estate Demand Intelligence Platform (Australia)

# TL;DR

Microsoft Fabric **Bronze → Silver → Gold** pipeline for **Australian real estate agencies**. Combines **property portal events** (views, enquiries) with **IPstack visitor geo enrichment** to answer: *what to promote, in which suburbs, at what price range, and when* — not just page-view dashboards.

## Core business goal

Help an agency decide:

- Which **suburbs** attract interstate / overseas interest  
- Which **property types** and **price ranges** convert best  
- Where **high views but low enquiries** signal a promotion problem  
- Which regions are **trending** month-over-month  

## Architecture

```
listings.csv + property_views.csv (Lakehouse Files)
    → Bronze: listings + views + IPstack raw JSON
    → Silver: silver_visits_enriched (property ⨝ visitor geo)
    → Gold: 8 decision-support tables
    → Power BI agency briefing
```

| Layer | Tables |
|-------|--------|
| Bronze | `bronze_listings`, `bronze_property_views`, `bronze_ipstack_raw` |
| Silver | `silver_listings`, `silver_ip_dim`, `silver_visits_enriched` |
| Gold | `gold_suburb_interest`, `gold_property_type_by_suburb`, `gold_price_engagement`, `gold_conversion_gaps`, `gold_property_trends`, `gold_region_type_preference`, `gold_repeat_interest`, `gold_interstate_flow` |

## What IPstack does (and does not do)

| IPstack provides | Your portal data provides |
|------------------|---------------------------|
| Visitor country, region, city (from IP) | Suburb, price, property type, bedrooms |
| Timezone, ISP | View duration, enquiry, favorite flags |
| VPN/proxy flags | Listing catalog, session behavior |

IPstack does **not** supply property listings or company CRM data.

## Notebooks (Fabric / PySpark)

| # | Notebook | Purpose |
|---|----------|---------|
| 1 | `1_config.ipynb` | dev/test/prod, lakehouse, mock IPstack |
| 2 | `2_setup.ipynb` | Create Delta tables |
| 3 | `3_cleanup_old_tables.ipynb` | 90-day retention |
| 4 | `4_bronze_loader.ipynb` | Ingest listings + property views |
| 5 | `5_silver_loader.ipynb` | IPstack on visitor IP + enrich joins |
| 6 | `6_gold_loader.ipynb` | Build 8 Gold analytics tables |

## Sample data (synthetic POC)

| File | Rows | Seeded stories |
|------|------|----------------|
| `data/sample/listings.csv` | 160 | VIC/NSW/QLD suburbs, luxury flags |
| `data/sample/property_views_500.csv` | 500 | Optional quick smoke test |
| `data/sample/property_views_5k.csv` | 5,000 | Default Fabric demo + trends |
| `data/fixtures/ipstack/` | 22 IPs | Sydney, Melbourne, Brisbane, SG, HK |

**Seeded analytics stories:** Richmond (high views / low conversion), Box Hill interstate townhouse interest, overseas luxury views, repeat session intent.

Regenerate: `python3 scripts/generate_sample_data.py`

## Quick start (Fabric)

1. Create lakehouse `lh_realestate_dev` and attach to notebooks.
2. Upload `data/sample/listings.csv` and `property_views_5k.csv` → `Files/raw/sample/`.
3. Upload `data/fixtures/ipstack/*.json` → `Files/fixtures/ipstack/`.
4. Open each notebook and run cells top-to-bottom: `2_setup` → `4_bronze` → `5_silver` (`MOCK_IPSTACK=True`) → `6_gold`.
5. Build Power BI from Gold tables — see [`powerbi/README.md`](powerbi/README.md).

## Parameters

| Parameter | Default (dev) | Description |
|-----------|---------------|-------------|
| ENV | dev | dev \| test \| prod |
| LOOKBACK_DAYS | 90 | View history window |
| MOCK_IPSTACK | true | Use fixture JSON for visitor IPs |
| VIEWS_FILE | property_views_5k.csv | Views CSV filename |
| MAX_IPSTACK_CALLS | 5 | Live API safety cap |
| FORCE_REFRESH_IPSTACK | false | Re-call IPstack even when cache exists |



## IPstack Modes

Development should normally use mock mode:

```python
MOCK_IPSTACK = True
```

This reads fixture JSON from `Files/fixtures/ipstack/` and keeps runs deterministic.

For a live API smoke test in `feature/live-ipstack-controls`:

```python
MOCK_IPSTACK = False
MAX_IPSTACK_CALLS = 5
FORCE_REFRESH_IPSTACK = False
IPSTACK_ACCESS_KEY = ""  # set in Fabric workspace only; never commit a real key
```

Live mode skips IPs already present in `silver_ip_dim` unless `FORCE_REFRESH_IPSTACK=True`. The safety cap prevents burning API quota during testing.

## Environments

See [`config/environments.yaml`](config/environments.yaml).

## Phase 2

- Notebook/API ingest from real portal instead of CSV  
- Hour-of-day engagement Gold table  
- Optional Kafka for live property views  

## License

MIT
