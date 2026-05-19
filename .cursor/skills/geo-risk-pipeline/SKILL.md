---
name: geo-risk-pipeline
description: Runs and extends the Geo Risk Intelligence Fabric medallion pipeline (IPstack enrichment, Bronze/Silver/Gold Delta, 30-day batch). Use when working on this repo, Fabric notebooks, IPstack, fraud Gold, customer 360, or Power BI.
---

# Geo Risk Pipeline

## E2E promotion

1. dev — events_100.csv, MOCK_IPSTACK=true, run 2_setup → 4 → 5 → 6
2. test — events_5k.csv, validate row counts and joins
3. prod — real 30-day export, MOCK_IPSTACK=false, live API for new IPs only

## Phase 1 checklist

- [ ] All Gold tables populated (mock run)
- [ ] 5 live IPstack calls succeed
- [ ] flag_suspicious for sess-velocity-001
- [ ] Power BI refresh OK

## Parameters

ENV, LAKEHOUSE, MOCK_IPSTACK, LOOKBACK_DAYS=30, SOURCE_FILE

## Notebooks

1_config, 2_setup, 3_cleanup, 4_bronze_loader, 5_silver_loader, 6_gold_loader

## Troubleshooting

- 429: enable mock or slow down API loop
- Null country: check fixture JSON path or bronze_ipstack_raw
- Wrong table: verify ENV matches lakehouse in environments.yaml

See [reference.md](reference.md) for table list and Fabric setup.
