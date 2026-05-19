#!/usr/bin/env python3
"""Regenerate data/sample/*.csv and data/fixtures/ipstack/*.json"""
import json, csv, uuid, random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
random.seed(42)

IP_PROFILES = {
    "203.0.113.10": {"country_code": "AU", "country_name": "Australia", "region": "Victoria", "city": "Melbourne", "lat": -37.81, "lon": 144.96, "tz": "Australia/Melbourne", "currency": "AUD", "isp": "Telstra", "org": "Telstra", "vpn": False, "proxy": False},
    "203.0.113.11": {"country_code": "AU", "country_name": "Australia", "region": "NSW", "city": "Sydney", "lat": -33.87, "lon": 151.21, "tz": "Australia/Sydney", "currency": "AUD", "isp": "Optus", "org": "Optus", "vpn": False, "proxy": False},
    "8.8.8.8": {"country_code": "US", "country_name": "United States", "region": "California", "city": "Mountain View", "lat": 37.39, "lon": -122.08, "tz": "America/Los_Angeles", "currency": "USD", "isp": "Google", "org": "Google", "vpn": False, "proxy": False},
    "1.1.1.1": {"country_code": "US", "country_name": "United States", "region": "California", "city": "Los Angeles", "lat": 34.05, "lon": -118.24, "tz": "America/Los_Angeles", "currency": "USD", "isp": "Cloudflare", "org": "APNIC", "vpn": False, "proxy": False},
    "165.21.186.1": {"country_code": "SG", "country_name": "Singapore", "region": "Singapore", "city": "Singapore", "lat": 1.35, "lon": 103.82, "tz": "Asia/Singapore", "currency": "SGD", "isp": "Singtel", "org": "Singtel", "vpn": False, "proxy": False},
    "185.220.101.50": {"country_code": "DE", "country_name": "Germany", "region": "Berlin", "city": "Berlin", "lat": 52.52, "lon": 13.40, "tz": "Europe/Berlin", "currency": "EUR", "isp": "VPN Provider", "org": "Privacy GmbH", "vpn": True, "proxy": True},
}
for i in range(10, 30):
    ip = f"192.0.2.{i}"
    cc, cn = [("AU", "Australia"), ("US", "United States"), ("SG", "Singapore"), ("GB", "United Kingdom")][i % 4]
    IP_PROFILES[ip] = {"country_code": cc, "country_name": cn, "region": "R", "city": "C", "lat": float(i), "lon": float(i), "tz": "UTC", "currency": "USD", "isp": f"I{i}", "org": f"O{i}", "vpn": False, "proxy": False}

def payload(ip, p):
    return {"ip": ip, "country_code": p["country_code"], "country_name": p["country_name"], "region_name": p["region"], "city": p["city"], "latitude": p["lat"], "longitude": p["lon"], "time_zone": {"id": p["tz"]}, "currency": {"code": p["currency"]}, "connection": {"isp": p["isp"], "org": p["org"]}, "security": {"is_proxy": p["proxy"], "proxy_type": "vpn" if p["vpn"] else None, "threat_level": "high" if p["vpn"] else "low"}}

fix = ROOT / "data/fixtures/ipstack"
fix.mkdir(parents=True, exist_ok=True)
for ip, p in IP_PROFILES.items():
    (fix / f"{ip}.json").write_text(json.dumps(payload(ip, p), indent=2))

def gen_events(n):
    ips = list(IP_PROFILES.keys())
    rows, base = [], datetime(2026, 4, 20, 10, 0, 0)
    for i in range(n):
        if i < 25:
            sess, ip = "sess-velocity-001", "185.220.101.50"
            ts = base + timedelta(minutes=i % 55)
        else:
            sess, ip = f"sess-{i%40:04d}", ips[i % len(ips)]
            ts = base + timedelta(days=i % 25, hours=i % 23)
        et = random.choice(["login", "purchase", "page_view", "session_start"])
        user = "user-whale-001" if i % 31 == 0 else f"user-{i%50:04d}"
        amt = round(230.0 if user == "user-whale-001" and et == "purchase" else random.uniform(5, 120), 2) if et == "purchase" else ""
        rows.append({"event_id": str(uuid.uuid4()), "session_id": sess, "event_ts": ts.strftime("%Y-%m-%dT%H:%M:%S"), "event_type": et, "user_id": user, "ip": ip, "user_agent": "Mozilla/iPhone" if i%3==0 else "Mozilla/Windows", "amount": amt})
    return rows

def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["event_id","session_id","event_ts","event_type","user_id","ip","user_agent","amount"])
        w.writeheader(); w.writerows(rows)

(ROOT/"data/sample").mkdir(parents=True, exist_ok=True)
write_csv(ROOT/"data/sample/events_100.csv", gen_events(100))
write_csv(ROOT/"data/sample/events_5k.csv", gen_events(5000))
print("Regenerated sample data")
