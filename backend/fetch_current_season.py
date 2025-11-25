"""
Fetch all fixtures from current 2025-26 season using Sportmonks API
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

API_TOKEN = os.getenv('SPORTMONKS_API_TOKEN')
BASE_URL = 'https://api.sportmonks.com/v3/football'

# League mappings
LEAGUES = {
    'Premier League': {'sportmonks_id': 8, 'api_football_id': 39},
    'La Liga': {'sportmonks_id': 564, 'api_football_id': 140},
    'Bundesliga': {'sportmonks_id': 82, 'api_football_id': 78},
    'Serie A': {'sportmonks_id': 384, 'api_football_id': 135},
    'Ligue 1': {'sportmonks_id': 301, 'api_football_id': 61},
}

async def get_current_season_id(league_id: int):
    """Get the current season ID for a league"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        endpoint = f"{BASE_URL}/leagues/{league_id}/seasons"
        params = {"api_token": API_TOKEN}
        
        response = await client.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Find 2025-26 season
        seasons = data.get('data', [])
        for season in seasons:
            name = season.get('name', '')
            if '2025' in name or '2026' in name:
                logger.info(f"Found season: {name} (ID: {season.get('id')})")
                return season.get('id')
        
        # If not found, use the latest season
        if seasons:
            latest = seasons[0]
            logger.info(f"Using latest season: {latest.get('name')} (ID: {latest.get('id')})")
            return latest.get('id')
        
        return None

async def get_fixtures_by_season(league_id: int, season_id: int):
    """Get all fixtures for a season"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        endpoint = f"{BASE_URL}/fixtures"
        params = {
            "api_token": API_TOKEN,
            "filters": f"fixtureLeagues:{league_id};fixtureSeasons:{season_id}",
            "include": "scores;participants"
        }
        
        response = await client.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get('data', [])

def transform_fixture(fixture, league_name, api_football_league_id):
    """Transform Sportmonks fixture to our format"""
    try:
        # Get participants
        participants = fixture.get('participants', [])
        home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), participants[0] if participants else {})
        away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), participants[1] if len(participants) > 1 else {})
        
        # Get scores
        scores = fixture.get('scores', [])
        home_score = None
        away_score = None
        
        for score in scores:
            if score.get('description') == 'CURRENT':
                participant_id = score.get('participant_id')
                score_value = score.get('score', {}).get('goals')
                
                if participant_id == home_team.get('id'):
                    home_score = score_value
                elif participant_id == away_team.get('id'):
                    away_score = score_value
        
        # Status
        state_id = fixture.get('state_id', 1)
        if state_id == 5:
            status = 'FINISHED'
        elif state_id in [3, 4]:
            status = 'LIVE'
        else:
            status = 'SCHEDULED'
        
        # Date
        date_str = fixture.get('starting_at')
        if date_str:
            utc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
        else:
            utc_date = datetime.utcnow()
        
        # Round/matchday
        round_info = fixture.get('round', {})
        round_name = round_info.get('name', 'Unknown') if isinstance(round_info, dict) else str(round_info)
        
        return {
            'fixture_id': fixture.get('id'),
            'league_id': api_football_league_id,
            'league_name': league_name,
            'home_team': home_team.get('name'),
            'away_team': away_team.get('name'),
            'home_logo': home_team.get('image_path'),
            'away_logo': away_team.get('image_path'),
            'utc_date': utc_date,
            'status': status,
            'matchday': round_name,
            'score': {'home': home_score, 'away': away_score} if home_score is not None and away_score is not None else None
        }
    except Exception as e:
        logger.error(f"Error transforming fixture: {e}")
        return None

async def main():
    print("=" * 70)
    print("FETCHING CURRENT 2025-26 SEASON FIXTURES FROM SPORTMONKS")
    print("=" * 70)
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    total_imported = 0
    
    for league_name, league_info in LEAGUES.items():
        print(f"\n📋 Processing {league_name}...")
        
        try:
            # Get current season ID
            season_id = await get_current_season_id(league_info['sportmonks_id'])
            if not season_id:
                print(f"   ❌ Could not find season ID")
                continue
            
            print(f"   ✅ Season ID: {season_id}")
            
            # Get fixtures
            print(f"   📥 Fetching fixtures...")
            fixtures = await get_fixtures_by_season(league_info['sportmonks_id'], season_id)
            print(f"   ✅ Found {len(fixtures)} fixtures")
            
            # Transform and save
            saved = 0
            for fixture in fixtures:
                transformed = transform_fixture(fixture, league_name, league_info['api_football_id'])
                if transformed:
                    db.fixtures.update_one(
                        {'fixture_id': transformed['fixture_id']},
                        {'$set': transformed},
                        upsert=True
                    )
                    saved += 1
            
            print(f"   ✅ Saved {saved} fixtures to database")
            total_imported += saved
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total fixtures imported: {total_imported}")
    
    # Count by league
    print("\nFixtures by league:")
    for league_name, league_info in LEAGUES.items():
        count = db.fixtures.count_documents({'league_id': league_info['api_football_id']})
        print(f"  {league_name}: {count}")
    
    print("\n✅ COMPLETE!")

if __name__ == "__main__":
    asyncio.run(main())
