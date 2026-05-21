# Azure Key Vault + Fabric Pipeline for IPstack

Use this for live IPstack testing in `ws_realestate_live_ipstack_dev`.

## 1. Create Key Vault

In Azure Portal:

1. Create a Key Vault, for example `kv-realestate-demo`.
2. Choose the same subscription/region as your Fabric trial resources if possible.
3. Keep soft delete enabled.

## 2. Add the IPstack secret

Create a secret:

| Field | Value |
|-------|-------|
| Name | `ipstack-access-key` |
| Value | your IPstack access key |

Do not store the key in GitHub, notebooks, screenshots, or Fabric output cells.

## 3. Grant secret read access

For trial/dev, grant your signed-in user permission to read secrets:

- Key Vault → Access control (IAM) or Access policies
- Role/permission: Key Vault Secrets User, or Secret Get/List access

If your tenant uses Fabric workspace identity, grant that identity secret read access too.

## 4. Configure Fabric Pipeline parameters

In `pl_realestate_demand_etl`, add or set these parameters for the Silver notebook activity:

| Parameter | Example |
|-----------|---------|
| `MOCK_IPSTACK` | `False` |
| `MAX_IPSTACK_CALLS` | `5` |
| `FORCE_REFRESH_IPSTACK` | `False` |
| `KEY_VAULT_NAME` | `kv-realestate-demo` |
| `IPSTACK_SECRET_NAME` | `ipstack-access-key` |

Pass these as notebook base parameters where Fabric supports notebook activity parameters.

## 5. First live test

Run the pipeline or run notebooks manually:

1. `2_setup`
2. `4_bronze_loader`
3. `5_silver_loader` with `MOCK_IPSTACK=False` and `MAX_IPSTACK_CALLS=5`
4. Check `bronze_ipstack_raw` and `bronze_ipstack_errors`
5. Run `6_gold_loader`

Keep `MAX_IPSTACK_CALLS` small until the API call path is proven.

## Troubleshooting

- If the notebook says a key is required, check `KEY_VAULT_NAME`, `IPSTACK_SECRET_NAME`, and Key Vault permissions.
- If Key Vault lookup fails, try passing the full vault URI as `KEY_VAULT_NAME`: `https://kv-realestate-demo.vault.azure.net/`.
- If IPstack returns empty data for synthetic IPs, test with a few real public IPs. Some sample IP ranges are documentation/test ranges.
