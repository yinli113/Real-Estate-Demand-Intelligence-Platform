#!/usr/bin/env python3
"""Generate notebooks, cursor rules, README, fabric docs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def nb(*cell_sources):
    cells = []
    for src in cell_sources:
        if isinstance(src, str):
            lines = [ln + "\n" for ln in src.split("\n")]
            if lines and lines[-1] == "\n":
                pass
            else:
                if lines and not lines[-1].endswith("\n"):
                    lines[-1] += "\n"
        else:
            lines = src
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": lines if isinstance(lines, list) else [src],
        })
    return {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "cells": cells,
    }

def save_nb(name, *cells):
    path = ROOT / "notebooks" / name
    path.write_text(json.dumps(nb(*cells), indent=1), encoding="utf-8")

# --- 1_config ---
save_nb("1_config.ipynb", r'''"""
Central configuration for Geo Risk Intelligence Pipeline.
"""
import os
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

# Widgets / pipeline parameters (Databricks + Fabric)
try:
    dbutils.widgets.dropdown("ENV", "dev", ["dev", "test", "prod"], "Environment")
    dbutils.widgets.text("LAKEHOUSE", "", "Lakehouse name (optional override)")
    dbutils.widgets.dropdown("MOCK_IPSTACK", "true", ["true", "false"], "Mock IPstack")
    dbutils.widgets.text("LOOKBACK_DAYS", "30", "Lookback days")
    dbutils.widgets.text("SOURCE_FILE", "events_100.csv", "Source CSV file")
    os.environ["ENV"] = dbutils.widgets.get("ENV").strip().lower()
    if dbutils.widgets.get("LAKEHOUSE").strip():
        os.environ["LAKEHOUSE"] = dbutils.widgets.get("LAKEHOUSE").strip()
    os.environ["MOCK_IPSTACK"] = dbutils.widgets.get("MOCK_IPSTACK").strip().lower()
    os.environ["LOOKBACK_DAYS"] = dbutils.widgets.get("LOOKBACK_DAYS").strip()
    os.environ["SOURCE_FILE"] = dbutils.widgets.get("SOURCE_FILE").strip()
except NameError:
    pass

def _load_env_yaml():
    if yaml is None:
        return {}
    cfg_path = Path("config/environments.yaml")
    if not cfg_path.exists():
        cfg_path = Path("/Workspace/Repos/geo-risk/config/environments.yaml")
    if cfg_path.exists():
        with open(cfg_path) as f:
            return yaml.safe_load(f) or {}
    return {}

_ENV_CFG = _load_env_yaml()

class Config:
    def __init__(self, env=None, lakehouse=None, mock_ipstack=None, lookback_days=None, source_file=None):
        self.env = (env or os.getenv("ENV") or "dev").strip().lower()
        ec = _ENV_CFG.get(self.env, {})
        self.lakehouse = (lakehouse or os.getenv("LAKEHOUSE") or ec.get("lakehouse") or f"lh_geo_risk_{self.env}").strip()
        self.schema = ec.get("schema", "geo")
        self.mock_ipstack = str(mock_ipstack if mock_ipstack is not None else os.getenv("MOCK_IPSTACK", ec.get("mock_ipstack", True))).lower() == "true"
        self.lookback_days = int(lookback_days or os.getenv("LOOKBACK_DAYS") or ec.get("lookback_days", 30))
        self.source_file = (source_file or os.getenv("SOURCE_FILE") or ec.get("source_file") or "events_100.csv").strip()
        self.files_base = f"/lakehouse/{self.lakehouse}/Files"
        self.raw_path = f"{self.files_base}/raw/sample/{self.source_file}"
        self.fixture_base = f"{self.files_base}/fixtures/ipstack"
        self.bronze_events = "bronze_events"
        self.bronze_ipstack_raw = "bronze_ipstack_raw"
        self.bronze_ipstack_errors = "bronze_ipstack_errors"
        self.silver_ip_dim = "silver_ip_dim"
        self.silver_events_enriched = "silver_events_enriched"
        self.gold_geo_traffic_daily = "gold_geo_traffic_daily"
        self.gold_fraud_signals = "gold_fraud_signals"
        self.gold_customer_features = "gold_customer_features"

    def table_fqn(self, table: str) -> str:
        return f"{self.lakehouse}.{self.schema}.{table}"

conf = Config()

from pyspark.sql import SparkSession
spark = SparkSession.getActiveSession() or SparkSession.builder.getOrCreate()
print(f"Config env={conf.env} lakehouse={conf.lakehouse} mock={conf.mock_ipstack} lookback={conf.lookback_days}")
''')

print("1_config done")
