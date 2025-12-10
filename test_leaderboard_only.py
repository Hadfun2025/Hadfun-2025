#!/usr/bin/env python3
"""
Simple test for leaderboard team_name functionality
"""

import requests
import json

def test_leaderboard_team_names():
    """Test that global leaderboard includes team_name field"""
    print("=== Testing Global Leaderboard with Team Names ===")
    
    base_url = "https://leaguepicks-1.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    try:
        response = requests.get(f"{api_url}/leaderboard", timeout=30)
        
        if response.status_code == 200:
            leaderboard = response.json()
            print(f"✅ Global leaderboard endpoint working")
            print(f"   Number of entries: {len(leaderboard)}")
            
            if not leaderboard:
                print("   ⚠️  No leaderboard entries found")
                return True
            
            # Check first entry for required fields
            first_entry = leaderboard[0]
            print(f"   First entry keys: {list(first_entry.keys())}")
            
            # Check if team_name field exists
            if 'team_name' in first_entry:
                print(f"   ✅ team_name field present: '{first_entry['team_name']}'")
                
                # Check all entries
                entries_with_team_name = [entry for entry in leaderboard if 'team_name' in entry]
                print(f"   ✅ {len(entries_with_team_name)}/{len(leaderboard)} entries have team_name field")
                
                return True
            else:
                print(f"   ❌ team_name field missing from leaderboard entry")
                print(f"   Available fields: {list(first_entry.keys())}")
                return False
        else:
            print(f"❌ Global leaderboard failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing leaderboard: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_leaderboard_team_names()
    if not success:
        exit(1)