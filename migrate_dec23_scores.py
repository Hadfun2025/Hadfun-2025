#!/usr/bin/env python3
"""
ONE-TIME MIGRATION: Hardcode Dec 2-3 Premier League scores
Run this once to populate production database with historical scores
"""
import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Hardcoded scores from reliable sources (BBC Sport, official Premier League)
SCORES = [
    # December 2, 2025
    {
        'home': 'Bournemouth',
        'away': 'Everton',
        'home_score': 0,
        'away_score': 1,
        'date': datetime(2025, 12, 2, 19, 30),
        'fixture_id': 1379100
    },
    {
        'home': 'Fulham',
        'away': 'Manchester City',
        'home_score': 4,
        'away_score': 5,
        'date': datetime(2025, 12, 2, 19, 30),
        'fixture_id': 1379101
    },
    {
        'home': 'Newcastle',
        'away': 'Tottenham',
        'home_score': 2,
        'away_score': 2,
        'date': datetime(2025, 12, 2, 20, 15),
        'fixture_id': 1379102
    },
    
    # December 3, 2025
    {
        'home': 'Burnley',
        'away': 'Crystal Palace',
        'home_score': 0,
        'away_score': 1,
        'date': datetime(2025, 12, 3, 19, 30),
        'fixture_id': 1379103
    },
    {
        'home': 'Brighton',
        'away': 'Aston Villa',
        'home_score': 3,
        'away_score': 4,
        'date': datetime(2025, 12, 3, 19, 30),
        'fixture_id': 1379104
    },
    {
        'home': 'Arsenal',
        'away': 'Brentford',
        'home_score': 2,
        'away_score': 0,
        'date': datetime(2025, 12, 3, 19, 30),
        'fixture_id': 1379105
    },
    {
        'home': 'Wolves',
        'away': 'Nottingham Forest',
        'home_score': 0,
        'away_score': 1,
        'date': datetime(2025, 12, 3, 19, 30),
        'fixture_id': 1379106
    },
    {
        'home': 'Leeds',
        'away': 'Chelsea',
        'home_score': 3,
        'away_score': 1,
        'date': datetime(2025, 12, 3, 20, 15),
        'fixture_id': 1379107
    },
    {
        'home': 'Liverpool',
        'away': 'Sunderland',
        'home_score': 1,
        'away_score': 1,
        'date': datetime(2025, 12, 3, 20, 15),
        'fixture_id': 1379108
    }
]

print("=" * 60)
print("ONE-TIME MIGRATION: Dec 2-3 Premier League Scores")
print("=" * 60)
print()

updated = 0
created = 0
skipped = 0

for match in SCORES:
    # Try to find existing fixture
    existing = db.fixtures.find_one({
        'league_id': 39,
        'home_team': match['home'],
        'away_team': match['away']
    })
    
    if existing:
        # Update existing fixture
        result = db.fixtures.update_one(
            {'_id': existing['_id']},
            {'$set': {
                'status': 'FINISHED',
                'score': {
                    'home': match['home_score'],
                    'away': match['away_score']
                },
                'home_score': match['home_score'],
                'away_score': match['away_score']
            }}
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated: {match['home']} {match['home_score']}-{match['away_score']} {match['away']}")
            updated += 1
        else:
            print(f"ℹ️  Already correct: {match['home']} vs {match['away']}")
            skipped += 1
    else:
        # Create new fixture entry
        fixture_doc = {
            'fixture_id': match['fixture_id'],
            'utc_date': match['date'],
            'home_team': match['home'],
            'away_team': match['away'],
            'league_id': 39,
            'league_name': 'Premier League',
            'status': 'FINISHED',
            'matchday': 'Regular Season - 14',
            'venue': 'Unknown',
            'score': {
                'home': match['home_score'],
                'away': match['away_score']
            },
            'home_score': match['home_score'],
            'away_score': match['away_score']
        }
        
        db.fixtures.insert_one(fixture_doc)
        print(f"✨ Created: {match['home']} {match['home_score']}-{match['away_score']} {match['away']}")
        created += 1

print()
print("=" * 60)
print("✅ MIGRATION COMPLETE!")
print("=" * 60)
print(f"Updated: {updated}")
print(f"Created: {created}")
print(f"Skipped: {skipped}")
print()
print("🚀 Deploy now to see these scores on production!")
