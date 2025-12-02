#!/usr/bin/env python3
"""
Check database state after testing
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

sys.path.append('/app/backend')

async def check_database():
    # Connect to MongoDB
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    print("🔍 Checking Database Collections")
    print("=" * 50)
    
    # Check payment_transactions
    payment_count = await db.payment_transactions.count_documents({})
    print(f"Payment Transactions: {payment_count}")
    
    if payment_count > 0:
        latest_payment = await db.payment_transactions.find_one({}, sort=[("created_at", -1)])
        print(f"  Latest payment: {latest_payment.get('user_email')} - £{latest_payment.get('amount')} - {latest_payment.get('payment_status')}")
    
    # Check team_invitations
    invitation_count = await db.team_invitations.count_documents({})
    print(f"Team Invitations: {invitation_count}")
    
    # Check teams
    team_count = await db.teams.count_documents({})
    print(f"Teams: {team_count}")
    
    if team_count > 0:
        latest_team = await db.teams.find_one({}, sort=[("created_at", -1)])
        print(f"  Latest team: {latest_team.get('name')} - {latest_team.get('join_code')}")
    
    # Check weekly_cycles
    cycle_count = await db.weekly_cycles.count_documents({})
    print(f"Weekly Cycles: {cycle_count}")
    
    if cycle_count > 0:
        current_cycle = await db.weekly_cycles.find_one({}, sort=[("week_start", -1)])
        print(f"  Current cycle: {current_cycle.get('week_id')} - £{current_cycle.get('total_pot', 0)} pot")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_database())