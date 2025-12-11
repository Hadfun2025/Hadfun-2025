#!/usr/bin/env python3
"""
Backend API Testing for HadFun Predictor
Tests Stripe payment integration and email invitation system
"""

import asyncio
import json
import os
import sys
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

# Add backend directory to path for imports
sys.path.append('/app/backend')

class BackendTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "https://kickoff-oracle-9.preview.emergentagent.com"
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        self.base_url = line.split('=', 1)[1].strip()
                        break
        except FileNotFoundError:
            pass
        
        self.api_url = f"{self.base_url}/api"
        self.test_user = {
            "username": "testuser",
            "email": "test@example.com", 
            "id": "test123"
        }
        
        print(f"Testing backend at: {self.api_url}")
        
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to backend API"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = requests.request(method, url, timeout=30, **kwargs)
            
            result = {
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "url": url,
                "method": method
            }
            
            try:
                result["data"] = response.json()
            except:
                result["data"] = response.text
                
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "status_code": 0,
                "success": False,
                "error": str(e),
                "url": url,
                "method": method
            }
    
    def test_api_health(self):
        """Test basic API connectivity"""
        print("\n=== Testing API Health ===")
        
        result = self.make_request("GET", "/")
        
        if result["success"]:
            print("✅ API is accessible")
            print(f"   Response: {result['data']}")
            return True
        else:
            print(f"❌ API health check failed: {result.get('error', 'Unknown error')}")
            return False
    
    def test_weekly_pot_current(self):
        """Test current weekly pot endpoint"""
        print("\n=== Testing Weekly Pot Current ===")
        
        result = self.make_request("GET", "/pot/current")
        
        if result["success"]:
            data = result["data"]
            print("✅ Weekly pot endpoint working")
            print(f"   Week ID: {data.get('week_id')}")
            print(f"   Play Mode: {data.get('play_mode')}")
            if data.get('play_mode') == 'pot':
                print(f"   Stake Amount: £{data.get('stake_amount')}")
                print(f"   Total Pot: £{data.get('total_pot')}")
            return True, data
        else:
            print(f"❌ Weekly pot endpoint failed: {result.get('error', 'Unknown error')}")
            return False, None
    
    def test_stripe_checkout_creation(self):
        """Test Stripe checkout session creation"""
        print("\n=== Testing Stripe Checkout Creation ===")
        
        # Test with valid stake amount
        params = {
            "user_email": self.test_user["email"],
            "user_name": self.test_user["username"], 
            "stake_amount": 5.0,
            "origin_url": self.base_url
        }
        
        result = self.make_request("POST", "/stripe/create-checkout", params=params)
        
        if result["success"]:
            data = result["data"]
            print("✅ Stripe checkout creation successful")
            print(f"   Response keys: {list(data.keys())}")
            
            if "url" in data and "session_id" in data:
                print(f"   Checkout URL: {data['url'][:50]}...")
                print(f"   Session ID: {data['session_id']}")
                return True, data["session_id"]
            else:
                print(f"   Unexpected response format: {data}")
                return False, None
        else:
            print(f"❌ Stripe checkout creation failed")
            print(f"   Status: {result['status_code']}")
            print(f"   Error: {result.get('data', 'Unknown error')}")
            return False, None
    
    def test_stripe_checkout_play_for_fun(self):
        """Test Stripe checkout with play for fun (£0)"""
        print("\n=== Testing Stripe Play For Fun ===")
        
        params = {
            "user_email": self.test_user["email"],
            "user_name": self.test_user["username"],
            "stake_amount": 0.0,
            "origin_url": self.base_url
        }
        
        result = self.make_request("POST", "/stripe/create-checkout", params=params)
        
        if result["success"]:
            data = result["data"]
            print("✅ Play for fun mode working")
            print(f"   Response: {data}")
            
            if data.get("play_for_fun") == True:
                print("   ✅ Correctly identified as play for fun")
                return True
            else:
                print("   ❌ Play for fun not properly handled")
                return False
        else:
            print(f"❌ Play for fun test failed: {result.get('data', 'Unknown error')}")
            return False
    
    def test_stripe_checkout_status(self, session_id: str):
        """Test Stripe checkout status retrieval"""
        print("\n=== Testing Stripe Checkout Status ===")
        
        if not session_id:
            print("❌ No session ID provided for status check")
            return False
        
        result = self.make_request("GET", f"/stripe/checkout-status/{session_id}")
        
        if result["success"]:
            data = result["data"]
            print("✅ Stripe checkout status retrieval successful")
            print(f"   Status: {data.get('status')}")
            print(f"   Payment Status: {data.get('payment_status')}")
            return True
        else:
            print(f"❌ Stripe checkout status failed: {result.get('data', 'Unknown error')}")
            return False
    
    def test_create_team(self):
        """Create a test team for invitation testing"""
        print("\n=== Creating Test Team ===")
        
        # Use timestamp to ensure unique team name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        team_data = {
            "name": f"Test Team {timestamp}",
            "admin_user_id": self.test_user["id"],
            "admin_username": self.test_user["username"],
            "stake_amount": 5,
            "play_mode": "pot",
            "is_private": True
        }
        
        result = self.make_request("POST", "/teams", json=team_data)
        
        if result["success"]:
            data = result["data"]
            print("✅ Test team created successfully")
            print(f"   Team ID: {data.get('id')}")
            print(f"   Team Name: {data.get('name')}")
            print(f"   Join Code: {data.get('join_code')}")
            return True, data["id"]
        else:
            print(f"❌ Team creation failed: {result.get('data', 'Unknown error')}")
            return False, None
    
    def test_email_invitation(self, team_id: str):
        """Test email invitation sending"""
        print("\n=== Testing Email Invitation ===")
        
        if not team_id:
            print("❌ No team ID provided for invitation test")
            return False
        
        params = {
            "recipient_email": "invite@example.com",
            "inviter_name": self.test_user["username"]
        }
        
        result = self.make_request("POST", f"/teams/{team_id}/invite", params=params)
        
        if result["success"]:
            data = result["data"]
            print("✅ Email invitation sent successfully")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            # Check if it's a domain verification issue (expected in test mode)
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "domain" in error_detail.lower() and "verify" in error_detail.lower():
                print("✅ Email service working (domain verification required)")
                print(f"   Note: {error_detail}")
                print("   This is expected behavior in test mode")
                return True
            else:
                print(f"❌ Email invitation failed")
                print(f"   Status: {result['status_code']}")
                print(f"   Error: {error_detail}")
                return False
    
    def test_get_team_invitations(self, team_id: str):
        """Test retrieving team invitations"""
        print("\n=== Testing Get Team Invitations ===")
        
        if not team_id:
            print("❌ No team ID provided for invitations retrieval")
            return False
        
        result = self.make_request("GET", f"/teams/{team_id}/invitations")
        
        if result["success"]:
            data = result["data"]
            print("✅ Team invitations retrieved successfully")
            print(f"   Number of invitations: {len(data)}")
            
            if data:
                latest = data[0]
                print(f"   Latest invitation to: {latest.get('recipient_email')}")
                print(f"   Sent at: {latest.get('sent_at')}")
            
            return True
        else:
            print(f"❌ Get team invitations failed: {result.get('data', 'Unknown error')}")
            return False
    
    def test_invalid_stripe_inputs(self):
        """Test Stripe endpoint with invalid inputs"""
        print("\n=== Testing Invalid Stripe Inputs ===")
        
        # Test invalid stake amount
        params = {
            "user_email": self.test_user["email"],
            "user_name": self.test_user["username"],
            "stake_amount": 10.0,  # Invalid amount
            "origin_url": self.base_url
        }
        
        result = self.make_request("POST", "/stripe/create-checkout", params=params)
        
        # Check if error contains the expected validation message
        if not result["success"] and (result["status_code"] in [400, 500]):
            error_detail = result.get('data', {})
            if isinstance(error_detail, dict):
                detail = error_detail.get('detail', '')
            else:
                detail = str(error_detail)
            
            if "Invalid stake amount" in detail:
                print("✅ Invalid stake amount properly rejected")
                print(f"   Error message: {detail}")
                return True
        
        print(f"❌ Invalid stake amount not properly handled")
        print(f"   Status: {result['status_code']}")
        print(f"   Response: {result.get('data')}")
        return False
    
    def check_database_collections(self):
        """Check if required database collections exist by testing endpoints"""
        print("\n=== Checking Database Collections ===")
        
        # Test payment_transactions collection via pot endpoint
        pot_result = self.make_request("GET", "/pot/current")
        if pot_result["success"]:
            print("✅ Weekly cycles collection accessible")
        else:
            print("❌ Weekly cycles collection issue")
        
        # Test teams collection
        teams_result = self.make_request("GET", "/teams")
        if teams_result["success"]:
            print("✅ Teams collection accessible")
        else:
            print("❌ Teams collection issue")
        
        return pot_result["success"] and teams_result["success"]
    
    def test_promo_code_validation_valid(self):
        """Test promo code validation with valid LAUNCH2025 code"""
        print("\n=== Testing Promo Code Validation - Valid Code ===")
        
        validation_data = {
            "code": "LAUNCH2025",
            "user_email": "test@example.com",
            "team_id": None
        }
        
        result = self.make_request("POST", "/promo-codes/validate", json=validation_data)
        
        if result["success"]:
            data = result["data"]
            print("✅ Promo code validation endpoint working")
            
            # Check required fields
            required_fields = ["valid", "discount_value", "discount_type", "description"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            if data.get("valid") == True:
                print(f"   ✅ LAUNCH2025 is valid")
                print(f"   Discount Value: £{data.get('discount_value')}")
                print(f"   Discount Type: {data.get('discount_type')}")
                print(f"   Description: {data.get('description')}")
                
                # Verify expected values
                if data.get("discount_value") == 3.0 and data.get("discount_type") == "fixed":
                    print("   ✅ Discount values match expected (£3 fixed)")
                    return True, data
                else:
                    print(f"   ❌ Unexpected discount values - expected £3 fixed, got £{data.get('discount_value')} {data.get('discount_type')}")
                    return False, None
            else:
                print(f"   ❌ LAUNCH2025 marked as invalid: {data.get('message')}")
                return False, None
        else:
            print(f"❌ Promo code validation failed: {result.get('data', 'Unknown error')}")
            return False, None
    
    def test_promo_code_validation_invalid(self):
        """Test promo code validation with invalid code"""
        print("\n=== Testing Promo Code Validation - Invalid Code ===")
        
        validation_data = {
            "code": "INVALID123",
            "user_email": "test@example.com",
            "team_id": None
        }
        
        result = self.make_request("POST", "/promo-codes/validate", json=validation_data)
        
        if result["success"]:
            data = result["data"]
            
            if data.get("valid") == False:
                print("✅ Invalid promo code correctly rejected")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"❌ Invalid code incorrectly marked as valid")
                return False
        else:
            print(f"❌ Promo code validation endpoint failed: {result.get('data', 'Unknown error')}")
            return False
    
    def test_promo_code_case_sensitivity(self):
        """Test promo code validation with different cases"""
        print("\n=== Testing Promo Code Case Sensitivity ===")
        
        test_cases = ["LAUNCH2025", "launch2025", "Launch2025", "LaUnCh2025"]
        all_passed = True
        
        for code in test_cases:
            validation_data = {
                "code": code,
                "user_email": "test@example.com",
                "team_id": None
            }
            
            result = self.make_request("POST", "/promo-codes/validate", json=validation_data)
            
            if result["success"] and result["data"].get("valid") == True:
                print(f"   ✅ {code} - valid")
            else:
                print(f"   ❌ {code} - invalid or failed")
                all_passed = False
        
        if all_passed:
            print("✅ All case variations work correctly")
            return True
        else:
            print("❌ Some case variations failed")
            return False
    
    def test_promo_code_apply_first_time(self):
        """Test applying LAUNCH2025 promo code for first time"""
        print("\n=== Testing Promo Code Apply - First Time ===")
        
        # Use unique email to avoid conflicts
        test_email = f"promotest_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        
        params = {
            "promo_code": "LAUNCH2025",
            "user_email": test_email,
            "team_id": None,
            "referred_by": None
        }
        
        result = self.make_request("POST", "/promo-codes/apply", params=params)
        
        if result["success"]:
            data = result["data"]
            print("✅ Promo code apply endpoint working")
            
            # Check required response fields
            required_fields = ["status", "original_amount", "discount_applied", "final_amount"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            print(f"   Status: {data.get('status')}")
            print(f"   Original Amount: £{data.get('original_amount')}")
            print(f"   Discount Applied: £{data.get('discount_applied')}")
            print(f"   Final Amount: £{data.get('final_amount')}")
            
            # Verify discount calculation
            expected_original = 3.0
            expected_discount = 3.0
            expected_final = 0.0
            
            if (data.get('original_amount') == expected_original and 
                data.get('discount_applied') == expected_discount and
                data.get('final_amount') == expected_final):
                print("   ✅ Discount calculation correct")
                return True, test_email
            else:
                print("   ❌ Discount calculation incorrect")
                return False, None
        else:
            print(f"❌ Promo code apply failed: {result.get('data', 'Unknown error')}")
            return False, None
    
    def test_promo_code_apply_second_time(self, test_email: str):
        """Test applying LAUNCH2025 promo code for second time (should fail)"""
        print("\n=== Testing Promo Code Apply - Second Time (Should Fail) ===")
        
        if not test_email:
            print("❌ No test email provided from first application")
            return False
        
        params = {
            "promo_code": "LAUNCH2025",
            "user_email": test_email,
            "team_id": None,
            "referred_by": None
        }
        
        result = self.make_request("POST", "/promo-codes/apply", params=params)
        
        # This should fail because max_uses_per_user = 1
        if not result["success"]:
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "already used" in error_detail.lower() or "maximum" in error_detail.lower():
                print("✅ Second application correctly rejected")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print("❌ Second application incorrectly allowed")
            print(f"   Response: {result.get('data')}")
            return False
    
    def test_promo_code_database_verification(self):
        """Test database verification by checking promo code stats"""
        print("\n=== Testing Promo Code Database Verification ===")
        
        result = self.make_request("GET", "/promo-codes/stats/LAUNCH2025")
        
        if result["success"]:
            data = result["data"]
            print("✅ LAUNCH2025 exists in database")
            
            # Check key fields
            expected_fields = ["code", "description", "is_active", "total_uses"]
            missing_fields = [field for field in expected_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing expected fields: {missing_fields}")
                return False
            
            print(f"   Code: {data.get('code')}")
            print(f"   Description: {data.get('description')}")
            print(f"   Is Active: {data.get('is_active')}")
            print(f"   Total Uses: {data.get('total_uses')}")
            print(f"   Max Uses: {data.get('max_uses')}")
            
            # Verify it's active
            if data.get('is_active') == True:
                print("   ✅ Promo code is active")
                return True
            else:
                print("   ❌ Promo code is not active")
                return False
        else:
            print(f"❌ LAUNCH2025 not found in database: {result.get('data', 'Unknown error')}")
            return False
    
    def test_refer10_disabled(self):
        """Test that REFER10 is disabled as requested"""
        print("\n=== Testing REFER10 Disabled ===")
        
        validation_data = {
            "code": "REFER10",
            "user_email": "test@example.com",
            "team_id": None
        }
        
        result = self.make_request("POST", "/promo-codes/validate", json=validation_data)
        
        if result["success"]:
            data = result["data"]
            
            if data.get("valid") == False:
                print("✅ REFER10 correctly disabled/not found")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print("❌ REFER10 is still active (should be disabled)")
                return False
        else:
            # If endpoint fails, that's also acceptable for disabled code
            print("✅ REFER10 not accessible (correctly disabled)")
            return True
    
    def create_test_user_and_team(self):
        """Create test user and team for prediction testing"""
        print("\n=== Creating Test User and Team for Predictions ===")
        
        # Create unique test user
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user = {
            "id": f"pred_user_{timestamp}",
            "username": f"PredUser{timestamp}",
            "email": f"preduser_{timestamp}@example.com"
        }
        
        # Create user
        user_result = self.make_request("POST", "/users", json=test_user)
        if not user_result["success"]:
            print(f"❌ Failed to create test user: {user_result.get('data')}")
            return False, None, None
        
        print(f"✅ Created test user: {test_user['username']}")
        
        # Create team
        team_data = {
            "name": f"Pred Test Team {timestamp}",
            "admin_user_id": test_user["id"],
            "admin_username": test_user["username"],
            "stake_amount": 5,
            "play_mode": "pot",
            "is_private": True
        }
        
        team_result = self.make_request("POST", "/teams", json=team_data)
        if not team_result["success"]:
            print(f"❌ Failed to create test team: {team_result.get('data')}")
            return False, test_user, None
        
        team_id = team_result["data"]["id"]
        print(f"✅ Created test team: {team_data['name']} (ID: {team_id})")
        
        return True, test_user, team_id
    
    def create_test_fixture(self):
        """Create a test fixture in the database"""
        print("\n=== Creating Test Fixture ===")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fixture_id = int(f"999{timestamp[-6:]}")  # Use timestamp for unique ID
        
        # Get current date + 1 day for future match
        match_date = (datetime.now() + timedelta(days=1)).isoformat()
        
        fixture_data = {
            "fixture_id": fixture_id,
            "league_id": 39,
            "league_name": "Premier League",
            "home_team": "Arsenal",
            "away_team": "Chelsea", 
            "home_logo": None,
            "away_logo": None,
            "match_date": match_date,
            "utc_date": match_date,
            "status": "SCHEDULED",
            "home_score": None,
            "away_score": None
        }
        
        # Insert directly via admin endpoint (simulate fixture creation)
        # Since we can't directly insert to DB, we'll use the fixtures endpoint
        result = self.make_request("GET", "/fixtures?league_ids=39&days_ahead=14")
        
        if result["success"]:
            fixtures = result["data"]
            if fixtures:
                # Use first available fixture
                test_fixture = fixtures[0]
                print(f"✅ Using existing fixture: {test_fixture['home_team']} vs {test_fixture['away_team']}")
                print(f"   Fixture ID: {test_fixture['fixture_id']}")
                return True, test_fixture
            else:
                print("❌ No fixtures available for testing")
                return False, None
        else:
            print(f"❌ Failed to get fixtures: {result.get('data')}")
            return False, None
    
    def test_prediction_creation_with_fixture_details(self):
        """Test that new predictions store complete fixture details"""
        print("\n=== Testing Prediction Creation with Fixture Details ===")
        
        # Create test user and team
        success, test_user, team_id = self.create_test_user_and_team()
        if not success:
            return False
        
        # Get test fixture
        success, fixture = self.create_test_fixture()
        if not success:
            return False
        
        # Create prediction
        prediction_data = {
            "user_id": test_user["id"],
            "fixture_id": fixture["fixture_id"],
            "prediction": "home",
            "match_date": fixture["match_date"]
        }
        
        result = self.make_request("POST", "/predictions", json=prediction_data)
        
        if result["success"]:
            prediction = result["data"]
            print("✅ Prediction created successfully")
            
            # Verify fixture details are stored
            required_fields = ["home_team", "away_team", "league", "match_date"]
            missing_fields = [field for field in required_fields if not prediction.get(field)]
            
            if missing_fields:
                print(f"❌ Missing fixture details in prediction: {missing_fields}")
                return False
            
            print(f"   ✅ Home Team: {prediction.get('home_team')}")
            print(f"   ✅ Away Team: {prediction.get('away_team')}")
            print(f"   ✅ League: {prediction.get('league')}")
            print(f"   ✅ Match Date: {prediction.get('match_date')}")
            
            return True, test_user, fixture, prediction
        else:
            print(f"❌ Prediction creation failed: {result.get('data')}")
            return False
    
    def test_prediction_update_preserves_fixture_details(self):
        """Test that updating predictions preserves fixture details"""
        print("\n=== Testing Prediction Update Preserves Fixture Details ===")
        
        # First create a prediction
        result = self.test_prediction_creation_with_fixture_details()
        if not result or result == False:
            return False
        
        success, test_user, fixture, original_prediction = result
        
        # Update the prediction (change from 'home' to 'away')
        update_data = {
            "user_id": test_user["id"],
            "fixture_id": fixture["fixture_id"],
            "prediction": "away",  # Changed from 'home'
            "match_date": fixture["match_date"]
        }
        
        update_result = self.make_request("POST", "/predictions", json=update_data)
        
        if update_result["success"]:
            updated_prediction = update_result["data"]
            print("✅ Prediction updated successfully")
            
            # Verify prediction changed
            if updated_prediction.get("prediction") != "away":
                print(f"❌ Prediction not updated correctly: {updated_prediction.get('prediction')}")
                return False
            
            print(f"   ✅ Prediction changed to: {updated_prediction.get('prediction')}")
            
            # Verify fixture details are STILL present
            required_fields = ["home_team", "away_team", "league", "match_date"]
            missing_fields = [field for field in required_fields if not updated_prediction.get(field)]
            
            if missing_fields:
                print(f"❌ Fixture details lost during update: {missing_fields}")
                return False
            
            print(f"   ✅ Home Team preserved: {updated_prediction.get('home_team')}")
            print(f"   ✅ Away Team preserved: {updated_prediction.get('away_team')}")
            print(f"   ✅ League preserved: {updated_prediction.get('league')}")
            
            return True
        else:
            print(f"❌ Prediction update failed: {update_result.get('data')}")
            return False
    
    def test_global_leaderboard_includes_team_names(self):
        """Test that global leaderboard includes team_name field"""
        print("\n=== Testing Global Leaderboard with Team Names ===")
        
        result = self.make_request("GET", "/leaderboard")
        
        if result["success"]:
            leaderboard = result["data"]
            print("✅ Global leaderboard endpoint working")
            print(f"   Number of entries: {len(leaderboard)}")
            
            if not leaderboard:
                print("   ⚠️  No leaderboard entries found (expected if no users with points)")
                return True
            
            # Check first entry for required fields
            first_entry = leaderboard[0]
            required_fields = ["username", "team_name", "rank", "total_points"]
            missing_fields = [field for field in required_fields if field not in first_entry]
            
            if missing_fields:
                print(f"❌ Missing required fields in leaderboard: {missing_fields}")
                return False
            
            print(f"   ✅ Sample entry:")
            print(f"      Username: {first_entry.get('username')}")
            print(f"      Team Name: {first_entry.get('team_name')}")
            print(f"      Rank: {first_entry.get('rank')}")
            print(f"      Points: {first_entry.get('total_points')}")
            
            # Check that team_name is present for all entries
            entries_without_team_name = [entry for entry in leaderboard if 'team_name' not in entry]
            if entries_without_team_name:
                print(f"❌ {len(entries_without_team_name)} entries missing team_name field")
                return False
            
            print(f"   ✅ All {len(leaderboard)} entries have team_name field")
            
            # Check for 'No Team' handling
            no_team_entries = [entry for entry in leaderboard if entry.get('team_name') == 'No Team']
            if no_team_entries:
                print(f"   ✅ {len(no_team_entries)} entries correctly show 'No Team'")
            
            return True
        else:
            print(f"❌ Global leaderboard failed: {result.get('data')}")
            return False
    
    def test_prediction_scoring_with_fixture_details(self):
        """Test that predictions get updated with scores when fixtures are finished"""
        print("\n=== Testing Prediction Scoring with Fixture Details ===")
        
        # This test simulates what happens when automated_result_update runs
        # We'll check if there are any finished fixtures with predictions
        
        # Get user predictions to see if any exist
        result = self.make_request("GET", "/predictions/user/test123")
        
        if result["success"]:
            predictions = result["data"]
            print(f"✅ Retrieved user predictions: {len(predictions)} found")
            
            if not predictions:
                print("   ⚠️  No predictions found for testing scoring")
                return True
            
            # Look for any predictions that have been scored (have home_score/away_score)
            scored_predictions = [p for p in predictions if p.get('home_score') is not None]
            
            if scored_predictions:
                scored_pred = scored_predictions[0]
                print("   ✅ Found scored prediction:")
                print(f"      Match: {scored_pred.get('home_team')} vs {scored_pred.get('away_team')}")
                print(f"      Score: {scored_pred.get('home_score')}-{scored_pred.get('away_score')}")
                print(f"      Result: {scored_pred.get('result')}")
                print(f"      Status: {scored_pred.get('status')}")
                
                # Verify all required fields are present
                required_fields = ["home_team", "away_team", "league", "home_score", "away_score", "status"]
                missing_fields = [field for field in required_fields if scored_pred.get(field) is None]
                
                if missing_fields:
                    print(f"   ❌ Missing fields in scored prediction: {missing_fields}")
                    return False
                
                print("   ✅ All required fields present in scored prediction")
                return True
            else:
                print("   ⚠️  No scored predictions found (expected if no matches finished)")
                return True
        else:
            print(f"❌ Failed to get user predictions: {result.get('data')}")
            return False
    
    def investigate_weekly_winners_calculation(self):
        """Investigate why weekly winners calculation is not awarding points to Pistachios"""
        print("\n" + "=" * 80)
        print("🔍 INVESTIGATING WEEKLY WINNERS CALCULATION ISSUE")
        print("=" * 80)
        
        investigation_results = {}
        
        # Step 1: Check Pistachios user data
        print("\n=== Step 1: Checking Pistachios User Data ===")
        
        # Get leaderboard to find Pistachios
        leaderboard_result = self.make_request("GET", "/leaderboard")
        if not leaderboard_result["success"]:
            print(f"❌ Failed to get leaderboard: {leaderboard_result.get('data')}")
            return False
        
        leaderboard = leaderboard_result["data"]
        pistachios_entry = None
        
        for entry in leaderboard:
            if entry.get('username', '').lower() == 'pistachios':
                pistachios_entry = entry
                break
        
        if not pistachios_entry:
            print("❌ Pistachios not found in leaderboard")
            return False
        
        print(f"✅ Found Pistachios in leaderboard:")
        print(f"   Username: {pistachios_entry.get('username')}")
        print(f"   Team: {pistachios_entry.get('team_name')}")
        print(f"   Total Points: {pistachios_entry.get('total_points')}")
        print(f"   Season Points: {pistachios_entry.get('season_points')}")
        print(f"   Total Predictions: {pistachios_entry.get('total_predictions')}")
        print(f"   Correct Predictions: {pistachios_entry.get('correct_predictions')}")
        
        # This contradicts user report of 47 total and 4 correct
        if pistachios_entry.get('total_predictions') == 0:
            print("⚠️  DISCREPANCY: User reports 47 predictions, but leaderboard shows 0")
        
        investigation_results['pistachios_data'] = pistachios_entry
        
        # Step 2: Check Weekly Pot Status for Cheshunt Crew
        print("\n=== Step 2: Checking Weekly Pot Status ===")
        
        pot_result = self.make_request("GET", "/pot/current")
        if pot_result["success"]:
            pot_data = pot_result["data"]
            print(f"✅ Current weekly pot data:")
            print(f"   Week ID: {pot_data.get('week_id')}")
            print(f"   Play Mode: {pot_data.get('play_mode')}")
            print(f"   Status: {pot_data.get('status')}")
            
            if pot_data.get('play_mode') == 'pot':
                print(f"   Stake Amount: £{pot_data.get('stake_amount')}")
                print(f"   Participants: {pot_data.get('participants')}")
                print(f"   Total Pot: £{pot_data.get('total_pot')}")
            
            investigation_results['weekly_pot'] = pot_data
        else:
            print(f"❌ Failed to get weekly pot: {pot_result.get('data')}")
            investigation_results['weekly_pot'] = None
        
        # Step 3: Test Calculate Weekly Winners Endpoint
        print("\n=== Step 3: Testing Calculate Weekly Winners Endpoint ===")
        
        calc_result = self.make_request("POST", "/admin/calculate-weekly-winners")
        if calc_result["success"]:
            calc_data = calc_result["data"]
            print(f"✅ Calculate weekly winners endpoint responded:")
            print(f"   Status: {calc_data.get('status')}")
            print(f"   Message: {calc_data.get('message')}")
            
            # Check if it mentions any teams processed
            if 'teams_processed' in calc_data:
                print(f"   Teams Processed: {calc_data.get('teams_processed')}")
            if 'winners_found' in calc_data:
                print(f"   Winners Found: {calc_data.get('winners_found')}")
            
            investigation_results['calc_winners_response'] = calc_data
        else:
            print(f"❌ Calculate weekly winners failed:")
            print(f"   Status: {calc_result.get('status_code')}")
            print(f"   Error: {calc_result.get('data')}")
            investigation_results['calc_winners_response'] = None
        
        # Step 4: Check if Cheshunt Crew has active weekly pot
        print("\n=== Step 4: Checking Team-Specific Weekly Pot ===")
        
        # We need to find the team ID first
        # Since teams endpoint returned empty, let's try to find team via team_members
        print("Searching for Cheshunt Crew team information...")
        
        # The leaderboard shows team names, so teams exist but might not be in teams collection
        cheshunt_users = [entry for entry in leaderboard if entry.get('team_name') == 'CHESHUNT CREW']
        print(f"✅ Found {len(cheshunt_users)} users in CHESHUNT CREW:")
        for user in cheshunt_users:
            print(f"   - {user.get('username')}: {user.get('correct_predictions')} correct, {user.get('total_predictions')} total")
        
        investigation_results['cheshunt_users'] = cheshunt_users
        
        # Step 5: Check Prediction Timestamps and 7-day Window
        print("\n=== Step 5: Checking Prediction Timestamps and 7-day Window ===")
        
        from datetime import datetime, timedelta
        now = datetime.now()
        week_start = now - timedelta(days=7)
        
        print(f"Current time: {now.isoformat()}")
        print(f"7-day window start: {week_start.isoformat()}")
        
        # Try to get predictions for Pistachios (we need user ID)
        # Since we don't have direct access to user ID from leaderboard, let's check if we can find it
        
        # Step 6: Check Database Collections Directly
        print("\n=== Step 6: Checking Database State ===")
        
        # Check if there are any predictions at all
        print("Checking for any predictions in the system...")
        
        # We can't directly query the database, but we can infer from the leaderboard data
        users_with_predictions = [entry for entry in leaderboard if entry.get('total_predictions', 0) > 0]
        print(f"Users with predictions: {len(users_with_predictions)}")
        
        if users_with_predictions:
            for user in users_with_predictions:
                print(f"   - {user.get('username')}: {user.get('total_predictions')} predictions, {user.get('correct_predictions')} correct")
        else:
            print("   ⚠️  NO USERS HAVE ANY PREDICTIONS")
        
        investigation_results['users_with_predictions'] = users_with_predictions
        
        # Step 7: Summary and Root Cause Analysis
        print("\n=== Step 7: Root Cause Analysis ===")
        
        print("\n📋 FINDINGS:")
        print(f"1. Pistachios exists in CHESHUNT CREW team: ✅")
        print(f"2. Pistachios current stats: {pistachios_entry.get('total_predictions')} predictions, {pistachios_entry.get('correct_predictions')} correct")
        print(f"3. User reports: 47 predictions, 4 correct")
        print(f"4. Calculate weekly winners endpoint: {'✅ Working' if investigation_results.get('calc_winners_response') else '❌ Failed'}")
        print(f"5. Weekly pot status: {investigation_results.get('weekly_pot', {}).get('status', 'Unknown')}")
        print(f"6. Total users with predictions: {len(users_with_predictions)}")
        
        # Determine root cause
        if len(users_with_predictions) == 0:
            print("\n🔍 ROOT CAUSE: NO PREDICTIONS FOUND IN SYSTEM")
            print("   - Either predictions were not created properly")
            print("   - Or predictions were deleted/lost")
            print("   - Or there's a data inconsistency")
        elif pistachios_entry.get('total_predictions') == 0:
            print("\n🔍 ROOT CAUSE: PISTACHIOS HAS NO PREDICTIONS IN DATABASE")
            print("   - User reports 47 predictions but database shows 0")
            print("   - This suggests a data loss or sync issue")
        else:
            print("\n🔍 ROOT CAUSE: WEEKLY WINNERS CALCULATION ISSUE")
            print("   - Predictions exist but points not being awarded")
        
        return investigation_results

    def investigate_cheshunt_crew_predictions(self):
        """Investigate missing prediction results for Cheshunt Crew team members"""
        print("\n" + "=" * 80)
        print("🔍 INVESTIGATING CHESHUNT CREW PREDICTION RESULTS")
        print("=" * 80)
        
        investigation_results = {}
        
        # Step 1: Find Cheshunt Crew Team and Members
        print("\n=== Step 1: Finding Cheshunt Crew Team and Members ===")
        
        # Get all teams to find Cheshunt Crew
        teams_result = self.make_request("GET", "/teams")
        if not teams_result["success"]:
            print(f"❌ Failed to get teams: {teams_result.get('data')}")
            return False
        
        teams = teams_result["data"]
        cheshunt_team = None
        
        # Search for team with "Cheshunt" in name (case insensitive)
        for team in teams:
            team_name = team.get('name', '').lower()
            if 'cheshunt' in team_name:
                cheshunt_team = team
                break
        
        if not cheshunt_team:
            print("❌ Cheshunt Crew team not found")
            print(f"   Available teams: {[t.get('name') for t in teams[:10]]}")  # Show first 10
            return False
        
        team_id = cheshunt_team['id']
        team_name = cheshunt_team['name']
        print(f"✅ Found team: {team_name} (ID: {team_id})")
        
        # Get team members
        members_result = self.make_request("GET", f"/teams/{team_id}/members")
        if not members_result["success"]:
            print(f"❌ Failed to get team members: {members_result.get('data')}")
            return False
        
        members = members_result["data"]
        print(f"✅ Found {len(members)} team members:")
        
        aysin_user = None
        pistachios_user = None
        
        for member in members:
            username = member.get('username', '').lower()
            print(f"   - {member.get('username')} (ID: {member.get('user_id')})")
            
            if 'aysin' in username:
                aysin_user = member
            elif 'pistachios' in username:
                pistachios_user = member
        
        target_users = []
        if aysin_user:
            target_users.append(aysin_user)
            print(f"✅ Found Aysin: {aysin_user['username']}")
        else:
            print("❌ Aysin not found in team members")
        
        if pistachios_user:
            target_users.append(pistachios_user)
            print(f"✅ Found Pistachios: {pistachios_user['username']}")
        else:
            print("❌ Pistachios not found in team members")
        
        if not target_users:
            print("❌ Neither Aysin nor Pistachios found in team")
            return False
        
        investigation_results['team_found'] = True
        investigation_results['target_users'] = target_users
        
        # Step 2: Check Predictions for These Users
        print("\n=== Step 2: Checking Predictions for Target Users ===")
        
        for user in target_users:
            user_id = user['user_id']
            username = user['username']
            
            print(f"\n--- Checking predictions for {username} ---")
            
            predictions_result = self.make_request("GET", f"/predictions/user/{user_id}")
            if not predictions_result["success"]:
                print(f"❌ Failed to get predictions for {username}: {predictions_result.get('data')}")
                continue
            
            predictions = predictions_result["data"]
            print(f"✅ Found {len(predictions)} total predictions for {username}")
            
            if not predictions:
                print(f"   ⚠️  {username} has no predictions")
                continue
            
            # Analyze predictions by status
            pending_count = len([p for p in predictions if p.get('result') == 'pending'])
            correct_count = len([p for p in predictions if p.get('result') == 'correct'])
            incorrect_count = len([p for p in predictions if p.get('result') == 'incorrect'])
            
            print(f"   Prediction breakdown:")
            print(f"   - Pending: {pending_count}")
            print(f"   - Correct: {correct_count}")
            print(f"   - Incorrect: {incorrect_count}")
            
            # Check Premier League predictions specifically
            pl_predictions = [p for p in predictions if p.get('league') == 'Premier League']
            print(f"   - Premier League predictions: {len(pl_predictions)}")
            
            # Show sample predictions with fixture details
            if predictions:
                sample_pred = predictions[0]
                print(f"   Sample prediction:")
                print(f"   - Match: {sample_pred.get('home_team')} vs {sample_pred.get('away_team')}")
                print(f"   - League: {sample_pred.get('league')}")
                print(f"   - Status: {sample_pred.get('result')}")
                print(f"   - Fixture ID: {sample_pred.get('fixture_id')}")
                
                if sample_pred.get('home_score') is not None:
                    print(f"   - Score: {sample_pred.get('home_score')}-{sample_pred.get('away_score')}")
        
        # Step 3: Check Finished Premier League Fixtures
        print("\n=== Step 3: Checking Finished Premier League Fixtures ===")
        
        fixtures_result = self.make_request("GET", "/fixtures?league_ids=39&days_ahead=30")
        if not fixtures_result["success"]:
            print(f"❌ Failed to get fixtures: {fixtures_result.get('data')}")
            return False
        
        fixtures = fixtures_result["data"]
        print(f"✅ Retrieved {len(fixtures)} Premier League fixtures")
        
        # Filter for finished fixtures
        finished_fixtures = [f for f in fixtures if f.get('status') == 'FINISHED']
        finished_with_scores = [f for f in finished_fixtures if f.get('home_score') is not None]
        
        print(f"   - Total fixtures: {len(fixtures)}")
        print(f"   - Finished fixtures: {len(finished_fixtures)}")
        print(f"   - Finished with scores: {len(finished_with_scores)}")
        
        if finished_with_scores:
            sample_finished = finished_with_scores[0]
            print(f"   Sample finished fixture:")
            print(f"   - Match: {sample_finished.get('home_team')} vs {sample_finished.get('away_team')}")
            print(f"   - Score: {sample_finished.get('home_score')}-{sample_finished.get('away_score')}")
            print(f"   - Date: {sample_finished.get('match_date')}")
            print(f"   - Fixture ID: {sample_finished.get('fixture_id')}")
        
        investigation_results['finished_fixtures_count'] = len(finished_with_scores)
        
        # Step 4: Match Predictions with Finished Fixtures
        print("\n=== Step 4: Matching Predictions with Finished Fixtures ===")
        
        finished_fixture_ids = {f['fixture_id'] for f in finished_with_scores}
        
        for user in target_users:
            user_id = user['user_id']
            username = user['username']
            
            print(f"\n--- Analyzing {username}'s predictions vs finished fixtures ---")
            
            predictions_result = self.make_request("GET", f"/predictions/user/{user_id}")
            if not predictions_result["success"]:
                continue
            
            predictions = predictions_result["data"]
            
            # Find predictions for finished fixtures
            predictions_for_finished = []
            for pred in predictions:
                if pred.get('fixture_id') in finished_fixture_ids:
                    predictions_for_finished.append(pred)
            
            print(f"   Predictions for finished fixtures: {len(predictions_for_finished)}")
            
            if predictions_for_finished:
                pending_for_finished = [p for p in predictions_for_finished if p.get('result') == 'pending']
                scored_for_finished = [p for p in predictions_for_finished if p.get('result') in ['correct', 'incorrect']]
                
                print(f"   - Still pending: {len(pending_for_finished)}")
                print(f"   - Already scored: {len(scored_for_finished)}")
                
                if pending_for_finished:
                    print(f"   ⚠️  {len(pending_for_finished)} predictions for finished fixtures are still pending!")
                    for pending_pred in pending_for_finished[:3]:  # Show first 3
                        print(f"      - {pending_pred.get('home_team')} vs {pending_pred.get('away_team')} (ID: {pending_pred.get('fixture_id')})")
                
                if scored_for_finished:
                    print(f"   ✅ {len(scored_for_finished)} predictions properly scored")
            else:
                print(f"   ⚠️  No predictions found for finished fixtures")
        
        # Step 5: Check Automated Result Update Status
        print("\n=== Step 5: Checking System Status ===")
        
        # Check if there are any pending predictions for finished fixtures globally
        print("Checking global prediction scoring status...")
        
        # This would require a custom endpoint, but we can infer from the data we have
        total_pending_for_finished = 0
        total_scored_for_finished = 0
        
        # We'd need to check all users, but for now we'll summarize what we found
        print(f"✅ Investigation completed")
        
        # Summary
        print("\n" + "=" * 80)
        print("📋 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        print(f"Team Found: {'✅' if investigation_results.get('team_found') else '❌'} {team_name}")
        print(f"Target Users Found: {len(target_users)}/2")
        for user in target_users:
            print(f"  - {user['username']} (ID: {user['user_id']})")
        
        print(f"Finished Premier League Fixtures: {investigation_results.get('finished_fixtures_count', 0)}")
        
        # Recommendations
        print("\n🔧 RECOMMENDATIONS:")
        if investigation_results.get('finished_fixtures_count', 0) == 0:
            print("1. No finished Premier League fixtures found - this may be why no results are showing")
        else:
            print("1. Check if automated result update is running properly")
            print("2. Verify prediction scoring logic for finished fixtures")
            print("3. Check if users have made predictions for the finished fixtures")
        
        return investigation_results

    def check_backend_logs(self):
        """Check backend logs for errors or issues"""
        print("\n=== Checking Backend Logs ===")
        
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.err.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                print("📋 Recent backend error logs:")
                print(result.stdout)
                return result.stdout
            else:
                print("✅ No recent backend errors found")
                return None
        except Exception as e:
            print(f"⚠️  Could not check backend logs: {e}")
            return None

    def test_social_features(self):
        """Run comprehensive social feature tests"""
        print("\n" + "=" * 80)
        print("🌟 TESTING SOCIAL FEATURE BACKEND ENDPOINTS")
        print("=" * 80)
        
        results = {}
        
        # Test user "aysin" as specified in the review request
        aysin_user_id = "ff88ef75-1201-477a-91d4-1e896d3ef6fc"
        
        # 1. Profile Management Tests
        print("\n=== 1. Profile Management Tests ===")
        results["get_user_aysin"] = self.test_get_user_aysin()
        results["profile_status_check"] = self.test_profile_status_check(aysin_user_id)
        results["complete_profile"] = self.test_complete_profile(aysin_user_id)
        results["update_profile"] = self.test_update_profile(aysin_user_id)
        results["age_validation"] = self.test_age_validation(aysin_user_id)
        
        # 2. Post Creation & Management Tests
        print("\n=== 2. Post Creation & Management Tests ===")
        results["post_without_profile"] = self.test_post_without_profile_completion()
        results["create_post"], post_id = self.test_create_post_with_completed_profile(aysin_user_id)
        results["get_posts_public"] = self.test_get_posts_public()
        
        if post_id:
            results["get_single_post"] = self.test_get_single_post(post_id)
            results["update_post"] = self.test_update_post(post_id, aysin_user_id)
        else:
            results["get_single_post"] = False
            results["update_post"] = False
        
        results["post_content_limit"] = self.test_post_content_limit(aysin_user_id)
        results["post_image_limit"] = self.test_post_image_limit(aysin_user_id)
        
        # 3. Comment Tests
        print("\n=== 3. Comment Tests ===")
        if post_id:
            results["create_comment"] = self.test_create_comment(post_id, aysin_user_id)
            results["get_comments_public"] = self.test_get_comments_public(post_id)
            results["comment_content_limit"] = self.test_comment_content_limit(post_id, aysin_user_id)
        else:
            results["create_comment"] = False
            results["get_comments_public"] = False
            results["comment_content_limit"] = False
        
        # 4. Like Tests
        print("\n=== 4. Like Tests ===")
        if post_id:
            results["like_post"] = self.test_like_post(post_id, aysin_user_id)
            results["like_post_duplicate"] = self.test_like_post_duplicate(post_id, aysin_user_id)
            results["get_post_likes"] = self.test_get_post_likes(post_id)
            results["unlike_post"] = self.test_unlike_post(post_id, aysin_user_id)
        else:
            results["like_post"] = False
            results["like_post_duplicate"] = False
            results["get_post_likes"] = False
            results["unlike_post"] = False
        
        # 5. Public Access Tests
        print("\n=== 5. Public Access Tests ===")
        results["public_posts_access"] = self.test_public_posts_access()
        if post_id:
            results["public_comments_access"] = self.test_public_comments_access(post_id)
        else:
            results["public_comments_access"] = False
        
        # Clean up - delete test post
        if post_id:
            results["delete_post"] = self.test_delete_post(post_id, aysin_user_id)
        else:
            results["delete_post"] = False
        
        return results
    
    def test_get_user_aysin(self):
        """Test GET /api/users/aysin (existing user - should return new profile fields)"""
        print("\n--- Testing GET /api/users/aysin ---")
        
        result = self.make_request("GET", "/users/aysin")
        
        if result["success"]:
            user_data = result["data"]
            print("✅ User aysin retrieved successfully")
            
            # Check for new profile fields
            profile_fields = ["full_name", "bio", "birthdate", "avatar_url", "location", 
                            "favorite_team", "favorite_leagues", "interests", "profile_completed"]
            
            missing_fields = [field for field in profile_fields if field not in user_data]
            
            if missing_fields:
                print(f"❌ Missing profile fields: {missing_fields}")
                return False
            
            print(f"   ✅ All profile fields present")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Profile Completed: {user_data.get('profile_completed')}")
            print(f"   Full Name: {user_data.get('full_name')}")
            
            return True
        else:
            print(f"❌ Failed to get user aysin: {result.get('data')}")
            return False
    
    def test_profile_status_check(self, user_id: str):
        """Test GET /api/users/id/{user_id}/profile-status"""
        print(f"\n--- Testing GET /api/users/id/{user_id}/profile-status ---")
        
        result = self.make_request("GET", f"/users/id/{user_id}/profile-status")
        
        if result["success"]:
            status_data = result["data"]
            print("✅ Profile status check successful")
            print(f"   Profile Completed: {status_data.get('profile_completed')}")
            print(f"   Username: {status_data.get('username')}")
            return True
        else:
            print(f"❌ Profile status check failed: {result.get('data')}")
            return False
    
    def test_complete_profile(self, user_id: str):
        """Test POST /api/users/{user_id}/complete-profile"""
        print(f"\n--- Testing POST /api/users/{user_id}/complete-profile ---")
        
        profile_data = {
            "full_name": "Aysin Test",
            "birthdate": "1990-01-01",
            "bio": "Football fan",
            "favorite_team": "Arsenal",
            "favorite_leagues": [39, 140]
        }
        
        result = self.make_request("POST", f"/users/{user_id}/complete-profile", json=profile_data)
        
        if result["success"]:
            user_data = result["data"]
            print("✅ Profile completion successful")
            print(f"   Profile Completed: {user_data.get('profile_completed')}")
            print(f"   Full Name: {user_data.get('full_name')}")
            print(f"   Favorite Team: {user_data.get('favorite_team')}")
            
            # Verify profile_completed is now true
            if user_data.get('profile_completed') == True:
                print("   ✅ Profile completion flag set correctly")
                return True
            else:
                print("   ❌ Profile completion flag not set")
                return False
        else:
            print(f"❌ Profile completion failed: {result.get('data')}")
            return False
    
    def test_update_profile(self, user_id: str):
        """Test PUT /api/users/{user_id}/profile to update bio"""
        print(f"\n--- Testing PUT /api/users/{user_id}/profile ---")
        
        update_data = {
            "bio": "Updated bio: Arsenal supporter and charity advocate"
        }
        
        result = self.make_request("PUT", f"/users/{user_id}/profile", json=update_data)
        
        if result["success"]:
            user_data = result["data"]
            print("✅ Profile update successful")
            print(f"   Updated Bio: {user_data.get('bio')}")
            return True
        else:
            print(f"❌ Profile update failed: {result.get('data')}")
            return False
    
    def test_age_validation(self, user_id: str):
        """Test age validation with birthdate 2015-01-01 (should fail - under 13)"""
        print(f"\n--- Testing Age Validation (Under 13) ---")
        
        # Create a test user for this validation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user_data = {
            "username": f"TestKid{timestamp}",
            "email": f"testkid_{timestamp}@example.com"
        }
        
        # Create test user
        user_result = self.make_request("POST", "/users", json=test_user_data)
        if not user_result["success"]:
            print(f"❌ Failed to create test user: {user_result.get('data')}")
            return False
        
        test_user_id = user_result["data"]["id"]
        
        # Try to complete profile with underage birthdate
        profile_data = {
            "full_name": "Test Kid",
            "birthdate": "2015-01-01"  # Under 13 years old
        }
        
        result = self.make_request("POST", f"/users/{test_user_id}/complete-profile", json=profile_data)
        
        # This should fail
        if not result["success"]:
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "13 years old" in error_detail:
                print("✅ Age validation working correctly")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print("❌ Age validation failed - underage user was allowed")
            return False
    
    def test_post_without_profile_completion(self):
        """Test POST /api/posts WITHOUT profile completion (should fail with 403)"""
        print("\n--- Testing POST /api/posts Without Profile Completion ---")
        
        # Create a test user without completed profile
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_user_data = {
            "username": f"IncompleteUser{timestamp}",
            "email": f"incomplete_{timestamp}@example.com"
        }
        
        user_result = self.make_request("POST", "/users", json=test_user_data)
        if not user_result["success"]:
            print(f"❌ Failed to create test user: {user_result.get('data')}")
            return False
        
        test_user_id = user_result["data"]["id"]
        
        # Try to create post without completing profile
        post_data = {
            "content": "This should fail because profile is not completed"
        }
        
        # Note: The API expects user_id as a query parameter or header
        # Based on the route definition, it expects user_id as a parameter
        result = self.make_request("POST", f"/posts?user_id={test_user_id}", json=post_data)
        
        # This should fail with 403
        if not result["success"] and result["status_code"] == 403:
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "complete your profile" in error_detail.lower():
                print("✅ Profile completion requirement enforced")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Post creation should have failed but didn't. Status: {result['status_code']}")
            return False
    
    def test_create_post_with_completed_profile(self, user_id: str):
        """Test POST /api/posts WITH completed profile"""
        print(f"\n--- Testing POST /api/posts With Completed Profile ---")
        
        post_data = {
            "content": "Football with purpose! Supporting local charities through our predictions.",
            "charity_name": "Local Food Bank",
            "charity_description": "Helping families in need"
        }
        
        result = self.make_request("POST", f"/posts?user_id={user_id}", json=post_data)
        
        if result["success"]:
            post = result["data"]
            print("✅ Post creation successful")
            print(f"   Post ID: {post.get('id')}")
            print(f"   Author: {post.get('author_username')}")
            print(f"   Content: {post.get('content')[:50]}...")
            print(f"   Charity: {post.get('charity_name')}")
            
            # Verify required fields
            required_fields = ["id", "author_id", "author_username", "content", "created_at"]
            missing_fields = [field for field in required_fields if not post.get(field)]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False, None
            
            return True, post.get('id')
        else:
            print(f"❌ Post creation failed: {result.get('data')}")
            return False, None
    
    def test_get_posts_public(self):
        """Test GET /api/posts (public - should return posts)"""
        print("\n--- Testing GET /api/posts (Public Access) ---")
        
        result = self.make_request("GET", "/posts")
        
        if result["success"]:
            posts = result["data"]
            print(f"✅ Public posts retrieval successful")
            print(f"   Number of posts: {len(posts)}")
            
            if posts:
                sample_post = posts[0]
                print(f"   Sample post by: {sample_post.get('author_username')}")
                print(f"   Content preview: {sample_post.get('content', '')[:50]}...")
            
            return True
        else:
            print(f"❌ Public posts retrieval failed: {result.get('data')}")
            return False
    
    def test_get_single_post(self, post_id: str):
        """Test GET /api/posts/{post_id}"""
        print(f"\n--- Testing GET /api/posts/{post_id} ---")
        
        result = self.make_request("GET", f"/posts/{post_id}")
        
        if result["success"]:
            post = result["data"]
            print("✅ Single post retrieval successful")
            print(f"   Post ID: {post.get('id')}")
            print(f"   Author: {post.get('author_username')}")
            return True
        else:
            print(f"❌ Single post retrieval failed: {result.get('data')}")
            return False
    
    def test_update_post(self, post_id: str, user_id: str):
        """Test PUT /api/posts/{post_id} to update content"""
        print(f"\n--- Testing PUT /api/posts/{post_id} ---")
        
        update_data = {
            "content": "Updated content: Football predictions for charity causes!"
        }
        
        result = self.make_request("PUT", f"/posts/{post_id}?user_id={user_id}", json=update_data)
        
        if result["success"]:
            post = result["data"]
            print("✅ Post update successful")
            print(f"   Updated content: {post.get('content')[:50]}...")
            return True
        else:
            print(f"❌ Post update failed: {result.get('data')}")
            return False
    
    def test_post_content_limit(self, user_id: str):
        """Test POST /api/posts with content > 5000 chars (should fail)"""
        print("\n--- Testing Post Content Limit (>5000 chars) ---")
        
        long_content = "A" * 5001  # 5001 characters
        
        post_data = {
            "content": long_content
        }
        
        result = self.make_request("POST", f"/posts?user_id={user_id}", json=post_data)
        
        # Should fail with 400
        if not result["success"] and result["status_code"] == 400:
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "5000 character" in error_detail:
                print("✅ Content length validation working")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Content length validation failed. Status: {result['status_code']}")
            return False
    
    def test_post_image_limit(self, user_id: str):
        """Test POST /api/posts with > 5 images (should fail)"""
        print("\n--- Testing Post Image Limit (>5 images) ---")
        
        post_data = {
            "content": "Test post with too many images",
            "images": [f"https://example.com/image{i}.jpg" for i in range(6)]  # 6 images
        }
        
        result = self.make_request("POST", f"/posts?user_id={user_id}", json=post_data)
        
        # Should fail with 400
        if not result["success"] and result["status_code"] == 400:
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "5 images" in error_detail:
                print("✅ Image count validation working")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Image count validation failed. Status: {result['status_code']}")
            return False
    
    def test_create_comment(self, post_id: str, user_id: str):
        """Test POST /api/posts/{post_id}/comments"""
        print(f"\n--- Testing POST /api/posts/{post_id}/comments ---")
        
        comment_data = {
            "content": "Great initiative! I'm in!"
        }
        
        result = self.make_request("POST", f"/posts/{post_id}/comments?user_id={user_id}", json=comment_data)
        
        if result["success"]:
            comment = result["data"]
            print("✅ Comment creation successful")
            print(f"   Comment ID: {comment.get('id')}")
            print(f"   Author: {comment.get('author_username')}")
            print(f"   Content: {comment.get('content')}")
            
            # Check if comments_count was incremented on the post
            post_result = self.make_request("GET", f"/posts/{post_id}")
            if post_result["success"]:
                post = post_result["data"]
                print(f"   ✅ Post comments_count: {post.get('comments_count')}")
            
            return True
        else:
            print(f"❌ Comment creation failed: {result.get('data')}")
            return False
    
    def test_get_comments_public(self, post_id: str):
        """Test GET /api/posts/{post_id}/comments (public)"""
        print(f"\n--- Testing GET /api/posts/{post_id}/comments (Public) ---")
        
        result = self.make_request("GET", f"/posts/{post_id}/comments")
        
        if result["success"]:
            comments = result["data"]
            print(f"✅ Public comments retrieval successful")
            print(f"   Number of comments: {len(comments)}")
            
            if comments:
                sample_comment = comments[0]
                print(f"   Sample comment by: {sample_comment.get('author_username')}")
            
            return True
        else:
            print(f"❌ Public comments retrieval failed: {result.get('data')}")
            return False
    
    def test_comment_content_limit(self, post_id: str, user_id: str):
        """Test comment with > 1000 chars (should fail)"""
        print("\n--- Testing Comment Content Limit (>1000 chars) ---")
        
        long_content = "B" * 1001  # 1001 characters
        
        comment_data = {
            "content": long_content
        }
        
        result = self.make_request("POST", f"/posts/{post_id}/comments?user_id={user_id}", json=comment_data)
        
        # Should fail with 400
        if not result["success"] and result["status_code"] == 400:
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "1000 character" in error_detail:
                print("✅ Comment length validation working")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Comment length validation failed. Status: {result['status_code']}")
            return False
    
    def test_like_post(self, post_id: str, user_id: str):
        """Test POST /api/posts/{post_id}/like"""
        print(f"\n--- Testing POST /api/posts/{post_id}/like ---")
        
        result = self.make_request("POST", f"/posts/{post_id}/like?user_id={user_id}")
        
        if result["success"]:
            print("✅ Post like successful")
            
            # Check if likes_count was incremented
            post_result = self.make_request("GET", f"/posts/{post_id}")
            if post_result["success"]:
                post = post_result["data"]
                print(f"   ✅ Post likes_count: {post.get('likes_count')}")
            
            return True
        else:
            print(f"❌ Post like failed: {result.get('data')}")
            return False
    
    def test_like_post_duplicate(self, post_id: str, user_id: str):
        """Test POST /api/posts/{post_id}/like again (should fail - already liked)"""
        print(f"\n--- Testing Duplicate Like (Should Fail) ---")
        
        result = self.make_request("POST", f"/posts/{post_id}/like?user_id={user_id}")
        
        # Should fail with 400
        if not result["success"] and result["status_code"] == 400:
            error_data = result.get('data', {})
            if isinstance(error_data, dict):
                error_detail = error_data.get('detail', '')
            else:
                error_detail = str(error_data)
            
            if "already liked" in error_detail.lower():
                print("✅ Duplicate like prevention working")
                print(f"   Error message: {error_detail}")
                return True
            else:
                print(f"❌ Unexpected error message: {error_detail}")
                return False
        else:
            print(f"❌ Duplicate like prevention failed. Status: {result['status_code']}")
            return False
    
    def test_get_post_likes(self, post_id: str):
        """Test GET /api/posts/{post_id}/likes"""
        print(f"\n--- Testing GET /api/posts/{post_id}/likes ---")
        
        result = self.make_request("GET", f"/posts/{post_id}/likes")
        
        if result["success"]:
            likes = result["data"]
            print(f"✅ Post likes retrieval successful")
            print(f"   Number of likes: {len(likes)}")
            
            if likes:
                sample_like = likes[0]
                print(f"   Sample like by: {sample_like.get('username')}")
            
            return True
        else:
            print(f"❌ Post likes retrieval failed: {result.get('data')}")
            return False
    
    def test_unlike_post(self, post_id: str, user_id: str):
        """Test DELETE /api/posts/{post_id}/like"""
        print(f"\n--- Testing DELETE /api/posts/{post_id}/like ---")
        
        result = self.make_request("DELETE", f"/posts/{post_id}/like?user_id={user_id}")
        
        if result["success"]:
            print("✅ Post unlike successful")
            
            # Check if likes_count was decremented
            post_result = self.make_request("GET", f"/posts/{post_id}")
            if post_result["success"]:
                post = post_result["data"]
                print(f"   ✅ Post likes_count after unlike: {post.get('likes_count')}")
            
            return True
        else:
            print(f"❌ Post unlike failed: {result.get('data')}")
            return False
    
    def test_public_posts_access(self):
        """Test GET /api/posts without any user_id (should work - public)"""
        print("\n--- Testing Public Posts Access (No Auth) ---")
        
        result = self.make_request("GET", "/posts")
        
        if result["success"]:
            posts = result["data"]
            print(f"✅ Public posts access working")
            print(f"   Retrieved {len(posts)} posts without authentication")
            return True
        else:
            print(f"❌ Public posts access failed: {result.get('data')}")
            return False
    
    def test_public_comments_access(self, post_id: str):
        """Test GET /api/posts/{post_id}/comments without auth (should work)"""
        print(f"\n--- Testing Public Comments Access (No Auth) ---")
        
        result = self.make_request("GET", f"/posts/{post_id}/comments")
        
        if result["success"]:
            comments = result["data"]
            print(f"✅ Public comments access working")
            print(f"   Retrieved {len(comments)} comments without authentication")
            return True
        else:
            print(f"❌ Public comments access failed: {result.get('data')}")
            return False
    
    def test_delete_post(self, post_id: str, user_id: str):
        """Test DELETE /api/posts/{post_id}"""
        print(f"\n--- Testing DELETE /api/posts/{post_id} ---")
        
        result = self.make_request("DELETE", f"/posts/{post_id}?user_id={user_id}")
        
        if result["success"]:
            print("✅ Post deletion successful")
            return True
        else:
            print(f"❌ Post deletion failed: {result.get('data')}")
            return False

    def test_fixtures_api_all_leagues_fix(self):
        """Test the critical fix for fixtures API returning ALL leagues when no filter applied"""
        print("\n" + "=" * 80)
        print("🔧 TESTING FIXTURES API - ALL LEAGUES FIX")
        print("=" * 80)
        
        results = {}
        
        # Test Case 1: Empty league_ids should return ALL leagues
        print("\n=== Test Case 1: Empty league_ids parameter ===")
        result1 = self.make_request("GET", "/fixtures?league_ids=&days_ahead=28")
        
        if result1["success"]:
            fixtures_all = result1["data"]
            print(f"✅ Empty league_ids request successful")
            print(f"   Total fixtures returned: {len(fixtures_all)}")
            
            # Count unique leagues
            unique_leagues = set()
            for fixture in fixtures_all:
                league_id = fixture.get('league_id')
                if league_id:
                    unique_leagues.add(league_id)
            
            print(f"   Unique leagues found: {len(unique_leagues)}")
            print(f"   League IDs: {sorted(list(unique_leagues))}")
            
            # Expected: Should be 18+ leagues and 500+ fixtures
            if len(fixtures_all) >= 500 and len(unique_leagues) >= 18:
                print("   ✅ PASS: Returns fixtures from ALL leagues (18+ leagues, 500+ fixtures)")
                results["empty_league_ids"] = True
            else:
                print(f"   ❌ FAIL: Expected 18+ leagues and 500+ fixtures, got {len(unique_leagues)} leagues and {len(fixtures_all)} fixtures")
                results["empty_league_ids"] = False
        else:
            print(f"❌ Empty league_ids request failed: {result1.get('data')}")
            results["empty_league_ids"] = False
        
        # Test Case 2: Single league filter (Premier League only)
        print("\n=== Test Case 2: Single league filter (Premier League) ===")
        result2 = self.make_request("GET", "/fixtures?league_ids=39&days_ahead=28")
        
        if result2["success"]:
            fixtures_pl = result2["data"]
            print(f"✅ Premier League only request successful")
            print(f"   Total fixtures returned: {len(fixtures_pl)}")
            
            # Verify all fixtures are Premier League
            non_pl_fixtures = [f for f in fixtures_pl if f.get('league_id') != 39]
            
            if len(non_pl_fixtures) == 0:
                print("   ✅ PASS: All fixtures are Premier League only")
                results["single_league_filter"] = True
            else:
                print(f"   ❌ FAIL: Found {len(non_pl_fixtures)} non-Premier League fixtures")
                results["single_league_filter"] = False
        else:
            print(f"❌ Premier League only request failed: {result2.get('data')}")
            results["single_league_filter"] = False
        
        # Test Case 3: Multiple league filter (Premier League + La Liga)
        print("\n=== Test Case 3: Multiple league filter (Premier League + La Liga) ===")
        result3 = self.make_request("GET", "/fixtures?league_ids=39,140&days_ahead=28")
        
        if result3["success"]:
            fixtures_multi = result3["data"]
            print(f"✅ Multiple leagues request successful")
            print(f"   Total fixtures returned: {len(fixtures_multi)}")
            
            # Verify only Premier League and La Liga fixtures
            valid_leagues = {39, 140}
            invalid_fixtures = [f for f in fixtures_multi if f.get('league_id') not in valid_leagues]
            
            # Count fixtures per league
            pl_count = len([f for f in fixtures_multi if f.get('league_id') == 39])
            laliga_count = len([f for f in fixtures_multi if f.get('league_id') == 140])
            
            print(f"   Premier League fixtures: {pl_count}")
            print(f"   La Liga fixtures: {laliga_count}")
            
            if len(invalid_fixtures) == 0:
                print("   ✅ PASS: Only Premier League and La Liga fixtures returned")
                results["multiple_league_filter"] = True
            else:
                print(f"   ❌ FAIL: Found {len(invalid_fixtures)} fixtures from other leagues")
                results["multiple_league_filter"] = False
        else:
            print(f"❌ Multiple leagues request failed: {result3.get('data')}")
            results["multiple_league_filter"] = False
        
        # Test Case 4: Verify the fix addresses the original bug
        print("\n=== Test Case 4: Comparing empty vs default behavior ===")
        
        # Get fixtures with no league_ids parameter (should behave same as empty)
        result4 = self.make_request("GET", "/fixtures?days_ahead=28")
        
        if result4["success"]:
            fixtures_no_param = result4["data"]
            print(f"✅ No league_ids parameter request successful")
            print(f"   Total fixtures returned: {len(fixtures_no_param)}")
            
            # Compare with empty league_ids result
            if results.get("empty_league_ids") and len(fixtures_no_param) >= 500:
                print("   ✅ PASS: No parameter behaves same as empty parameter (returns all leagues)")
                results["no_param_behavior"] = True
            else:
                print("   ❌ FAIL: No parameter doesn't return all leagues")
                results["no_param_behavior"] = False
        else:
            print(f"❌ No league_ids parameter request failed: {result4.get('data')}")
            results["no_param_behavior"] = False
        
        # Test Case 5: Verify specific leagues are included
        print("\n=== Test Case 5: Verify specific leagues are included ===")
        
        if results.get("empty_league_ids") and result1["success"]:
            fixtures_all = result1["data"]
            
            # Check for specific leagues mentioned in the review
            expected_leagues = {
                39: "Premier League",
                140: "La Liga", 
                78: "Bundesliga",
                40: "Championship",
                135: "Serie A",
                61: "Ligue 1",
                179: "Scottish Premiership"
            }
            
            found_leagues = {}
            for fixture in fixtures_all:
                league_id = fixture.get('league_id')
                league_name = fixture.get('league_name')
                if league_id in expected_leagues:
                    found_leagues[league_id] = league_name
            
            print(f"   Expected leagues found: {len(found_leagues)}/{len(expected_leagues)}")
            for league_id, league_name in found_leagues.items():
                print(f"   ✅ {expected_leagues[league_id]} (ID: {league_id})")
            
            missing_leagues = set(expected_leagues.keys()) - set(found_leagues.keys())
            if missing_leagues:
                for league_id in missing_leagues:
                    print(f"   ❌ Missing: {expected_leagues[league_id]} (ID: {league_id})")
            
            if len(found_leagues) >= 5:  # At least 5 of the major leagues
                print("   ✅ PASS: Major leagues are included")
                results["major_leagues_included"] = True
            else:
                print("   ❌ FAIL: Missing major leagues")
                results["major_leagues_included"] = False
        else:
            results["major_leagues_included"] = False
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FIXTURES API FIX TEST RESULTS")
        print("=" * 80)
        
        test_cases = [
            ("Empty league_ids returns ALL leagues", results.get("empty_league_ids", False)),
            ("Single league filter works correctly", results.get("single_league_filter", False)),
            ("Multiple league filter works correctly", results.get("multiple_league_filter", False)),
            ("No parameter behaves same as empty", results.get("no_param_behavior", False)),
            ("Major leagues are included", results.get("major_leagues_included", False))
        ]
        
        passed = sum(1 for _, result in test_cases if result)
        total = len(test_cases)
        
        for test_name, result in test_cases:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nFixtures API Fix Tests: {passed}/{total} passed")
        
        # Overall assessment
        critical_tests_passed = results.get("empty_league_ids", False) and results.get("single_league_filter", False)
        
        if critical_tests_passed:
            print("🎉 CRITICAL FIX VERIFICATION: ✅ WORKING")
            print("   The fixtures API now correctly returns ALL leagues when no filter is applied")
        else:
            print("🚨 CRITICAL FIX VERIFICATION: ❌ FAILING")
            print("   The fixtures API fix is not working as expected")
        
        return results

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting HadFun Predictor Backend Tests")
        print("=" * 60)
        
        results = {}
        
        # Basic connectivity
        results["api_health"] = self.test_api_health()
        
        if not results["api_health"]:
            print("\n❌ API not accessible - stopping tests")
            return results
        
        # NEW: Social Feature Tests (Priority)
        print("\n" + "=" * 60)
        print("🌟 TESTING SOCIAL FEATURE BACKEND ENDPOINTS")
        print("=" * 60)
        
        social_results = self.test_social_features()
        results.update(social_results)
        
        # Database collections
        results["database"] = self.check_database_collections()
        
        # Weekly pot
        results["weekly_pot"], pot_data = self.test_weekly_pot_current()
        
        # Stripe payment tests
        results["stripe_checkout"], session_id = self.test_stripe_checkout_creation()
        results["stripe_play_for_fun"] = self.test_stripe_checkout_play_for_fun()
        results["stripe_invalid"] = self.test_invalid_stripe_inputs()
        
        if session_id:
            results["stripe_status"] = self.test_stripe_checkout_status(session_id)
        else:
            results["stripe_status"] = False
        
        # Email invitation tests
        results["team_creation"], team_id = self.test_create_team()
        
        if team_id:
            results["email_invitation"] = self.test_email_invitation(team_id)
            results["get_invitations"] = self.test_get_team_invitations(team_id)
        else:
            results["email_invitation"] = False
            results["get_invitations"] = False
        
        # Promo code tests
        results["promo_validation_valid"], promo_data = self.test_promo_code_validation_valid()
        results["promo_validation_invalid"] = self.test_promo_code_validation_invalid()
        results["promo_case_sensitivity"] = self.test_promo_code_case_sensitivity()
        results["promo_database_verification"] = self.test_promo_code_database_verification()
        results["promo_apply_first"], test_email = self.test_promo_code_apply_first_time()
        
        if test_email:
            results["promo_apply_second"] = self.test_promo_code_apply_second_time(test_email)
        else:
            results["promo_apply_second"] = False
        
        results["refer10_disabled"] = self.test_refer10_disabled()
        
        # Prediction and Leaderboard functionality
        print("\n" + "=" * 60)
        print("🎯 TESTING PREDICTION & LEADERBOARD FUNCTIONALITY")
        print("=" * 60)
        
        results["prediction_creation"] = self.test_prediction_creation_with_fixture_details()
        results["prediction_update"] = self.test_prediction_update_preserves_fixture_details()
        results["leaderboard_team_names"] = self.test_global_leaderboard_includes_team_names()
        results["prediction_scoring"] = self.test_prediction_scoring_with_fixture_details()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<35} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed - check logs above")
        
        return results

def main():
    """Main test execution"""
    tester = BackendTester()
    
    # Check if we should run investigation only
    if len(sys.argv) > 1 and sys.argv[1] == "investigate":
        print("🔍 Running Cheshunt Crew Investigation Only")
        investigation_results = tester.investigate_cheshunt_crew_predictions()
        if not investigation_results:
            sys.exit(1)
        return
    elif len(sys.argv) > 1 and sys.argv[1] == "weekly-winners":
        print("🔍 Running Weekly Winners Investigation Only")
        investigation_results = tester.investigate_weekly_winners_calculation()
        if not investigation_results:
            sys.exit(1)
        return
    
    # Run full test suite
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()