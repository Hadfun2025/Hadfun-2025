"""
Import fixtures from CSV file
CSV format: date,home_team,away_team,home_score,away_score,league,matchday,status
Example: 2025-08-15,Liverpool,Bournemouth,4,2,Premier League,1,FINISHED
"""
import csv
import sys
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# League name to ID mapping
LEAGUE_MAP = {
    'Premier League': 39,
    'La Liga': 140,
    'Bundesliga': 78,
    'Serie A': 135,
    'Ligue 1': 61,
    'Championship': 40,
    'Scottish Premiership': 179,
    'Primeira Liga': 94,
    'Eredivisie': 88,
}

def import_from_csv(csv_file):
    """Import fixtures from CSV"""
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = MongoClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    imported = 0
    errors = 0
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Parse date
                date_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                if 'time' in row and row['time']:
                    time_obj = datetime.strptime(row['time'], '%H:%M')
                    date_obj = date_obj.replace(hour=time_obj.hour, minute=time_obj.minute)
                
                # Get league ID
                league_name = row.get('league', 'Premier League')
                league_id = LEAGUE_MAP.get(league_name, 39)
                
                # Parse scores
                home_score = int(row['home_score']) if row.get('home_score') and row['home_score'].isdigit() else None
                away_score = int(row['away_score']) if row.get('away_score') and row['away_score'].isdigit() else None
                
                # Build fixture
                fixture = {
                    'fixture_id': int(f"{league_id}{row.get('matchday', '1').zfill(2)}{imported:03d}"),
                    'league_id': league_id,
                    'league_name': league_name,
                    'home_team': row['home_team'],
                    'away_team': row['away_team'],
                    'home_logo': None,
                    'away_logo': None,
                    'utc_date': date_obj,
                    'status': row.get('status', 'SCHEDULED'),
                    'matchday': f"Regular Season - {row.get('matchday', '1')}",
                    'score': {'home': home_score, 'away': away_score} if home_score is not None else None
                }
                
                # Upsert
                db.fixtures.update_one(
                    {'fixture_id': fixture['fixture_id']},
                    {'$set': fixture},
                    upsert=True
                )
                
                imported += 1
                print(f"✅ {fixture['home_team']} vs {fixture['away_team']}")
                
            except Exception as e:
                errors += 1
                print(f"❌ Error on row: {row} - {e}")
    
    print(f"\n✅ Imported {imported} fixtures")
    print(f"❌ {errors} errors")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_fixtures_from_csv.py <csv_file>")
        sys.exit(1)
    
    import_from_csv(sys.argv[1])
