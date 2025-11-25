"""
Fetch upcoming fixtures for next 2 months
"""
import asyncio
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from api_football_service import APIFootballService
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Supported leagues
LEAGUES = {
    39: "Premier League",
    140: "La Liga",
    78: "Bundesliga",
    135: "Serie A",
    61: "Ligue 1",
}

async def fetch_upcoming():
    """Fetch upcoming fixtures"""
    service = APIFootballService()
    client = MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    # Get next 60 days of fixtures
    today = datetime.now()
    end_date = today + timedelta(days=60)
    
    total_saved = 0
    
    for league_id, league_name in LEAGUES.items():
        try:
            logger.info(f"\nFetching upcoming fixtures for {league_name}...")
            
            # Get fixtures for this league
            fixtures = await service.get_fixtures_by_league(league_id, season=2025)
            
            if fixtures:
                logger.info(f"  Found {len(fixtures)} total fixtures")
                
                upcoming_count = 0
                for fixture in fixtures:
                    fixture_data = fixture.get('fixture', {})
                    teams = fixture.get('teams', {})
                    goals = fixture.get('goals', {})
                    league_info = fixture.get('league', {})
                    
                    # Parse date
                    date_str = fixture_data.get('date', '')
                    try:
                        utc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        utc_date = utc_date.replace(tzinfo=None)
                    except:
                        continue
                    
                    # Only save upcoming fixtures within our range
                    if utc_date < today or utc_date > end_date:
                        continue
                    
                    # Determine status
                    status = fixture_data.get('status', {}).get('long', 'SCHEDULED')
                    if status in ['Match Finished', 'FINISHED', 'FT']:
                        status = 'FINISHED'
                    elif status in ['In Play', 'LIVE', '1H', '2H', 'HT']:
                        status = 'LIVE'
                    else:
                        status = 'SCHEDULED'
                    
                    # Build fixture document
                    fixture_doc = {
                        'fixture_id': fixture_data.get('id'),
                        'league_id': league_id,
                        'league_name': league_name,
                        'home_team': teams.get('home', {}).get('name', ''),
                        'away_team': teams.get('away', {}).get('name', ''),
                        'home_logo': teams.get('home', {}).get('logo'),
                        'away_logo': teams.get('away', {}).get('logo'),
                        'utc_date': utc_date,
                        'status': status,
                        'matchday': f"Regular Season - {league_info.get('round', '')}",
                        'score': {
                            'home': goals.get('home'),
                            'away': goals.get('away')
                        } if goals.get('home') is not None else None
                    }
                    
                    # Upsert to database
                    db.fixtures.update_one(
                        {'fixture_id': fixture_doc['fixture_id']},
                        {'$set': fixture_doc},
                        upsert=True
                    )
                    
                    upcoming_count += 1
                    total_saved += 1
                    
                logger.info(f"  ✅ Saved {upcoming_count} upcoming fixtures")
                    
        except Exception as e:
            logger.error(f"  ❌ Error fetching {league_name}: {e}")
        
        # Rate limiting
        await asyncio.sleep(1)
    
    logger.info(f"\n✅ Total upcoming fixtures saved: {total_saved}")
    client.close()

if __name__ == '__main__':
    asyncio.run(fetch_upcoming())
