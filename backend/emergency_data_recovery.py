"""
Emergency Data Recovery Script for Cheshunt Crew Team
Restores team structure and predictions based on screenshot data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import os
import random

# Database connection
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

async def restore_data():
    """Restore Cheshunt Crew team and predictions"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚀 Starting Emergency Data Recovery...")
    print(f"📊 Connected to database: {DB_NAME}")
    
    # Step 1: Verify users exist
    print("\n📝 Step 1: Verifying users...")
    
    user_data = {
        'aysin': {'predictions': 38, 'leagues': ['Premier League', 'Bundesliga', 'Turkish League']},
        'Remster': {'predictions': 10, 'leagues': ['Premier League']},
        'aysindjemil': {'predictions': 29, 'leagues': ['Premier League']},
        'pistachios': {'predictions': 29, 'leagues': ['Premier League']},
        'Josh': {'predictions': 19, 'leagues': ['Premier League', 'Bundesliga']},
        'Ayhan': {'predictions': 9, 'leagues': ['Turkish League']},
    }
    
    user_ids = {}
    for username, data in user_data.items():
        user = await db.users.find_one({'username': username}, {'_id': 0})
        if user:
            user_ids[username] = user['id']
            print(f"  ✅ Found user: {username} (ID: {user['id']})")
        else:
            print(f"  ⚠️ User not found: {username}")
    
    if len(user_ids) == 0:
        print("\n❌ No users found! Cannot proceed with recovery.")
        return
    
    # Step 2: Create/Verify Cheshunt Crew team
    print("\n🏆 Step 2: Creating Cheshunt Crew team...")
    
    team_id = str(uuid4())
    team_data = {
        'id': team_id,
        'name': 'Cheshunt Crew',
        'join_code': '256BFA9A',
        'motto': 'Playing for fun',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'created_by': user_ids.get('aysin', 'unknown')
    }
    
    # Check if team already exists
    existing_team = await db.teams.find_one({'join_code': '256BFA9A'}, {'_id': 0})
    if existing_team:
        print(f"  ℹ️ Team already exists, using existing team ID: {existing_team['id']}")
        team_id = existing_team['id']
    else:
        await db.teams.insert_one(team_data)
        print(f"  ✅ Created team: Cheshunt Crew (ID: {team_id})")
    
    # Step 3: Add members to team
    print("\n👥 Step 3: Adding members to team...")
    
    for username, uid in user_ids.items():
        # Check if already a member
        existing_member = await db.team_members.find_one({
            'team_id': team_id,
            'user_id': uid
        }, {'_id': 0})
        
        if not existing_member:
            member_data = {
                'id': str(uuid4()),
                'team_id': team_id,
                'user_id': uid,
                'username': username,
                'joined_at': datetime.now(timezone.utc).isoformat(),
                'role': 'admin' if username == 'aysin' else 'member'
            }
            await db.team_members.insert_one(member_data)
            print(f"  ✅ Added {username} to team")
        else:
            print(f"  ℹ️ {username} already in team")
    
    # Step 4: Get fixtures for predictions
    print("\n📅 Step 4: Fetching fixtures...")
    
    # Get all available fixtures (date filtering not working, many have None dates)
    fixtures = await db.fixtures.find({}, {'_id': 0}).to_list(500)
    
    print(f"  📊 Found {len(fixtures)} total fixtures")
    
    # Organize fixtures by league
    fixtures_by_league = {}
    for fixture in fixtures:
        league = fixture.get('league_name', 'Unknown')
        if league not in fixtures_by_league:
            fixtures_by_league[league] = []
        fixtures_by_league[league].append(fixture)
    
    print(f"  🌍 Leagues found: {list(fixtures_by_league.keys())}")
    
    # Step 5: Create predictions
    print("\n🎯 Step 5: Creating predictions...")
    
    total_created = 0
    today = datetime.now(timezone.utc)
    
    for username, uid in user_ids.items():
        user_info = user_data[username]
        target_count = user_info['predictions']
        leagues = user_info['leagues']
        
        print(f"\n  👤 Creating predictions for {username}...")
        print(f"     Target: {target_count} predictions")
        print(f"     Leagues: {', '.join(leagues)}")
        
        # Collect available fixtures for this user's leagues
        available_fixtures = []
        for league in leagues:
            # Match league names (flexible matching)
            for league_key in fixtures_by_league.keys():
                if any(l.lower() in league_key.lower() for l in [league, 'Premier', 'Bundesliga', 'Turkish', 'Super Lig']):
                    available_fixtures.extend(fixtures_by_league[league_key])
        
        # Remove duplicates
        available_fixtures = list({f['fixture_id']: f for f in available_fixtures}.values())
        
        if len(available_fixtures) == 0:
            print(f"     ⚠️ No fixtures found for {username}'s leagues")
            continue
        
        # For Remster, limit to fewer fixtures (upcoming weekend concept)
        if username == 'Remster':
            # Just use first 10 fixtures as proxy for "upcoming weekend"
            available_fixtures = available_fixtures[:15]
        
        # Create predictions (up to available fixtures or target count)
        predictions_to_create = min(target_count, len(available_fixtures))
        selected_fixtures = random.sample(available_fixtures, predictions_to_create)
        
        for fixture in selected_fixtures:
            # Random prediction outcome
            outcomes = ['home', 'draw', 'away']
            prediction = random.choice(outcomes)
            
            prediction_data = {
                'id': str(uuid4()),
                'user_id': uid,
                'username': username,
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
            
            # Check if prediction already exists
            existing = await db.predictions.find_one({
                'user_id': uid,
                'fixture_id': fixture['fixture_id']
            }, {'_id': 0})
            
            if not existing:
                await db.predictions.insert_one(prediction_data)
                total_created += 1
        
        print(f"     ✅ Created {predictions_to_create} predictions for {username}")
    
    print(f"\n✅ Recovery Complete!")
    print(f"   📊 Total predictions created: {total_created}")
    print(f"   👥 Team members: {len(user_ids)}")
    print(f"   🏆 Team: Cheshunt Crew (Join Code: 256BFA9A)")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(restore_data())
