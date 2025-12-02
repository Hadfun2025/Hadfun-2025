import os
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017/'))
db = client[os.getenv('DB_NAME', 'test_database')]

def remove_duplicates_for_league(league_name):
    """Remove duplicate fixtures for a specific league"""
    
    print(f"\n{'='*60}")
    print(f"Processing: {league_name}")
    print(f"{'='*60}")
    
    # Get all fixtures for this league
    all_fixtures = list(db.fixtures.find({'league_name': league_name}))
    print(f"Total fixtures: {len(all_fixtures)}")
    
    # Group by unique key: date + home + away
    fixture_groups = defaultdict(list)
    for fixture in all_fixtures:
        date_str = fixture['utc_date'].strftime('%Y-%m-%d %H:%M') if isinstance(fixture['utc_date'], datetime) else str(fixture['utc_date'])
        key = f"{date_str}|{fixture['home_team']}|{fixture['away_team']}"
        fixture_groups[key].append(fixture)
    
    print(f"Unique fixtures: {len(fixture_groups)}")
    
    # Find and remove duplicates
    removed_count = 0
    kept_ids = []
    
    for key, fixtures_list in fixture_groups.items():
        if len(fixtures_list) > 1:
            # Keep the first one (or the one with more complete data)
            # Sort by: has score data, then by _id (oldest first)
            fixtures_list.sort(key=lambda x: (
                (x.get('score') is not None and x.get('score', {}).get('home') is not None),  # Prefer fixtures with scores
                -x['_id'].generation_time.timestamp()  # Then prefer older records
            ), reverse=True)
            
            kept_fixture = fixtures_list[0]
            kept_ids.append(kept_fixture['_id'])
            
            # Remove the rest
            for fixture in fixtures_list[1:]:
                db.fixtures.delete_one({'_id': fixture['_id']})
                removed_count += 1
        else:
            kept_ids.append(fixtures_list[0]['_id'])
    
    print(f"✅ Removed {removed_count} duplicate fixtures")
    print(f"✅ Kept {len(kept_ids)} unique fixtures")
    
    return removed_count

def main():
    print("=" * 60)
    print("DUPLICATE FIXTURE REMOVAL TOOL")
    print("=" * 60)
    
    uefa_leagues = ['UEFA Champions League', 'UEFA Europa League', 'UEFA Conference League']
    
    total_removed = 0
    
    for league in uefa_leagues:
        removed = remove_duplicates_for_league(league)
        total_removed += removed
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 60)
    print(f"Total duplicates removed: {total_removed}")
    
    # Show final counts
    print("\n📊 Final fixture counts:")
    for league in uefa_leagues:
        count = db.fixtures.count_documents({'league_name': league})
        finished = db.fixtures.count_documents({'league_name': league, 'status': 'FINISHED'})
        print(f"   {league}: {count} total ({finished} finished)")

if __name__ == "__main__":
    main()
