import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

async def sync_predictions():
    load_dotenv()
    mongo_url = os.getenv('MONGO_URL')
    db_name = os.getenv('DB_NAME', 'test_database')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("Syncing predictions with fixture data...")
    
    # Get all predictions
    all_predictions = await db.predictions.find({}).to_list(length=10000)
    
    updated_count = 0
    missing_fixtures = 0
    
    for pred in all_predictions:
        fixture_id = pred.get('fixture_id')
        
        # Find matching fixture
        fixture = await db.fixtures.find_one({"fixture_id": fixture_id})
        
        if fixture:
            # Update prediction with fixture details
            await db.predictions.update_one(
                {"id": pred.get('id')},
                {"$set": {
                    "home_team": fixture.get('home_team'),
                    "away_team": fixture.get('away_team'),
                    "league": fixture.get('league_name'),
                    "home_score": fixture.get('home_score'),
                    "away_score": fixture.get('away_score'),
                    "match_date": fixture.get('utc_date') or fixture.get('match_date')
                }}
            )
            updated_count += 1
        else:
            missing_fixtures += 1
    
    print(f"✅ Synced {updated_count} predictions")
    print(f"⚠️  {missing_fixtures} predictions reference missing fixtures")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(sync_predictions())
