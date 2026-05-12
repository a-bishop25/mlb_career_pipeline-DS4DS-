"""
Test Script for MLB Career Longevity Predictor
===============================================
Verifies the live prediction API is working end-to-end.
Sends a player lookup request and a direct prediction request,
prints results to terminal, and exits 0 on success.

Requirements: pip install requests

Usage: python test_project.py
"""

import requests
import sys

API_URL = "http://100.54.195.185:8000"

print("=" * 50)
print("MLB Career Longevity Predictor — API Test")
print("=" * 50)

# ── Test 1: Health Check ──────────────────────────
print("\n[1/3] Health check...")
try:
    resp = requests.get(f"{API_URL}/", timeout=30)
    if resp.status_code != 200:
        print(f"FAIL: Health check returned {resp.status_code}")
        sys.exit(1)
    print(f"PASS: {resp.json()['status']}")
except Exception as e:
    print(f"FAIL: Could not reach API — {e}")
    sys.exit(1)

# ── Test 2: Player Lookup ─────────────────────────
print("\n[2/3] Player lookup (Mike Trout)...")
try:
    resp = requests.get(f"{API_URL}/player/mike/trout", timeout=30)
    if resp.status_code != 200:
        print(f"FAIL: Player lookup returned {resp.status_code}")
        sys.exit(1)
    data = resp.json()
    print(f"PASS: Found {data['nameFirst'].title()} {data['nameLast'].title()}")
    print(f"      Seasons in dataset : {data['seasons_played']}")
    print(f"      Last recorded season: {data['latest_season']}")
    print(f"      Predicted years left: {data['prediction']}")
    print(f"      Estimated final year: {data['estimated_final_season']}")
except Exception as e:
    print(f"FAIL: Player lookup failed — {e}")
    sys.exit(1)

# ── Test 3: Direct Prediction ─────────────────────
print("\n[3/3] Direct prediction endpoint...")
payload = {
    "age": 27,
    "wOBA": 0.370,
    "lag_wOBA": 0.360,
    "lag_PA": 550,
    "career_PA": 3000,
    "career_G": 750,
    "years_in_league": 4,
    "total_injuries": 0,
    "avg_severity": 0.0,
    "career_injuries": 1,
    "career_severity": 2.0,
    "missed_prev_year": 0
}
try:
    resp = requests.post(f"{API_URL}/predict", json=payload, timeout=30)
    if resp.status_code != 200:
        print(f"FAIL: Prediction returned {resp.status_code}")
        sys.exit(1)
    result = resp.json()
    print(f"PASS: Prediction received")
    print(f"      Predicted years remaining: {result['prediction']}")
    print(f"      Estimated final season   : {result['estimated_final_season']}")
except Exception as e:
    print(f"FAIL: Prediction request failed — {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("ALL TESTS PASSED")
print("=" * 50)
sys.exit(0)
