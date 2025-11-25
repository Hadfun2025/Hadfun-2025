"""
Fetch missing fixtures from Nov 22-24, 2025
"""
import asyncio
import os
from datetime import datetime
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
    40: "Championship",
    179: "Scottish Premiership",
    94: "Primeira Liga",
    88: "Eredivisie",
}

async def fetch_and_save_fixtures():
    """Fetch fixtures for Nov 22-24"""
    service = APIFootballService()
    client = MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    dates = ['2025-11-22', '2025-11-23', '2025-11-24']
    total_saved = 0
    
    for date in dates:
        logger.info(f"\n=== Fetching fixtures for {date} ===")
        
        for league_id, league_name in LEAGUES.items():
            try:
                logger.info(f"  Fetching {league_name}...")
                fixtures = await service.get_fixtures_by_date(date, league_id, season=2025)
                
                if fixtures:
                    logger.info(f"    Found {len(fixtures)} fixtures")
                    
                    for fixture in fixtures:
                        # Transform to database format
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
                            utc_date = datetime.strptime(date, '%Y-%m-%d')
                        
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
                        
                        logger.info(f"      ✅ {fixture_doc['home_team']} vs {fixture_doc['away_team']} - {status}")
                        total_saved += 1
                        
                else:
                    logger.info(f"    No fixtures found")
                    
            except Exception as e:
                logger.error(f"    ❌ Error: {e}")
            
            # Rate limiting
            await asyncio.sleep(0.5)
    
    logger.info(f"\n✅ Total fixtures saved: {total_saved}")
    client.close()

if __name__ == '__main__':
    asyncio.run(fetch_and_save_fixtures())
