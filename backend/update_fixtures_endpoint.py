"""
Standalone script to update fixtures - can be called via API endpoint or externally
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
    # European Competitions (Working)
    2: "UEFA Champions League",
    3: "UEFA Europa League",
    848: "UEFA Conference League",
}

# Different seasons for different competitions
LEAGUE_SEASONS = {
    1: 2026,      # World Cup 2026
    387: 2024,    # Euro 2024
    960: 2024,    # Euro 2024 Qualifiers
}

SEASON = 2025

async def update_fixtures():
    """Update only recent fixtures (last 7 days) to save API calls"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    updated_count = 0
    
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': API_KEY
        }
        
        # Only update fixtures from last 7 days (to catch score updates)
        from datetime import timedelta
        date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        date_to = datetime.now().strftime('%Y-%m-%d')
        
        for league_id, league_name in LEAGUES.items():
            logger.info(f"Updating {league_name}...")
            
            # Use specific season for some leagues, default to SEASON for others
            league_season = LEAGUE_SEASONS.get(league_id, SEASON)
            
            try:
                params = {
                    'league': league_id,
                    'season': league_season,
                    'from': date_from,
                    'to': date_to
                }
                
                response = await http_client.get(
                    f"{BASE_URL}/fixtures",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                fixtures = data.get('response', [])
                
                # Update each fixture
                for fixture in fixtures:
                    fixture_data = fixture.get('fixture', {})
                    teams_data = fixture.get('teams', {})
                    goals_data = fixture.get('goals', {})
                    league_data = fixture.get('league', {})
                    
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
                    else:
                        status = 'SCHEDULED'
                    
                    # Build update
                    update_data = {
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
                        'score': None
                    }
                    
                    # Add score if available
                    if goals_data.get('home') is not None and goals_data.get('away') is not None:
                        update_data['score'] = {
                            'home': goals_data.get('home'),
                            'away': goals_data.get('away')
                        }
                    
                    # Upsert to database
                    db.fixtures.update_one(
                        {'fixture_id': update_data['fixture_id']},
                        {'$set': update_data},
                        upsert=True
                    )
                    updated_count += 1
                
                logger.info(f"  Updated {len(fixtures)} fixtures")
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"  Error: {e}")
    
    return updated_count

async def main():
    logger.info("Starting fixture update...")
    count = await update_fixtures()
    logger.info(f"✅ Updated {count} fixtures")
    return count

if __name__ == "__main__":
    asyncio.run(main())
