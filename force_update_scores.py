#!/usr/bin/env python3
"""
Force update scores for Dec 2-4 Premier League matches
Run this if production is not showing scores
"""
import requests
import os
from pymongo import MongoClient
from datetime import datetime

API_KEY = os.getenv('API_FOOTBALL_KEY', 'edd455f6352f2079c15983bca9af94cf')
API_HOST = 'v3.football.api-sports.io'
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': API_HOST}

print("=" * 60)
print("FORCE UPDATE PREMIER LEAGUE SCORES - DEC 2-4, 2025")
print("=" * 60)

updated_count = 0

for date_str in ['2025-12-02', '2025-12-03', '2025-12-04']:
    print(f"\n📅 Fetching {date_str} results...")
    
    response = requests.get(
        f'https://{API_HOST}/fixtures',
        headers=headers,
        params={'league': 39, 'date': date_str, 'season': 2025},
        timeout=30
    )
    
    if response.status_code == 200:
        fixtures = response.json().get('response', [])
        print(f"   Found {len(fixtures)} fixtures from API")
        
        for f in fixtures:
            fixture = f['fixture']
            teams = f['teams']
            score = f['score']
            
            if fixture['status']['short'] in ['FT', 'AET', 'PEN']:
                h_score = score['fulltime']['home']
                a_score = score['fulltime']['away']
                
                # Update with INTEGER fixture_id
                result = db.fixtures.update_one(
                    {'fixture_id': fixture['id']},
                    {'$set': {
                        'status': 'FINISHED',
                        'score': {'home': h_score, 'away': a_score},
                        'home_score': h_score,
                        'away_score': a_score
                    }}
                )
                
                if result.modified_count > 0:
                    print(f"   ✅ {teams['home']['name']} {h_score}-{a_score} {teams['away']['name']}")
                    updated_count += 1
                elif result.matched_count > 0:
                    print(f"   ℹ️  {teams['home']['name']} vs {teams['away']['name']} (already updated)")
                else:
                    print(f"   ⚠️  {teams['home']['name']} vs {teams['away']['name']} (not found in DB)")

print(f"\n{'='*60}")
print(f"✅ COMPLETE - Updated {updated_count} fixtures")
print(f"{'='*60}")

# Verify
verified = db.fixtures.count_documents({
    'league_id': 39,
    'utc_date': {'$gte': datetime(2025, 12, 2), '$lte': datetime(2025, 12, 4)},
    'status': 'FINISHED',
    'score.home': {'$ne': None}
})

print(f"\n📊 Verification:")
print(f"   Premier League Dec 2-4 with scores: {verified}")
