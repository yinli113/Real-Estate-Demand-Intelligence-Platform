# CI/CD — Real Estate Demand Intelligence Platform

# TL;DR

**Azure DevOps** is the source of truth for Fabric Git integration. **GitHub** mirrors the repo for portfolio and local development. Deploy by merging to `main`, updating the prod Fabric workspace from Git, running the pipeline once, then scheduling daily runs and publishing Power BI.

---

## Architecture

```
┌─────────────┐     push      ┌──────────────┐     Git sync     ┌─────────────────────┐
│ Local /     │ ────────────► │ GitHub       │                  │                     │
│ Cursor      │               │ (portfolio)  │                  │  Fabric prod        │
└─────────────┘               └──────────────┘                  │  ws_realestate_pro  │
       │                                                        │  lh_realestate_pro  │
       │ commit                                                 └──────────▲──────────┘
       ▼                                                                 │
┌─────────────┐     sync      ┌──────────────┐     Git sync              │
│ Developer   │ ────────────► │ Azure DevOps │ ──────────────────────────┘
│ (Fabric UI) │   (optional)  │ main branch  │   Update workspace
└─────────────┘               └──────────────┘
                                      │
                                      ▼
                              pl_realestate_demand_etl
                              (daily schedule → Bronze/Silver/Gold)
                                      │
                                      ▼
                              Power BI report (Direct Lake)
```

| System | Role |
|--------|------|
| **Azure DevOps** | Fabric Git integration — prod/dev workspaces pull from here |
| **GitHub** | Portfolio, backup, local clone — **not** connected to Fabric directly |
| **Fabric pipeline** | Runtime orchestration (not code deployment) |
| **Power BI** | Consumption layer on Gold star schema |

---

## Branch strategy

| Branch | Purpose | Fabric workspace |
|--------|---------|------------------|
| `main` | Stable, production-ready code | Prod (`ws_realestate_pro`) |
| `feature/*` | New work (IPstack, geo, schema changes) | Dev / experiment workspace |

**Rules**

1. Never develop directly on `main` in Fabric for risky changes — use a feature branch + dev workspace.
2. Merge to `main` in **Azure DevOps** when notebooks and pipeline pass in dev.
3. Prod workspace: **Source control → Update** from `main` after merge.
4. Push the same commits to **GitHub** from local for portfolio visibility.

---

## Environments

See [`config/environments.yaml`](../config/environments.yaml).

| Env | Workspace (example) | Lakehouse (example) | IPstack | Data source |
|-----|---------------------|---------------------|---------|-------------|
| dev | `ws_realestate_*_dev` | `lh_realestate_dev` | Mock fixtures | `property_views_5k.csv` |
| prod | `ws_realestate_pro` | `lh_realestate_pro` | Live or mock | CSV until portal API (Phase 2) |

Notebook Cell 0 (or pipeline base parameters) must match the target environment. See [`variable_library.md`](variable_library.md).

---

## Deployment checklist (minimum prod deploy)

### One-time setup

- [ ] Prod workspace created with Fabric capacity assigned
- [ ] Prod workspace Git-connected to **Azure DevOps** → branch `main`
- [ ] Lakehouse `lh_realestate_pro` created and files uploaded:
  - `Files/raw/sample/listings.csv`
  - `Files/raw/sample/property_views_5k.csv` (or real export)
  - `Files/fixtures/ipstack/*.json` (if `MOCK_IPSTACK = True`)
- [ ] Key Vault configured for live IPstack ([`key_vault_live_ipstack.md`](key_vault_live_ipstack.md))
- [ ] Pipeline `pl_realestate_demand_etl` created: **Setup → Bronze → Silver → Gold**
- [ ] **Every notebook activity** in pipeline: Lakehouse = `lh_realestate_pro` (Default)
- [ ] Prod values in notebook Cell 0 (especially `5_silver_loader`)

### First prod run

- [ ] `RUN_SETUP = true` (or run `2_setup` manually once)
- [ ] Pipeline **Run now** — all activities green
- [ ] Validate: `dim_visitor_geo`, `fact_property_view` row counts in `playground.ipynb`

### Go live

