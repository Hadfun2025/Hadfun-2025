import requests
import os
from pymongo import MongoClient
from datetime import datetime
import time

# API Configuration
API_KEY = 'edd455f6352f2079c15983bca9af94cf'
API_HOST = 'v3.football.api-sports.io'
BASE_URL = f'https://{API_HOST}'

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017/'))
db = client[os.getenv('DB_NAME', 'test_database')]

# Team IDs for major clubs
TEAMS = {
    40: 'Liverpool',
    42: 'Arsenal',
    33: 'Manchester United',
    50: 'Manchester City',
    49: 'Chelsea',
    47: 'Tottenham',
}

def fetch_team_fixtures(team_id, team_name, league_id=2, season=2024):
    """Fetch fixtures for a specific team"""
    
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }
    
    url = f"{BASE_URL}/fixtures"
    params = {
        'team': team_id,
        'league': league_id,
        'season': season
    }
    
    print(f"\n🔍 Fetching {team_name} Champions League fixtures...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get('response', [])
            print(f"   Found {len(fixtures)} fixtures from API")
            
            added = 0
            updated = 0
            
            for fixture_data in fixtures:
                fixture = fixture_data['fixture']
                teams = fixture_data['teams']
                league = fixture_data['league']
                score = fixture_data['score']
                
                # Parse date
                utc_date = datetime.fromisoformat(fixture['date'].replace('Z', '+00:00'))
                
                # Determine status
                status_map = {
                    'FT': 'FINISHED', 'AET': 'FINISHED', 'PEN': 'FINISHED',
                    'NS': 'SCHEDULED', 'TBD': 'SCHEDULED', 'PST': 'POSTPONED',
                    'CANC': 'CANCELLED', '1H': 'IN_PLAY', 'HT': 'IN_PLAY',
                    '2H': 'IN_PLAY', 'ET': 'IN_PLAY', 'P': 'IN_PLAY', 'LIVE': 'IN_PLAY'
                }
                status = status_map.get(fixture['status']['short'], 'SCHEDULED')
                
                # Get scores
                home_score = None
                away_score = None
                if status == 'FINISHED':
                    if score['fulltime']['home'] is not None:
                        home_score = score['fulltime']['home']
                        away_score = score['fulltime']['away']
                
                # Create fixture document
                fixture_doc = {
                    'fixture_id': fixture['id'],  # Store as integer for consistency
                    'utc_date': utc_date,
                    'home_team': teams['home']['name'],
                    'away_team': teams['away']['name'],
                    'league_id': league['id'],
                    'league_name': 'UEFA Champions League',
                    'status': status,
                    'matchday': league.get('round', 'Unknown'),
                    'venue': fixture.get('venue', {}).get('name', 'Unknown'),
                    'score': {'home': home_score, 'away': away_score}
                }
                
                # Upsert
                result = db.fixtures.update_one(
                    {'fixture_id': fixture_doc['fixture_id']},
                    {'$set': fixture_doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    added += 1
                elif result.modified_count > 0:
                    updated += 1
            
            print(f"   ✅ Added: {added} | Updated: {updated}")
            return added, updated
            
        else:
            print(f"   ❌ API Error: {response.status_code}")
            return 0, 0
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return 0, 0

def main():
    print("=" * 60)
    print("TEAM-SPECIFIC FIXTURE FETCH - Champions League 2024/25")
    print("=" * 60)
    
    total_added = 0
    total_updated = 0
    
    for team_id, team_name in TEAMS.items():
        added, updated = fetch_team_fixtures(team_id, team_name)
        total_added += added
        total_updated += updated
        time.sleep(2)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE!")
    print(f"   New fixtures added: {total_added}")
    print(f"   Fixtures updated: {total_updated}")
    print(f"{'='*60}")
    
    # Verify Liverpool fixtures
    liverpool_count = db.fixtures.count_documents({
        'league_name': 'UEFA Champions League',
        '$or': [{'home_team': 'Liverpool'}, {'away_team': 'Liverpool'}]
    })
    print(f"\n📊 Liverpool Champions League fixtures in DB: {liverpool_count}")

if __name__ == "__main__":
    main()
