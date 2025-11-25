"""
Import all fixtures from API-Football for the 2025-26 season
"""
import asyncio
import httpx
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv('API_FOOTBALL_KEY')
BASE_URL = "https://v3.football.api-sports.io"

# Leagues to import (all 13 leagues)
LEAGUES = {
    39: "Premier League",
    40: "Championship",
    179: "Scottish Premiership",
    140: "La Liga",
    78: "Bundesliga",
    135: "Serie A",
    61: "Ligue 1",
    94: "Primeira Liga",
    88: "Eredivisie",
    203: "Süper Lig",
    253: "MLS",
    71: "Brasileirão",
    239: "Liga BetPlay",
}

SEASON = 2025

async def fetch_fixtures_for_league(league_id: int, league_name: str):
    """Fetch all fixtures for a league"""
    all_fixtures = []
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': API_KEY
        }
        
        params = {
            'league': league_id,
            'season': SEASON
        }
        
        logger.info(f"Fetching fixtures for {league_name}...")
        
        try:
            response = await client.get(
                f"{BASE_URL}/fixtures",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            fixtures = data.get('response', [])
            
            logger.info(f"  Retrieved {len(fixtures)} fixtures")
            return fixtures
            
        except Exception as e:
            logger.error(f"  Error fetching {league_name}: {e}")
            return []

def transform_fixture(fixture, league_id, league_name):
    """Transform API-Football format to database format"""
    try:
        fixture_data = fixture.get('fixture', {})
        league_data = fixture.get('league', {})
        teams_data = fixture.get('teams', {})
        goals_data = fixture.get('goals', {})
        
        # Parse date
        date_str = fixture_data.get('date')
        if date_str:
            try:
                utc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                utc_date = datetime.utcnow()
        else:
            utc_date = datetime.utcnow()
        
        # Determine status
        status_short = fixture_data.get('status', {}).get('short', 'NS')
        if status_short in ['FT', 'AET', 'PEN']:
            status = 'FINISHED'
        elif status_short in ['1H', '2H', 'HT', 'ET', 'BT', 'P', 'LIVE']:
            status = 'LIVE'
        else:
            status = 'SCHEDULED'
        
        # Build score
        score = None
        if goals_data.get('home') is not None and goals_data.get('away') is not None:
            score = {
                'home': goals_data.get('home'),
                'away': goals_data.get('away')
            }
        
        return {
            'fixture_id': fixture_data.get('id'),
            'league_id': league_id,
            'league_name': league_name,
            'home_team': teams_data.get('home', {}).get('name'),
            'away_team': teams_data.get('away', {}).get('name'),
            'home_logo': teams_data.get('home', {}).get('logo'),
            'away_logo': teams_data.get('away', {}).get('logo'),
            'utc_date': utc_date,
            'status': status,
            'matchday': league_data.get('round', 'Unknown'),
            'score': score
        }
        
    except Exception as e:
        logger.error(f"Error transforming fixture: {e}")
        return None

async def main():
    print("=" * 80)
    print("API-FOOTBALL BULK IMPORT - 2025-26 SEASON")
    print("=" * 80)
    
    if not API_KEY:
        print("\n❌ ERROR: API_FOOTBALL_KEY not found")
        return
    
    print(f"\n✅ API Key found: {API_KEY[:20]}...")
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    print(f"✅ Connected to database: {os.getenv('DB_NAME')}")
    
    # Clear existing fixtures
    print("\n🗑️  Clearing existing fixtures...")
    db.fixtures.delete_many({})
    print("✅ Database cleared")
    
    total_imported = 0
    
    for league_id, league_name in LEAGUES.items():
        print(f"\n{'='*80}")
        print(f"📋 {league_name} (ID: {league_id})")
        print('='*80)
        
        try:
            # Fetch fixtures
            fixtures = await fetch_fixtures_for_league(league_id, league_name)
            
            if not fixtures:
                print(f"  ⚠️  No fixtures found")
                continue
            
            # Transform and save
            saved = 0
            finished = 0
            scheduled = 0
            
            for fixture in fixtures:
                transformed = transform_fixture(fixture, league_id, league_name)
                if transformed:
                    db.fixtures.update_one(
                        {'fixture_id': transformed['fixture_id']},
                        {'$set': transformed},
                        upsert=True
                    )
                    saved += 1
                    
                    if transformed['status'] == 'FINISHED':
                        finished += 1
                    elif transformed['status'] == 'SCHEDULED':
                        scheduled += 1
            
            print(f"  ✅ Saved {saved} fixtures ({finished} finished, {scheduled} scheduled)")
            total_imported += saved
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"\nTotal fixtures imported: {total_imported}")
    
    print("\n📊 Breakdown by league:")
    for league_id, league_name in LEAGUES.items():
        count = db.fixtures.count_documents({'league_id': league_id})
        finished = db.fixtures.count_documents({'league_id': league_id, 'status': 'FINISHED'})
        scheduled = db.fixtures.count_documents({'league_id': league_id, 'status': 'SCHEDULED'})
        print(f"  {league_name}: {count} total ({finished} finished, {scheduled} scheduled)")
    
    print("\n✅ ALL DONE! Your app now has real fixture data from API-Football.")
    print(f"📊 API requests used: ~{len(LEAGUES)} (well within your 100/day limit)")

if __name__ == "__main__":
    asyncio.run(main())
