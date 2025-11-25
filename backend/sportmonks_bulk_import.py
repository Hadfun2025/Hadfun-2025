"""
Bulk import all fixtures from Sportmonks API v3
Using proper includes and filters as recommended by Sportmonks
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

# League mappings (Sportmonks IDs)
LEAGUES = {
    8: {'name': 'Premier League', 'api_football_id': 39, 'country': 'England'},
    564: {'name': 'La Liga', 'api_football_id': 140, 'country': 'Spain'},
    82: {'name': 'Bundesliga', 'api_football_id': 78, 'country': 'Germany'},
    384: {'name': 'Serie A', 'api_football_id': 135, 'country': 'Italy'},
    301: {'name': 'Ligue 1', 'api_football_id': 61, 'country': 'France'},
    2: {'name': 'Championship', 'api_football_id': 40, 'country': 'England'},
    501: {'name': 'Scottish Premiership', 'api_football_id': 179, 'country': 'Scotland'},
}

async def fetch_all_fixtures_for_league(league_id: int, league_info: dict):
    """Fetch all fixtures for a league using pagination"""
    all_fixtures = []
    page = 1
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            try:
                endpoint = f"{BASE_URL}/fixtures"
                params = {
                    "api_token": API_TOKEN,
                    "filters": f"fixtureLeagues:{league_id}",
                    "include": "scores;participants;state;round",
                    "page": page,
                    "per_page": 100  # Max per page
                }
                
                logger.info(f"Fetching page {page} for league {league_id}...")
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                fixtures = data.get('data', [])
                
                if not fixtures:
                    break
                
                all_fixtures.extend(fixtures)
                logger.info(f"  Got {len(fixtures)} fixtures (total: {len(all_fixtures)})")
                
                # Check pagination
                pagination = data.get('pagination', {})
                if not pagination.get('has_more'):
                    break
                
                page += 1
                await asyncio.sleep(0.2)  # Rate limiting
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning("Rate limited, waiting 5 seconds...")
                    await asyncio.sleep(5)
                    continue
                else:
                    logger.error(f"HTTP Error: {e}")
                    break
            except Exception as e:
                logger.error(f"Error: {e}")
                break
    
    return all_fixtures

def transform_fixture(fixture, league_info):
    """Transform Sportmonks fixture to our database format"""
    try:
        # Get participants (teams)
        participants = fixture.get('participants', [])
        if not participants or len(participants) < 2:
            return None
        
        home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), participants[0])
        away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), participants[1])
        
        # Get scores
        scores = fixture.get('scores', [])
        home_score = None
        away_score = None
        
        for score in scores:
            description = score.get('description', '')
            if 'CURRENT' in description.upper() or 'FT' in description.upper():
                score_data = score.get('score', {})
                participant_id = score.get('participant_id')
                goals = score_data.get('goals')
                
                if participant_id == home_team.get('id'):
                    home_score = goals
                elif participant_id == away_team.get('id'):
                    away_score = goals
        
        # Get state/status
        state = fixture.get('state', {})
        state_id = state.get('id') if isinstance(state, dict) else fixture.get('state_id', 1)
        
        if state_id == 5:  # Finished
            status = 'FINISHED'
        elif state_id in [3, 4]:  # Live
            status = 'LIVE'
        else:
            status = 'SCHEDULED'
        
        # Parse date
        date_str = fixture.get('starting_at')
        if date_str:
            try:
                utc_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            except:
                utc_date = datetime.utcnow()
        else:
            utc_date = datetime.utcnow()
        
        # Get round/matchday
        round_data = fixture.get('round', {})
        if isinstance(round_data, dict):
            round_name = round_data.get('name', 'Unknown')
        else:
            round_name = str(round_data) if round_data else 'Unknown'
        
        # Build fixture object
        db_fixture = {
            'fixture_id': fixture.get('id'),
            'league_id': league_info['api_football_id'],
            'league_name': league_info['name'],
            'home_team': home_team.get('name'),
            'away_team': away_team.get('name'),
            'home_logo': home_team.get('image_path'),
            'away_logo': away_team.get('image_path'),
            'utc_date': utc_date,
            'status': status,
            'matchday': round_name,
            'score': None
        }
        
        # Add score if both teams have scores
        if home_score is not None and away_score is not None:
            db_fixture['score'] = {'home': home_score, 'away': away_score}
        
        return db_fixture
        
    except Exception as e:
        logger.error(f"Error transforming fixture {fixture.get('id')}: {e}")
        return None

async def main():
    print("=" * 80)
    print("SPORTMONKS BULK FIXTURE IMPORT")
    print("Importing ALL fixtures from current 2025-26 season")
    print("=" * 80)
    
    if not API_TOKEN:
        print("\n❌ ERROR: SPORTMONKS_API_TOKEN not found in environment")
        return
    
    print(f"\n✅ API Token found: {API_TOKEN[:20]}...")
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    print(f"✅ Connected to database: {os.getenv('DB_NAME')}")
    
    # Clear existing fixtures to avoid duplicates
    print("\n🗑️  Clearing existing fixtures...")
    db.fixtures.delete_many({})
    print("✅ Database cleared")
    
    total_imported = 0
    
    for league_id, league_info in LEAGUES.items():
        print(f"\n{'='*80}")
        print(f"📋 {league_info['name']} (Sportmonks ID: {league_id})")
        print('='*80)
        
        try:
            # Fetch all fixtures
            fixtures = await fetch_all_fixtures_for_league(league_id, league_info)
            print(f"\n✅ Retrieved {len(fixtures)} total fixtures from API")
            
            # Transform and save
            saved = 0
            finished = 0
            scheduled = 0
            
            for fixture in fixtures:
                transformed = transform_fixture(fixture, league_info)
                if transformed:
                    # Save to database
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
            
            print(f"✅ Saved {saved} fixtures ({finished} finished, {scheduled} scheduled)")
            total_imported += saved
            
        except Exception as e:
            print(f"❌ Error processing {league_info['name']}: {e}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("IMPORT COMPLETE")
    print("=" * 80)
    print(f"\nTotal fixtures imported: {total_imported}")
    
    print("\n📊 Breakdown by league:")
    for league_id, league_info in LEAGUES.items():
        count = db.fixtures.count_documents({'league_id': league_info['api_football_id']})
        finished = db.fixtures.count_documents({'league_id': league_info['api_football_id'], 'status': 'FINISHED'})
        scheduled = db.fixtures.count_documents({'league_id': league_info['api_football_id'], 'status': 'SCHEDULED'})
        print(f"  {league_info['name']}: {count} total ({finished} finished, {scheduled} scheduled)")
    
    print("\n✅ ALL DONE! Your app now has real fixture data from Sportmonks.")

if __name__ == "__main__":
    asyncio.run(main())
