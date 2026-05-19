# Power BI — Geo Risk Intelligence

## Semantic model

Import or DirectLake from Gold tables in the active lakehouse:

| Table | Role | Key columns |
|-------|------|-------------|
| `gold_geo_traffic_daily` | Fact | date, country_code, event_count, revenue |
| `gold_fraud_signals` | Fact | session_id, flag_suspicious, is_vpn |
| `gold_customer_features` | Dimension | user_id, total_spend, primary_country |

## Starter pages

1. **Geo traffic** — map by `country_code`, bar chart events by date
2. **Fraud** — VPN %, table of `flag_suspicious = true`
3. **Customers** — top spenders by `total_spend`, timezone distribution

## Measures (examples)

```dax
VPN Rate = DIVIDE(CALCULATE(COUNTROWS(gold_fraud_signals), gold_fraud_signals[is_vpn] = TRUE()), COUNTROWS(gold_fraud_signals))
Total Revenue = SUM(gold_geo_traffic_daily[revenue])
```

## Per environment

| ENV | Dataset name |
|-----|----------------|
| dev | Geo Risk DEV |
| test | Geo Risk TEST |
| prod | Geo Risk PROD |

Point each dataset at the matching lakehouse (`lh_geo_risk_*`).
