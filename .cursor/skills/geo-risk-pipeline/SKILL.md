---
name: real-estate-demand-intelligence
description: Runs the AU Real Estate Demand Intelligence Fabric pipeline (property views, IPstack visitor geo, Gold decision tables). Use for suburb interest, conversion gaps, interstate demand, or Power BI agency analytics.
---

# Real Estate Demand Intelligence

## Flow
2_setup → 4_bronze (listings + views) → 5_silver (IPstack + join) → 6_gold

## Parameters
ENV, LAKEHOUSE, MOCK_IPSTACK, LOOKBACK_DAYS=90, VIEWS_FILE

## Gold tables
gold_suburb_interest, gold_conversion_gaps, gold_property_trends, gold_interstate_flow, gold_repeat_interest

See reference.md for schemas and Fabric setup.
