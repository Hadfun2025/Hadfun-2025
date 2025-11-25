"""
Load all fixtures for international competitions (past, present, future)
This script loads comprehensive fixture data for:
- UEFA Champions League, Europa League, Conference League
- UEFA Nations League
- World Cup 2026 and UEFA Qualifiers
- Euro 2024 and Qualifiers
"""
import asyncio
import httpx
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv('API_FOOTBALL_KEY')
BASE_URL = "https://v3.football.api-sports.io"

# International competitions with their seasons (2025/26)
# Only including competitions that actually work in API-Football
INTERNATIONAL_LEAGUES = {
    # European Club Competitions (2025/26 season)
    2: {"name": "UEFA Champions League", "season": 2025},
    3: {"name": "UEFA Europa League", "season": 2025},
    848: {"name": "UEFA Conference League", "season": 2025},
}

async def load_all_fixtures_for_league(http_client, headers, league_id, league_info, db):
    """Load all fixtures for a specific league and season"""
    league_name = league_info['name']
    season = league_info['season']
    
    logger.info(f"📥 Loading fixtures for {league_name} (Season {season})...")
    
    try:
        params = {
            'league': league_id,
            'season': season
        }
        
        response = await http_client.get(
            f"{BASE_URL}/fixtures",
            headers=headers,
            params=params,
            timeout=60.0
        )
        response.raise_for_status()
        
        data = response.json()
        fixtures = data.get('response', [])
        
        if not fixtures:
            logger.warning(f"   ⚠️  No fixtures found for {league_name}")
            return 0
        
        loaded_count = 0
        for fixture in fixtures:
            fixture_data = fixture.get('fixture', {})
            teams_data = fixture.get('teams', {})
            goals_data = fixture.get('goals', {})
            league_data = fixture.get('league', {})
            score_data = fixture.get('score', {})
            
            # Parse date
            date_str = fixture_data.get('date')
            if date_str:
                utc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            else:
                continue
            
            # Determine status
            status_short = fixture_data.get('status', {}).get('short', 'NS')
            if status_short in ['FT', 'AET', 'PEN']:
                status = 'FINISHED'
            elif status_short in ['1H', '2H', 'HT', 'ET', 'BT', 'P', 'LIVE']:
                status = 'LIVE'
            elif status_short in ['CANC', 'ABD', 'PST', 'SUSP']:
                status = 'CANCELLED'
            else:
                status = 'SCHEDULED'
            
            # Build fixture document
            fixture_doc = {
                'fixture_id': fixture_data.get('id'),
                'league_id': league_id,
                'league_name': league_name,
                'season': season,
                'round': league_data.get('round', 'Unknown'),
                'utc_date': utc_date,
                'status': status,
                'home_team': teams_data.get('home', {}).get('name'),
                'away_team': teams_data.get('away', {}).get('name'),
                'home_team_id': teams_data.get('home', {}).get('id'),
                'away_team_id': teams_data.get('away', {}).get('id'),
                'home_logo': teams_data.get('home', {}).get('logo'),
                'away_logo': teams_data.get('away', {}).get('logo'),
                'venue': fixture_data.get('venue', {}).get('name'),
                'city': fixture_data.get('venue', {}).get('city'),
                'score': {
                    'home': goals_data.get('home'),
                    'away': goals_data.get('away')
                },
                'halftime_score': {
                    'home': score_data.get('halftime', {}).get('home'),
                    'away': score_data.get('halftime', {}).get('away')
                },
                'fulltime_score': {
                    'home': score_data.get('fulltime', {}).get('home'),
                    'away': score_data.get('fulltime', {}).get('away')
                },
                'updated_at': datetime.utcnow()
            }
            
            # Insert or update
            db.fixtures.update_one(
                {"fixture_id": fixture_doc['fixture_id']},
                {"$set": fixture_doc},
                upsert=True
            )
            loaded_count += 1
        
        logger.info(f"   ✅ Loaded {loaded_count} fixtures for {league_name}")
        return loaded_count
        
    except Exception as e:
        logger.error(f"   ❌ Error loading {league_name}: {str(e)}")
        return 0

async def main():
    """Main function to load all international fixtures"""
    logger.info("=" * 60)
    logger.info("🌍 LOADING INTERNATIONAL COMPETITION FIXTURES")
    logger.info("=" * 60)
    
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    total_loaded = 0
    
    async with httpx.AsyncClient(timeout=120.0) as http_client:
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': API_KEY
        }
        
        for league_id, league_info in INTERNATIONAL_LEAGUES.items():
            count = await load_all_fixtures_for_league(
                http_client, headers, league_id, league_info, db
            )
            total_loaded += count
            # Small delay to avoid rate limiting
            await asyncio.sleep(1)
    
    logger.info("=" * 60)
    logger.info(f"🎉 COMPLETE! Total fixtures loaded: {total_loaded}")
    logger.info("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
