#!/usr/bin/env python3
"""
Test email functionality only
"""

import requests
from datetime import datetime

def test_email_invitation():
    base_url = "https://kickoff-oracle-9.preview.emergentagent.com/api"
    
    # Create a test team first
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    team_data = {
        "name": f"Email Test Team {timestamp}",
        "admin_user_id": "test123",
        "admin_username": "testuser",
        "stake_amount": 5,
        "play_mode": "pot",
        "is_private": True
    }
    
    print("Creating test team...")
    team_response = requests.post(f"{base_url}/teams", json=team_data)
    
    if team_response.status_code != 200:
        print(f"❌ Team creation failed: {team_response.text}")
        return
    
    team_id = team_response.json()["id"]
    print(f"✅ Team created: {team_id}")
    
    # Test email invitation
    print("Testing email invitation...")
    params = {
        "recipient_email": "test@emergentagent.com",
        "inviter_name": "testuser"
    }
    
    email_response = requests.post(f"{base_url}/teams/{team_id}/invite", params=params)
    
    print(f"Status: {email_response.status_code}")
    print(f"Response: {email_response.text}")
    
    if email_response.status_code == 200:
        print("✅ Email invitation successful!")
    else:
        print("❌ Email invitation failed")

if __name__ == "__main__":
    test_email_invitation()