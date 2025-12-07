"""
Script to wipe all predictions and reset points for fresh start
Keeps users and teams intact
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime

async def wipe_predictions():
    """Clean wipe of all predictions and points"""
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client[os.environ.get('DB_NAME')]
    
    print("🧹 Starting clean wipe...")
    print("=" * 60)
    
    # Count before deletion
    predictions_count = await db.predictions.count_documents({})
    league_points_count = await db.user_league_points.count_documents({})
    
    print(f"\n📊 Current data:")
    print(f"  - Predictions: {predictions_count}")
    print(f"  - League points records: {league_points_count}")
    
    # Get user count for reference
    users_count = await db.users.count_documents({})
    teams_count = await db.teams.count_documents({})
    print(f"  - Users (will keep): {users_count}")
    print(f"  - Teams (will keep): {teams_count}")
    
    # Delete all predictions
    print("\n🗑️  Deleting predictions...")
    result1 = await db.predictions.delete_many({})
    print(f"  ✅ Deleted {result1.deleted_count} predictions")
    
    # Delete all league points
    print("\n🗑️  Deleting league points...")
    result2 = await db.user_league_points.delete_many({})
    print(f"  ✅ Deleted {result2.deleted_count} league point records")
    
    # Reset user points to zero
    print("\n🔄 Resetting user points to zero...")
    result3 = await db.users.update_many(
        {},
        {
            "$set": {
                "total_points": 0,
                "season_points": 0,
                "points": 0,
                "correct_predictions": 0,
                "total_predictions": 0,
                "weekly_wins": 0,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
    )
    print(f"  ✅ Reset points for {result3.modified_count} users")
    
    # Verify cleanup
    print("\n✅ Verification:")
    remaining_predictions = await db.predictions.count_documents({})
    remaining_points = await db.user_league_points.count_documents({})
    print(f"  - Remaining predictions: {remaining_predictions}")
    print(f"  - Remaining league points: {remaining_points}")
    
    print("\n" + "=" * 60)
    print("🎉 Clean wipe complete! Ready for fresh start.")
    print("=" * 60)
    
    # Show what's still there
    print("\n📋 What's preserved:")
    users = await db.users.find({}, {"_id": 0, "username": 1, "email": 1}).to_list(100)
    print(f"\n👥 Users ({len(users)}):")
    for user in users:
        print(f"  - {user['username']} ({user['email']})")
    
    teams = await db.teams.find({}, {"_id": 0, "name": 1}).to_list(100)
    print(f"\n👥 Teams ({len(teams)}):")
    for team in teams:
        print(f"  - {team['name']}")
    
    client.close()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete ALL predictions and reset all points!")
    print("Users and teams will be preserved.\n")
    
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        asyncio.run(wipe_predictions())
    else:
        print("❌ Cancelled.")
