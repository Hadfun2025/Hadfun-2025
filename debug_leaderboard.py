#!/usr/bin/env python3
"""
Debug leaderboard team_name issue
"""

import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient

# Add backend directory to path
sys.path.append('/app/backend')

async def debug_leaderboard():
    """Debug the leaderboard team_name issue"""
    
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    print("=== Debugging Leaderboard Team Names ===")
    
    # Get users with season_points
    pipeline = [
        {"$match": {"season_points": {"$exists": True}}},
        {
            "$lookup": {
                "from": "predictions",
                "localField": "id",
                "foreignField": "user_id",
                "as": "predictions"
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "username": 1,
                "email": 1,
                "season_points": {"$ifNull": ["$season_points", 0]},
                "weekly_points": {"$ifNull": ["$weekly_points", 0]},
                "weekly_wins": {"$ifNull": ["$weekly_wins", 0]},
                "total_predictions": {"$size": "$predictions"},
                "correct_predictions": {
                    "$size": {
                        "$filter": {
                            "input": "$predictions",
                            "as": "pred",
                            "cond": {"$eq": ["$$pred.result", "correct"]}
                        }
                    }
                }
            }
        },
        {"$sort": {"season_points": -1}},
        {"$limit": 3}  # Just get first 3 for debugging
    ]
    
    results = await db.users.aggregate(pipeline).to_list(None)
    print(f"Found {len(results)} users with season_points")
    
    if results:
        user = results[0]
        print(f"First user: {user['username']} (ID: {user['id']})")
        
        # Check team membership
        membership = await db.team_members.find_one({"user_id": user['id']}, {"_id": 0})
        print(f"Team membership: {membership}")
        
        if membership:
            team = await db.teams.find_one({"id": membership['team_id']}, {"_id": 0, "name": 1})
            print(f"Team: {team}")
            team_name = team.get('name') if team else 'No Team'
        else:
            team_name = 'No Team'
        
        print(f"Calculated team_name: {team_name}")
        
        # Now simulate the full leaderboard logic
        for idx, user in enumerate(results):
            user['rank'] = idx + 1
            user['total_points'] = user["season_points"]
            
            # Get user's primary team (first team they joined)
            membership = await db.team_members.find_one({"user_id": user['id']}, {"_id": 0})
            if membership:
                team = await db.teams.find_one({"id": membership['team_id']}, {"_id": 0, "name": 1})
                user['team_name'] = team.get('name') if team else 'No Team'
            else:
                user['team_name'] = 'No Team'
        
        print(f"Final result for first user: {results[0]}")
        print(f"Has team_name: {'team_name' in results[0]}")
        print(f"team_name value: {results[0].get('team_name')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(debug_leaderboard())