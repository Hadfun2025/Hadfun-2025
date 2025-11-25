import asyncio
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from api_football_service import APIFootballService

os.environ.setdefault('MONGO_URL', 'mongodb://localhost:27017')
os.environ.setdefault('DB_NAME', 'test_database')

LEAGUES = {
    39: "Premier League",
    140: "La Liga",
    78: "Bundesliga",
    135: "Serie A",
}

async def fetch_upcoming():
    service = APIFootballService()
    client = MongoClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    total_saved = 0
    
    for league_id, league_name in LEAGUES.items():
        try:
            print(f"\nFetching {league_name}...")
            
            # Get fixtures for next 2 months
            today = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
            fixtures = await service.get_fixtures_by_league_and_season(
                league_id, 
                season=2025, 
                from_date=today, 
                to_date=end_date
            )
            
            if fixtures:
                print(f"  Found {len(fixtures)} upcoming fixtures")
                
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
                    
                    total_saved += 1
                    
                print(f"  ✅ Saved {len(fixtures)} fixtures")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        await asyncio.sleep(1)
    
    print(f"\n✅ Total fixtures saved: {total_saved}")
    client.close()

if __name__ == '__main__':
    asyncio.run(fetch_upcoming())
