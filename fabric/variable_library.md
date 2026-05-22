# Fabric Variable Library

| Variable | dev example | Notes |
|----------|-------------|-------|
| ENV | dev | dev, test, prod |
| LAKEHOUSE | lh_realestate_dev | Per environments.yaml |
| MOCK_IPSTACK | true | false in prod |
| LOOKBACK_DAYS | 90 | Property view history window |
| VIEWS_FILE | property_views_5k.csv | Under Files/raw/sample/ |
| IPSTACK_KEY_SECRET_NAME | ipstack-access-key | Key Vault in prod |

| MAX_IPSTACK_CALLS | 5 | Live IPstack safety cap |
| FORCE_REFRESH_IPSTACK | false | Re-enrich cached IPs when true |
| IPSTACK_ACCESS_KEY | secret reference | Store only in Fabric/Key Vault, never Git |
| KEY_VAULT_NAME | kv-ipstack | Key Vault short name or URI |
| IPSTACK_SECRET_NAME | ipstack-access-key | Secret containing the IPstack API key |
