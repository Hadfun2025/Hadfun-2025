#!/usr/bin/env python3
"""
Script to find and remove duplicate predictions
A duplicate is when the same user has multiple predictions for the same fixture_id
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


async def remove_duplicates():
    """Find and remove duplicate predictions"""
    
    try:
        logger.info("=== CHECKING FOR DUPLICATE PREDICTIONS ===\n")
        
        # Get all predictions
        predictions = await db.predictions.find({}, {"_id": 0}).to_list(10000)
        logger.info(f"Total predictions: {len(predictions)}")
        
        # Group by (user_id, fixture_id) to find duplicates
        seen = {}
        to_delete = []
        
        for pred in predictions:
            key = (pred['user_id'], pred['fixture_id'])
            
            if key in seen:
                # This is a duplicate - keep the first one, mark this for deletion
                logger.info(f"Found duplicate: {pred.get('username')} - Fixture {pred['fixture_id']}")
                logger.info(f"  First: {seen[key].get('league', 'N/A')}")
                logger.info(f"  Duplicate: {pred.get('league', 'N/A')}")
                to_delete.append(pred['id'])
            else:
                seen[key] = pred
        
        logger.info(f"\nFound {len(to_delete)} duplicate predictions to remove")
        
        if to_delete:
            # Ask for confirmation
            print(f"\n⚠️  About to delete {len(to_delete)} duplicate predictions")
            print("This will keep only ONE prediction per (user, fixture) combination")
            response = input("Proceed with deletion? (yes/no): ")
            
            if response.lower() == 'yes':
                result = await db.predictions.delete_many({"id": {"$in": to_delete}})
                logger.info(f"✅ Deleted {result.deleted_count} duplicate predictions")
                
                # Verify
                remaining = await db.predictions.count_documents({})
                logger.info(f"Remaining predictions: {remaining}")
            else:
                logger.info("❌ Deletion cancelled")
        else:
            logger.info("✅ No duplicates found - database is clean!")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(remove_duplicates())
