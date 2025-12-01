import requests
import os
from pymongo import MongoClient
from datetime import datetime, timezone
import time

# API Configuration
API_KEY = os.getenv('API_FOOTBALL_KEY', 'edd455f6352f2079c15983bca9af94cf')
API_HOST = os.getenv('API_FOOTBALL_HOST', 'v3.football.api-sports.io')
BASE_URL = f"https://{API_HOST}"

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017/'))
db = client['test_database']

# UEFA Competition IDs on API-Football
UEFA_COMPETITIONS = {
    2: 'UEFA Champions League',      # Champions League
    3: 'UEFA Europa League',         # Europa League  
    848: 'UEFA Conference League'    # Conference League
}

def fetch_fixtures_for_competition(league_id, season=2024):
    """Fetch fixtures for a specific UEFA competition and season"""
    
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': API_HOST
    }
    
    url = f"{BASE_URL}/fixtures"
    params = {
        'league': league_id,
        'season': season
    }
    
    print(f"\n🔍 Fetching {UEFA_COMPETITIONS[league_id]} fixtures for season {season}...")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get('response', [])
            print(f"   Found {len(fixtures)} fixtures from API")
            return fixtures
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return []

def process_and_store_fixture(fixture_data, league_name):
    """Process API fixture data and store in database"""
    
    try:
        fixture = fixture_data['fixture']
        teams = fixture_data['teams']
        league = fixture_data['league']
        score = fixture_data['score']
        
        # Parse date
        utc_date_str = fixture['date']
        utc_date = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
        
        # Determine status
        status_mapping = {
            'FT': 'FINISHED',
            'AET': 'FINISHED',
            'PEN': 'FINISHED',
            'NS': 'SCHEDULED',
            'TBD': 'SCHEDULED',
            'PST': 'POSTPONED',
            'CANC': 'CANCELLED',
            '1H': 'IN_PLAY',
            'HT': 'IN_PLAY',
            '2H': 'IN_PLAY',
            'ET': 'IN_PLAY',
            'P': 'IN_PLAY',
            'LIVE': 'IN_PLAY'
        }
        
        api_status = fixture['status']['short']
        status = status_mapping.get(api_status, 'SCHEDULED')
        
        # Get scores (only for finished matches)
        home_score = None
        away_score = None
        
        if status == 'FINISHED':
            # Use fulltime score, or if not available, try extratime, then penalty
            if score['fulltime']['home'] is not None:
                home_score = score['fulltime']['home']
                away_score = score['fulltime']['away']
            elif score['extratime']['home'] is not None:
                home_score = score['extratime']['home']
                away_score = score['extratime']['away']
            elif score['penalty']['home'] is not None:
                home_score = score['penalty']['home']
                away_score = score['penalty']['away']
        
        # Create fixture document
        fixture_doc = {
            'fixture_id': str(fixture['id']),
            'utc_date': utc_date,
            'home_team': teams['home']['name'],
            'away_team': teams['away']['name'],
            'league_id': league['id'],
            'league_name': league_name,
            'status': status,
            'matchday': league.get('round', 'Unknown'),
            'venue': fixture.get('venue', {}).get('name', 'Unknown'),
            'score': {
                'home': home_score,
                'away': away_score
            }
        }
        
        # Upsert (update if exists, insert if not)
        db.fixtures.update_one(
            {'fixture_id': fixture_doc['fixture_id']},
            {'$set': fixture_doc},
            upsert=True
        )
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Error processing fixture: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("UEFA FIXTURES FETCHER - 2024/25 Season")
    print("=" * 60)
    
    total_added = 0
    total_updated = 0
    
    for league_id, league_name in UEFA_COMPETITIONS.items():
        print(f"\n{'='*60}")
        print(f"Processing: {league_name}")
        print(f"{'='*60}")
        
        # Check current count
        before_count = db.fixtures.count_documents({'league_name': league_name})
        print(f"Current fixtures in DB: {before_count}")
        
        # Fetch fixtures
        fixtures = fetch_fixtures_for_competition(league_id, 2024)
        
        if fixtures:
            print(f"\n📥 Processing {len(fixtures)} fixtures...")
            success_count = 0
            
            for idx, fixture_data in enumerate(fixtures, 1):
                if process_and_store_fixture(fixture_data, league_name):
                    success_count += 1
                
                if idx % 20 == 0:
                    print(f"   Processed {idx}/{len(fixtures)}...")
            
            after_count = db.fixtures.count_documents({'league_name': league_name})
            added = after_count - before_count
            
            print(f"\n✅ Completed {league_name}")
            print(f"   Successfully processed: {success_count}/{len(fixtures)}")
            print(f"   Fixtures in DB: {before_count} → {after_count} (+{added})")
            
            total_added += added
        
        # Rate limiting - wait between competitions
        if league_id != list(UEFA_COMPETITIONS.keys())[-1]:
            print("\n⏳ Waiting 2 seconds before next competition...")
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ FETCH COMPLETE!")
    print("=" * 60)
    print(f"Total new fixtures added: {total_added}")
    
    # Show final counts
    print("\n📊 Final fixture counts:")
    for league_name in UEFA_COMPETITIONS.values():
        count = db.fixtures.count_documents({'league_name': league_name})
        finished = db.fixtures.count_documents({'league_name': league_name, 'status': 'FINISHED'})
        print(f"   {league_name}: {count} total ({finished} finished)")

if __name__ == "__main__":
    main()
