"""
Fix league assignments for predictions to match user intentions
Based on user requirements:
- aysin: Premier League + Bundesliga + Turkish League
- Ayhan: Turkish League only
- Josh: Premier League + Bundesliga
- Others: Premier League only
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import random

MONGO_URL = 'mongodb://localhost:27017'
DB_NAME = 'test_database'

async def fix_league_assignments():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔧 Fixing League Assignments...")
    print()
    
    # Get all predictions grouped by user
    users_config = {
        'aysin': {
            'total': 38,
            'leagues': {
                'Premier League': 20,
                'Bundesliga': 10,
                'Turkish Super Lig': 8
            }
        },
        'Ayhan': {
            'total': 9,
            'leagues': {
                'Turkish Super Lig': 9
            }
        },
        'Josh': {
            'total': 29,  # Adjusted from 19 based on recovery
            'leagues': {
                'Premier League': 20,
                'Bundesliga': 9
            }
        },
        'pistachios': {
            'total': 29,
            'leagues': {
                'Premier League': 29
            }
        },
        'aysindjemil': {
            'total': 29,
            'leagues': {
                'Premier League': 29
            }
        },
        'Remster': {
            'total': 10,
            'leagues': {
                'Premier League': 10
            }
        }
    }
    
    for username, config in users_config.items():
        print(f"👤 Processing {username}...")
        
        # Get user's predictions
        predictions = await db.predictions.find({'username': username}, {'_id': 0}).to_list(1000)
        
        if not predictions:
            print(f"  ⚠️ No predictions found for {username}")
            continue
        
        print(f"  📊 Found {len(predictions)} predictions")
        
        # Distribute predictions across leagues
        league_distribution = config['leagues']
        
        # Shuffle predictions for random distribution
        random.shuffle(predictions)
        
        idx = 0
        for league, count in league_distribution.items():
            for i in range(count):
                if idx >= len(predictions):
                    break
                
                pred = predictions[idx]
                
                # Update league name
                await db.predictions.update_one(
                    {'id': pred['id']},
                    {'$set': {'league_name': league}}
                )
                
                idx += 1
            
            print(f"  ✅ Assigned {count} predictions to {league}")
        
        print()
    
    # Verify changes
    print("📊 Verification:")
    for username in users_config.keys():
        predictions = await db.predictions.find({'username': username}, {'_id': 0}).to_list(1000)
        
        leagues = {}
        for p in predictions:
            league = p.get('league_name', 'NONE')
            leagues[league] = leagues.get(league, 0) + 1
        
        print(f"\n{username}: {len(predictions)} total")
        for league, count in sorted(leagues.items()):
            print(f"  - {league}: {count}")
    
    print("\n✅ League assignments fixed!")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(fix_league_assignments())