- [ ] `RUN_SETUP = false` for daily runs
- [ ] Schedule trigger (e.g. daily 6:00 AM)
- [ ] Publish Power BI report in prod workspace
- [ ] Share workspace with stakeholders (Viewer)
- [ ] Merge feature → `main` in Azure DevOps if not already done
- [ ] Push `main` to GitHub

---

## Pipeline activities (prod)

| Order | Notebook | First run | Daily run |
|-------|----------|-----------|-----------|
| 1 | `2_setup` | Yes (`RUN_SETUP=true`) | Skip |
| 2 | `4_bronze_loader` | Yes | Yes |
| 3 | `5_silver_loader` | Yes | Yes |
| 4 | `6_gold_loader` | Yes | Yes |

Optional: `3_cleanup_old_tables` before Bronze (90-day retention). Skip until core chain is stable.

**Critical:** Each activity must have **Lakehouse = `lh_realestate_pro`**. Manual notebook runs can work while pipeline fails if this is missing on activities.

---

## Code change workflow

### Feature development

1. Create branch `feature/my-change` in Azure DevOps (or locally → push).
2. Connect **dev** Fabric workspace to that branch (or paste notebook changes in Fabric → commit to feature branch).
3. Run notebooks or pipeline in dev; validate Gold + Power BI.
4. Open PR: `feature/my-change` → `main` in Azure DevOps.
5. Merge after review.

### Promote to prod

1. Prod workspace → **Source control → Update** (pull `main`).
2. If schema changed: run with `RUN_SETUP=true` once.
3. Run pipeline manually once; confirm Monitoring hub green.
4. Next scheduled run picks up new code automatically.

### Sync GitHub (portfolio)

From local clone after merge:

```bash
git checkout main
git pull origin main          # or pull from Azure DevOps remote if configured
git push origin main          # GitHub
```

Fabric does **not** read from GitHub — keep DevOps and GitHub in sync manually or via dual remotes.

---

## Parameters

| Approach | When to use |
|----------|-------------|
| **Cell 0 in notebooks** | Simplest for prod — edit once per workspace |
| **Pipeline parameters + base parameters** | One knob for dev/prod without editing notebooks |

Prod Cell 0 minimum:

```python
ENV = "prod"
VIEWS_FILE = "property_views_5k.csv"
LISTINGS_FILE = "listings.csv"
MOCK_IPSTACK = True   # or False for live IPstack
```

Pipeline parameters alone do **not** reach notebooks unless mapped on each activity (`@pipeline().parameters.X`).

---

## Power BI release

1. Semantic model on prod Lakehouse (Direct Lake).
2. After pipeline run: refresh SQL analytics endpoint if new columns added.
3. Edit tables / refresh semantic model schema when `dim_*` columns change.
4. Publish report in `ws_realestate_pro`.
5. Set data categories on `visitor_latitude`, `visitor_longitude`, `suburb_latitude`, `suburb_longitude`.

Report structure: [`powerbi/README.md`](../powerbi/README.md).

---

## Troubleshooting (prod pipeline)

| Symptom | Likely fix |
|---------|------------|
| ADLS Gen2 error in pipeline, manual notebook works | Set Lakehouse on **each** pipeline notebook activity |
| All visitor regions = Victoria | Re-run Silver with fixtures; see `5_silver_loader` cache reset |
| Power BI old data | Refresh report; re-sync semantic model schema |
| Key Vault error in Silver | IAM on `kv-ipstack`; see key vault doc |
| Bronze PATH_NOT_FOUND | Upload CSV to prod Lakehouse `Files/raw/sample/` |

---

## Phase 2 (not CI/CD yet)

- Portal REST API ingest in `4_bronze_loader` (replace CSV)
- Azure Pipelines YAML for automated tests (optional)
- Separate `test` workspace on `main` before prod promotion
- Fabric deployment pipelines (when available in tenant)

---

## Related docs

- [`variable_library.md`](variable_library.md) — pipeline parameter reference
- [`key_vault_live_ipstack.md`](key_vault_live_ipstack.md) — live API secrets
- [`../config/environments.yaml`](../config/environments.yaml) — environment names
- [`../powerbi/README.md`](../powerbi/README.md) — dashboard spec
