# Fabric Variable Library

Create a Variable Library in each workspace and attach to `pl_geo_risk_etl`.

| Variable | Example (dev) | Notes |
|----------|---------------|-------|
| `ENV` | dev | dev, test, prod |
| `LAKEHOUSE` | lh_geo_risk_dev | Matches environments.yaml |
| `MOCK_IPSTACK` | true | false in prod |
| `LOOKBACK_DAYS` | 30 | Historical window |
| `SOURCE_FILE` | events_100.csv | Under Files/raw/sample/ |
| `IPSTACK_KEY_SECRET_NAME` | ipstack-access-key | Key Vault reference in prod |

Pipeline notebook activities should pass these as base parameters.
