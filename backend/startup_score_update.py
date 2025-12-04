#!/usr/bin/env python3
"""
Startup script to ensure recent match scores are populated
This runs automatically when backend starts
"""
import requests
import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_recent_scores():
    """Update scores for matches in the last 7 days"""
    
    API_KEY = os.getenv('API_FOOTBALL_KEY', 'edd455f6352f2079c15983bca9af94cf')
    API_HOST = 'v3.football.api-sports.io'
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    DB_NAME = os.getenv('DB_NAME', 'test_database')
    
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    
    headers = {'x-rapidapi-key': API_KEY, 'x-rapidapi-host': API_HOST}
    
    # Check for Premier League fixtures in last 7 days without scores
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    fixtures_without_scores = db.fixtures.find({
        'league_id': 39,
        'utc_date': {'$gte': seven_days_ago, '$lte': datetime.now()},
        'status': {'$in': ['SCHEDULED', 'Match Scheduled', 'NS']},
        '$or': [
            {'score.home': None},
            {'score.home': {'$exists': False}}
        ]
    })
    
    count = 0
    for fixture in fixtures_without_scores:
        fixture_id = fixture.get('fixture_id')
        
        # Fetch from API
        try:
            response = requests.get(
                f'https://{API_HOST}/fixtures',
                headers=headers,
                params={'id': fixture_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json().get('response', [])
                if data:
                    api_fixture = data[0]
                    status = api_fixture['fixture']['status']['short']
                    
                    if status in ['FT', 'AET', 'PEN']:
                        score = api_fixture['score']
                        h_score = score['fulltime']['home']
                        a_score = score['fulltime']['away']
                        
                        db.fixtures.update_one(
                            {'fixture_id': fixture_id},
                            {'$set': {
                                'status': 'FINISHED',
                                'score': {'home': h_score, 'away': a_score},
                                'home_score': h_score,
                                'away_score': a_score
                            }}
                        )
                        count += 1
                        logger.info(f"Updated: {fixture['home_team']} {h_score}-{a_score} {fixture['away_team']}")
        except Exception as e:
            logger.error(f"Error updating fixture {fixture_id}: {e}")
            continue
    
    logger.info(f"Startup score update complete: {count} fixtures updated")

if __name__ == "__main__":
    update_recent_scores()
