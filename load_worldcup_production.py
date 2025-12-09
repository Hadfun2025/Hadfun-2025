#!/usr/bin/env python3
"""
Load World Cup 2026 data into production database
Run this script after deployment to populate World Cup groups and fixtures
"""

import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# Your API key
API_KEY = "edd455f6352f2079c15983bca9af94cf"

async def load_worldcup_data():
    """Load World Cup 2026 groups and fixtures into production"""
    
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("=" * 60)
    print("LOADING WORLD CUP 2026 DATA INTO PRODUCTION")
    print("=" * 60)
    
    # Step 1: Load World Cup fixtures from API
    print("\n📥 Step 1: Loading World Cup 2026 fixtures from API...")
    
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "league": 1,  # World Cup
        "season": 2026,
        "timezone": "Europe/London"
    }
    headers = {"x-apisports-key": API_KEY}
    
    fixtures_loaded = 0
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                fixtures = data.get('response', [])
                
                print(f"   Found {len(fixtures)} World Cup fixtures from API")
                
                for api_fixture in fixtures:
                    fixture_id = api_fixture['fixture']['id']
                    
                    # Transform
                    fixture_date_str = api_fixture['fixture']['date']
                    fixture_date = datetime.fromisoformat(fixture_date_str.replace('Z', '+00:00'))
                    
                    fixture = {
                        "fixture_id": fixture_id,
                        "home_team": api_fixture['teams']['home']['name'],
                        "away_team": api_fixture['teams']['away']['name'],
                        "home_logo": api_fixture['teams']['home']['logo'],
                        "away_logo": api_fixture['teams']['away']['logo'],
                        "league_id": 1,
                        "league_name": "World Cup 2026",
                        "status": "SCHEDULED",
                        "utc_date": fixture_date.replace(tzinfo=None),
                        "matchday": str(api_fixture['league']['round']),
                        "home_score": None,
                        "away_score": None
                    }
                    
                    await db.fixtures.update_one(
                        {"fixture_id": fixture_id},
                        {"$set": fixture},
                        upsert=True
                    )
                    fixtures_loaded += 1
                
                print(f"   ✅ Loaded {fixtures_loaded} World Cup fixtures")
            else:
                print(f"   ❌ API error: {response.status}")
                return
    
    # Step 2: Verify groups are loaded
    print("\n📋 Step 2: Checking World Cup 2026 groups...")
    
    groups = await db.world_cup_groups.find({}).to_list(100)
    print(f"   Found {len(groups)} groups in database")
    
    if len(groups) == 12:
        print("   ✅ All 12 groups present (A-L)")
    else:
        print(f"   ⚠️  Only {len(groups)} groups found, expected 12")
        print("   Note: Groups should have been migrated during deployment")
    
    # Step 3: Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ World Cup Fixtures: {fixtures_loaded} loaded")
    print(f"✅ World Cup Groups: {len(groups)} in database")
    print("\nWorld Cup 2026 data is now available in production!")
    print("Users can now view groups and make predictions on matches.")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(load_worldcup_data())
