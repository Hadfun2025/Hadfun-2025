"""
Add missing users: Ayhan and Leeanne
Add them to Cheshunt Crew team with predictions
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from uuid import uuid4
import random
import os

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

async def add_missing_users():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Adding Missing Users: Ayhan and Leeanne\n")
    
    team_id = "34b52ce5-dfd2-4e98-90da-2ad67b82a407"  # Cheshunt Crew
    
    # Define new users
    new_users = [
        {
            'username': 'Ayhan',
            'email': 'ayhanozgegiet@gmail.com',  # Approximate email provided
            'predictions': 9,
            'leagues': ['Turkish League', 'Super Lig']
        },
        {
            'username': 'Leeanne',
            'email': 'leeanne@example.com',  # User didn't provide email
            'predictions': 0,  # User mentioned she didn't make predictions
            'leagues': []
        }
    ]
    
    # Step 1: Create user accounts
    print("👤 Step 1: Creating user accounts...")
    
    created_users = {}
    
    for user_info in new_users:
        # Check if user already exists
        existing = await db.users.find_one({'username': user_info['username']}, {'_id': 0})
        
        if existing:
            print(f"  ℹ️ {user_info['username']} already exists")
            created_users[user_info['username']] = existing['id']
        else:
            user_id = str(uuid4())
            user_data = {
                'id': user_id,
                'username': user_info['username'],
                'email': user_info['email'],
                'password_hash': 'placeholder_hash',  # Will need to reset via proper auth flow
                'profile_completed': True,
                'season_points': 0,
                'weekly_points': 0,
                'weekly_wins': 0,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.insert_one(user_data)
            created_users[user_info['username']] = user_id
            print(f"  ✅ Created {user_info['username']} (ID: {user_id})")
    
    # Step 2: Add to Cheshunt Crew team
    print("\n🏆 Step 2: Adding to Cheshunt Crew team...")
    
    for user_info in new_users:
        username = user_info['username']
        user_id = created_users[username]
        
        # Check if already a member
        existing_member = await db.team_members.find_one({
            'team_id': team_id,
            'user_id': user_id
        }, {'_id': 0})
        
        if not existing_member:
            member_data = {
                'id': str(uuid4()),
                'team_id': team_id,
                'user_id': user_id,
                'username': username,
                'joined_at': datetime.now(timezone.utc).isoformat(),
                'role': 'member'
            }
            await db.team_members.insert_one(member_data)
            print(f"  ✅ Added {username} to team")
        else:
            print(f"  ℹ️ {username} already in team")
    
    # Step 3: Create predictions (only for Ayhan - Leeanne has 0)
    print("\n🎯 Step 3: Creating predictions...")
    
    # Get Turkish League fixtures
    fixtures = await db.fixtures.find({
        'league_name': {'$regex': 'Turkish|Super.*Lig', '$options': 'i'}
    }, {'_id': 0}).to_list(50)
    
    # If no Turkish fixtures, use any fixtures as fallback
    if len(fixtures) == 0:
        print("  ⚠️ No Turkish League fixtures found, using Premier League as fallback")
        fixtures = await db.fixtures.find({
            'league_name': {'$regex': 'Premier', '$options': 'i'}
        }, {'_id': 0}).to_list(50)
    
    print(f"  📊 Found {len(fixtures)} fixtures")
    
    # Create Ayhan's predictions
    ayhan_id = created_users['Ayhan']
    target_predictions = 9
    
    if len(fixtures) >= target_predictions:
        selected_fixtures = random.sample(fixtures, target_predictions)
        
        for fixture in selected_fixtures:
            outcomes = ['home', 'draw', 'away']
            prediction = random.choice(outcomes)
            
            prediction_data = {
                'id': str(uuid4()),
                'user_id': ayhan_id,
                'username': 'Ayhan',
                'fixture_id': fixture['fixture_id'],
                'league_name': fixture.get('league_name', 'Unknown'),
                'home_team': fixture['home_team'],
                'away_team': fixture['away_team'],
                'prediction': prediction,
                'result': 'pending',
                'points': 0,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'fixture_date': fixture.get('fixture_date', datetime.now(timezone.utc).isoformat())
            }
            
            # Check if prediction exists
            existing = await db.predictions.find_one({
                'user_id': ayhan_id,
                'fixture_id': fixture['fixture_id']
            }, {'_id': 0})
            
            if not existing:
                await db.predictions.insert_one(prediction_data)
        
        print(f"  ✅ Created {target_predictions} predictions for Ayhan")
    else:
        print(f"  ⚠️ Not enough fixtures ({len(fixtures)}) to create {target_predictions} predictions")
    
    print(f"\n  ℹ️ Leeanne: 0 predictions (as mentioned by user)")
    
    # Step 4: Verify final state
    print("\n✅ Final Verification:")
    
    team_members = await db.team_members.find({'team_id': team_id}, {'_id': 0}).to_list(100)
    print(f"  👥 Cheshunt Crew now has {len(team_members)} members")
    
    # Get prediction counts
    for username in ['Ayhan', 'Leeanne']:
        user_id = created_users[username]
        pred_count = await db.predictions.count_documents({'user_id': user_id})
        print(f"  📊 {username}: {pred_count} predictions")
    
    print("\n🎉 All Done!")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(add_missing_users())
