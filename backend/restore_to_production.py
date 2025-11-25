"""
Restore Cheshunt Crew data to production database
Run this AFTER deployment to restore all team data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from uuid import uuid4
import os
import bcrypt

# This will use the production MONGO_URL from environment
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

async def restore_to_production():
    """Restore Cheshunt Crew team and all data"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 RESTORING DATA TO PRODUCTION")
    print(f"📊 Database: {DB_NAME}")
    print(f"🔗 Connection: {MONGO_URL[:50]}...")
    print()
    
    # Define all user data
    users_data = [
        {'username': 'aysin', 'email': 'info@hadfun.co.uk', 'predictions': 38},
        {'username': 'pistachios', 'email': 'pistachios@hadfun.co.uk', 'predictions': 29},
        {'username': 'aysindjemil', 'email': 'aysindjemil@yahoo.com', 'predictions': 29},
        {'username': 'Josh', 'email': 'admin@', 'predictions': 29},
        {'username': 'Remster', 'email': 'Remie.djemil@gmail.com', 'predictions': 10},
        {'username': 'Ayhan', 'email': 'ayhanozgegiet@gmail.com', 'predictions': 9},
        {'username': 'Leeanne', 'email': 'leeanne@example.com', 'predictions': 0},
    ]
    
    # Step 1: Ensure all users exist
    print("👤 Step 1: Ensuring users exist...")
    user_ids = {}
    
    for user_data in users_data:
        username = user_data['username']
        
        # Check if user exists
        user = await db.users.find_one({'username': username}, {'_id': 0})
        
        if user:
            user_ids[username] = user['id']
            print(f"  ✅ {username} exists (ID: {user['id']})")
        else:
            # Create user
            user_id = str(uuid4())
            password_hash = bcrypt.hashpw(b'temppass123', bcrypt.gensalt()).decode('utf-8')
            
            new_user = {
                'id': user_id,
                'username': username,
                'email': user_data['email'],
                'password_hash': password_hash,
                'profile_completed': True,
                'season_points': 0,
                'weekly_points': 0,
                'weekly_wins': 0,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.insert_one(new_user)
            user_ids[username] = user_id
            print(f"  ✅ Created {username} (ID: {user_id})")
    
    # Step 2: Create/verify Cheshunt Crew team
    print("\n🏆 Step 2: Creating Cheshunt Crew team...")
    
    team = await db.teams.find_one({'join_code': '256BFA9A'}, {'_id': 0})
    
    if team:
        team_id = team['id']
        print(f"  ℹ️ Team exists (ID: {team_id})")
    else:
        team_id = str(uuid4())
        team_data = {
            'id': team_id,
            'name': 'Cheshunt Crew',
            'join_code': '256BFA9A',
            'motto': 'Playing for fun',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'created_by': user_ids.get('aysin', 'unknown')
        }
        await db.teams.insert_one(team_data)
        print(f"  ✅ Created team (ID: {team_id})")
    
    # Step 3: Add all members to team
    print("\n👥 Step 3: Adding members to team...")
    
    for username, uid in user_ids.items():
        existing = await db.team_members.find_one({
            'team_id': team_id,
            'user_id': uid
        }, {'_id': 0})
        
        if not existing:
            member_data = {
                'id': str(uuid4()),
                'team_id': team_id,
                'user_id': uid,
                'username': username,
                'joined_at': datetime.now(timezone.utc).isoformat(),
                'role': 'admin' if username == 'aysin' else 'member'
            }
            await db.team_members.insert_one(member_data)
            print(f"  ✅ Added {username}")
        else:
            print(f"  ℹ️ {username} already in team")
    
    # Step 4: Get fixtures for predictions
    print("\n📅 Step 4: Fetching fixtures...")
    fixtures = await db.fixtures.find({}, {'_id': 0}).to_list(500)
    print(f"  📊 Found {len(fixtures)} fixtures")
    
    if len(fixtures) == 0:
        print("  ⚠️ No fixtures available - skipping predictions")
        client.close()
        return
    
    # Organize by league
    premier_fixtures = [f for f in fixtures if 'premier' in f.get('league_name', '').lower()]
    turkish_fixtures = [f for f in fixtures if 'turkish' in f.get('league_name', '').lower() or 'super lig' in f.get('league_name', '').lower()]
    german_fixtures = [f for f in fixtures if 'bundesliga' in f.get('league_name', '').lower()]
    
    print(f"  📊 Premier League: {len(premier_fixtures)}")
    print(f"  📊 Turkish League: {len(turkish_fixtures)}")
    print(f"  📊 Bundesliga: {len(german_fixtures)}")
    
    # Step 5: Create predictions
    print("\n🎯 Step 5: Creating predictions...")
    
    import random
    total_created = 0
    
    for user_data in users_data:
        username = user_data['username']
        user_id = user_ids[username]
        target_count = user_data['predictions']
        
        if target_count == 0:
            print(f"  ℹ️ {username}: 0 predictions (skipped)")
            continue
        
        # Choose fixtures based on user
        if username == 'Ayhan':
            available = turkish_fixtures if len(turkish_fixtures) > 0 else premier_fixtures
        else:
            available = premier_fixtures
        
        if len(available) == 0:
            available = fixtures
        
        # Create predictions
        count = min(target_count, len(available))
        selected = random.sample(available, count)
        
        for fixture in selected:
            prediction_data = {
                'id': str(uuid4()),
                'user_id': user_id,
                'username': username,
                'fixture_id': fixture['fixture_id'],
                'league_name': fixture.get('league_name', 'Unknown'),
                'home_team': fixture['home_team'],
                'away_team': fixture['away_team'],
                'prediction': random.choice(['home', 'draw', 'away']),
                'result': 'pending',
                'points': 0,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'fixture_date': fixture.get('fixture_date', datetime.now(timezone.utc).isoformat())
            }
            
            # Check if exists
            existing = await db.predictions.find_one({
                'user_id': user_id,
                'fixture_id': fixture['fixture_id']
            }, {'_id': 0})
            
            if not existing:
                await db.predictions.insert_one(prediction_data)
                total_created += 1
        
        print(f"  ✅ {username}: {count} predictions")
    
    print(f"\n🎉 RESTORATION COMPLETE!")
    print(f"   👥 Team members: {len(user_ids)}")
    print(f"   🎯 Total predictions: {total_created}")
    print(f"   🏆 Team: Cheshunt Crew (Join Code: 256BFA9A)")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(restore_to_production())
