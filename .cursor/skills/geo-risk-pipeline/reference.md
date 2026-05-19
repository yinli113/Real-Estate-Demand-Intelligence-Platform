# Reference

## Tables

- bronze_events, bronze_ipstack_raw, bronze_ipstack_errors
- silver_ip_dim, silver_events_enriched
- gold_geo_traffic_daily, gold_fraud_signals, gold_customer_features

## Fabric setup

1. Lakehouse per env from config/environments.yaml
2. Upload data/sample and data/fixtures to Files/
3. Variable Library: ENV, LAKEHOUSE, MOCK_IPSTACK, LOOKBACK_DAYS, SOURCE_FILE
4. Pipeline pl_geo_risk_etl — see fabric/pipelines/pl_geo_risk_etl.json

## Phase 2 triggers

- Streaming: Event Hub + Structured Streaming
- Hybrid C: Fabric Bronze + Databricks Silver/Gold
