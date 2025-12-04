#!/usr/bin/env python3
"""
One-time script to reset all user points and recalculate based on new winner-takes-all logic.

This script:
1. Resets all users' season_points to 0
2. Removes the 'points' field from all predictions (no longer used)
3. Recalculates and awards points using the new matchday winner logic

Run this script manually after deploying the new scoring logic.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


async def reset_and_recalculate():
    """Reset all points and recalculate using new logic"""
    
    try:
        # Step 1: Reset all users' season_points to 0
        logger.info("Step 1: Resetting all users' season_points to 0...")
        result = await db.users.update_many(
            {},
            {"$set": {"season_points": 0}}
        )
        logger.info(f"  ✅ Reset {result.modified_count} users' points to 0")
        
        # Step 2: Remove 'points' field from all predictions (no longer used)
        logger.info("Step 2: Removing 'points' field from predictions...")
        result = await db.predictions.update_many(
            {"points": {"$exists": True}},
            {"$unset": {"points": ""}}
        )
        logger.info(f"  ✅ Removed points field from {result.modified_count} predictions")
        
        # Step 2b: Clear the user_league_points collection (fresh start)
        logger.info("Step 2b: Clearing user_league_points collection...")
        result = await db.user_league_points.delete_many({})
        logger.info(f"  ✅ Removed {result.deleted_count} old records")
        
        # Step 3: Recalculate points using new winner-takes-all logic
        logger.info("Step 3: Recalculating points using winner-takes-all logic...")
        
        # Get all fixtures with their matchday and league info
        fixtures = await db.fixtures.find(
            {"status": "FINISHED", "matchday": {"$exists": True, "$ne": None}},
            {"_id": 0, "fixture_id": 1, "league_id": 1, "matchday": 1, "league_name": 1}
        ).to_list(10000)
        
        if not fixtures:
            logger.info("  No finished fixtures with matchday info found")
            return
        
        # Group fixtures by (league_id, matchday)
        league_matchday_groups = {}
        for fixture in fixtures:
            league_id = fixture.get('league_id')
            matchday = fixture.get('matchday', '').strip()
            
            if not league_id or not matchday:
                continue
            
            key = (league_id, matchday)
            if key not in league_matchday_groups:
                league_matchday_groups[key] = {
                    'league_id': league_id,
                    'league_name': fixture.get('league_name', 'Unknown'),
                    'matchday': matchday,
                    'fixture_ids': []
                }
            league_matchday_groups[key]['fixture_ids'].append(fixture['fixture_id'])
        
        logger.info(f"  Found {len(league_matchday_groups)} unique (league, matchday) combinations")
        
        # For each group, find winners and award points
        total_winners = 0
        for (league_id, matchday), group_data in league_matchday_groups.items():
            fixture_ids = group_data['fixture_ids']
            league_name = group_data['league_name']
            
            # Get all correct predictions for these fixtures
            correct_predictions = await db.predictions.find({
                "fixture_id": {"$in": fixture_ids},
                "result": "correct"
            }, {"_id": 0, "user_id": 1, "username": 1}).to_list(10000)
            
            if not correct_predictions:
                continue
            
            # Count correct predictions per user
            user_correct_counts = {}
            for pred in correct_predictions:
                user_id = pred['user_id']
                if user_id not in user_correct_counts:
                    user_correct_counts[user_id] = {
                        'count': 0,
                        'username': pred.get('username', 'Unknown')
                    }
                user_correct_counts[user_id]['count'] += 1
            
            # Find the maximum correct count
            max_correct = max(user_correct_counts.values(), key=lambda x: x['count'])['count']
            
            # Find all users with max correct predictions (winners)
            winners = [uid for uid, data in user_correct_counts.items() if data['count'] == max_correct]
            
            # Award 3 points to each winner
            for winner_id in winners:
                await db.users.update_one(
                    {"id": winner_id},
                    {"$inc": {"season_points": 3}}
                )
                username = user_correct_counts[winner_id]['username']
                logger.info(f"    ✅ {league_name} - {matchday}: {username} wins with {max_correct} correct → +3 points")
                total_winners += 1
        
        logger.info(f"  🎉 Recalculation complete: {total_winners} winners awarded 3 points each")
        
        # Step 4: Verify results
        logger.info("Step 4: Verifying results...")
        users_with_points = await db.users.count_documents({"season_points": {"$gt": 0}})
        total_points = await db.users.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$season_points"}}}
        ]).to_list(1)
        total_points_value = total_points[0]['total'] if total_points else 0
        
        logger.info(f"  ✅ {users_with_points} users have points")
        logger.info(f"  ✅ Total points awarded: {total_points_value}")
        logger.info(f"  ✅ Average points per winner: {total_points_value / total_winners if total_winners > 0 else 0:.2f}")
        
        logger.info("\n✅ Migration complete! Points have been reset and recalculated.")
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(reset_and_recalculate())
