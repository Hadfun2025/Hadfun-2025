"""
Script to fetch all real fixtures from Sportmonks API
Fetches data from August 2025 to current date for all supported leagues
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from pymongo import MongoClient
from sportmonks_service import SportmonksService
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# League mappings (API-Football ID -> Sportmonks ID)
LEAGUE_MAPPINGS = {
    39: {"sportmonks_id": 8, "name": "Premier League", "country": "England"},
    140: {"sportmonks_id": 564, "name": "La Liga", "country": "Spain"},
    78: {"sportmonks_id": 82, "name": "Bundesliga", "country": "Germany"},
    135: {"sportmonks_id": 384, "name": "Serie A", "country": "Italy"},
    61: {"sportmonks_id": 301, "name": "Ligue 1", "country": "France"},
    40: {"sportmonks_id": 2, "name": "Championship", "country": "England"},
    179: {"sportmonks_id": 501, "name": "Scottish Premiership", "country": "Scotland"},
    94: {"sportmonks_id": 271, "name": "Primeira Liga", "country": "Portugal"},
    88: {"sportmonks_id": 72, "name": "Eredivisie", "country": "Netherlands"},
}

async def fetch_fixtures_for_date_range(service: SportmonksService, start_date: datetime, end_date: datetime, league_id: int):
    """Fetch fixtures for a date range"""
    all_fixtures = []
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        logger.info(f"Fetching fixtures for {date_str}, league {league_id}...")
        
        try:
            fixtures = await service.get_fixtures_by_date(date_str, league_id)
            if fixtures:
                all_fixtures.extend(fixtures)
                logger.info(f"  Found {len(fixtures)} fixtures")
        except Exception as e:
            logger.error(f"  Error fetching {date_str}: {e}")
        
        current_date += timedelta(days=1)
        await asyncio.sleep(0.1)  # Rate limiting
    
    return all_fixtures

def transform_to_db_format(api_fixture):
    """Transform API-Football format to database format"""
    fixture_data = api_fixture.get('fixture', {})
    league_data = api_fixture.get('league', {})
    teams_data = api_fixture.get('teams', {})
    goals_data = api_fixture.get('goals', {})
    
    # Parse date
    date_str = fixture_data.get('date')
    if date_str:
        try:
            utc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            utc_date = utc_date.replace(tzinfo=None)  # Make naive for MongoDB
        except:
            utc_date = datetime.utcnow()
    else:
        utc_date = datetime.utcnow()
    
    # Determine status
    status_data = fixture_data.get('status', {})
    status_long = status_data.get('long', 'SCHEDULED')
    if status_long in ['Match Finished', 'FINISHED']:
        status = 'FINISHED'
    elif status_long in ['In Play', 'LIVE']:
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
        'league_id': league_data.get('id'),
        'league_name': league_data.get('name'),
        'home_team': teams_data.get('home', {}).get('name'),
        'away_team': teams_data.get('away', {}).get('name'),
        'home_logo': teams_data.get('home', {}).get('logo'),
        'away_logo': teams_data.get('away', {}).get('logo'),
        'utc_date': utc_date,
        'status': status,
        'matchday': league_data.get('round', 'Unknown'),
        'score': score
    }

async def main():
    """Main execution"""
    print("=" * 60)
    print("FETCHING ALL FIXTURES FROM SPORTMONKS API")
    print("=" * 60)
    
    # Initialize service
    service = SportmonksService()
    
    # Test connection
    print("\n1. Testing Sportmonks API connection...")
    conn_test = await service.test_connection()
    print(f"   Status: {conn_test}")
    
    if conn_test.get('status') != 'connected':
        print("\n❌ ERROR: Cannot connect to Sportmonks API")
        print(f"   Reason: {conn_test.get('reason')}")
        return
    
    # Connect to MongoDB
    print("\n2. Connecting to MongoDB...")
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    print(f"   Connected to database: {os.getenv('DB_NAME')}")
    
    # Define date range: August 1, 2025 to current date
    start_date = datetime(2025, 8, 1)
    end_date = datetime.now()
    
    print(f"\n3. Fetching fixtures from {start_date.date()} to {end_date.date()}")
    print(f"   Total days: {(end_date - start_date).days + 1}")
    
    # Fetch for each league
    total_saved = 0
    for league_id, league_info in LEAGUE_MAPPINGS.items():
        print(f"\n4. Processing {league_info['name']} (League ID: {league_id})...")
        
        try:
            # Fetch fixtures
            fixtures = await fetch_fixtures_for_date_range(service, start_date, end_date, league_id)
            print(f"   Retrieved {len(fixtures)} fixtures from API")
            
            # Transform and save to database
            saved_count = 0
            for fixture in fixtures:
                try:
                    db_fixture = transform_to_db_format(fixture)
                    
                    # Upsert to database
                    result = db.fixtures.update_one(
                        {'fixture_id': db_fixture['fixture_id']},
                        {'$set': db_fixture},
                        upsert=True
                    )
                    
                    if result.upserted_id or result.modified_count > 0:
                        saved_count += 1
                except Exception as e:
                    logger.error(f"   Error saving fixture {fixture.get('fixture', {}).get('id')}: {e}")
            
            print(f"   ✅ Saved {saved_count} fixtures to database")
            total_saved += saved_count
            
        except Exception as e:
            logger.error(f"   ❌ Error processing {league_info['name']}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total fixtures saved: {total_saved}")
    
    # Show breakdown by league
    print("\nFixtures by league:")
    for league_id, league_info in LEAGUE_MAPPINGS.items():
        count = db.fixtures.count_documents({'league_id': league_id})
        print(f"  {league_info['name']}: {count}")
    
    # Show breakdown by status
    print("\nFixtures by status:")
    for status in ['FINISHED', 'LIVE', 'SCHEDULED']:
        count = db.fixtures.count_documents({'status': status})
        print(f"  {status}: {count}")
    
    print("\n✅ COMPLETE!")

if __name__ == "__main__":
    asyncio.run(main())
