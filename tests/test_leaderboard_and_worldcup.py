"""
Backend API Tests for Football Prediction App
Tests:
1. Leaderboard API - /api/teams/{team_id}/leaderboard/by-league
2. World Cup Groups API - /api/world-cup/groups
3. Scoring system verification (3 pts sole winner, 1 pt tied)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from review request
TEST_TEAM_ID = "adf96b37-1fe9-420e-b0d1-9ce2424b3598"
TEST_TEAM_NAME = "Cheshunt Crew"
TEST_USER = "aysin"


class TestLeaderboardAPI:
    """Tests for the new leaderboard by-league endpoint"""
    
    def test_leaderboard_endpoint_returns_200(self):
        """Test that leaderboard endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"✅ Leaderboard endpoint returns 200 OK")
    
    def test_leaderboard_returns_list(self):
        """Test that leaderboard returns a list of league data"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✅ Leaderboard returns list with {len(data)} leagues")
    
    def test_leaderboard_structure_per_league(self):
        """Test that each league entry has correct structure"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) == 0:
            pytest.skip("No league data available - team may have no predictions")
        
        for league_data in data:
            # Check required fields
            assert 'league_name' in league_data, "Missing league_name field"
            assert 'matchdays' in league_data, "Missing matchdays field"
            assert 'leaderboard' in league_data, "Missing leaderboard field"
            
            # Validate types
            assert isinstance(league_data['league_name'], str), "league_name should be string"
            assert isinstance(league_data['matchdays'], list), "matchdays should be list"
            assert isinstance(league_data['leaderboard'], list), "leaderboard should be list"
            
            print(f"✅ League '{league_data['league_name']}' has correct structure")
    
    def test_leaderboard_user_entry_structure(self):
        """Test that each user entry in leaderboard has correct structure"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) == 0:
            pytest.skip("No league data available")
        
        for league_data in data:
            for entry in league_data['leaderboard']:
                # Check required fields for user entry
                assert 'username' in entry, "Missing username field"
                assert 'total_points' in entry, "Missing total_points field"
                assert 'total_correct' in entry, "Missing total_correct field"
                assert 'total_predictions' in entry, "Missing total_predictions field"
                assert 'matchday_scores' in entry, "Missing matchday_scores field"
                assert 'rank' in entry, "Missing rank field"
                
                # Validate types
                assert isinstance(entry['username'], str), "username should be string"
                assert isinstance(entry['total_points'], int), "total_points should be int"
                assert isinstance(entry['rank'], int), "rank should be int"
                assert isinstance(entry['matchday_scores'], dict), "matchday_scores should be dict"
                
                print(f"✅ User '{entry['username']}' entry has correct structure")
    
    def test_matchday_scores_structure(self):
        """Test that matchday_scores has correct structure with scoring fields"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) == 0:
            pytest.skip("No league data available")
        
        for league_data in data:
            for entry in league_data['leaderboard']:
                for md, md_score in entry['matchday_scores'].items():
                    # Check required fields for matchday score
                    assert 'points' in md_score, f"Missing points in matchday {md}"
                    assert 'correct' in md_score, f"Missing correct in matchday {md}"
                    assert 'total' in md_score, f"Missing total in matchday {md}"
                    assert 'is_winner' in md_score, f"Missing is_winner in matchday {md}"
                    assert 'is_tie' in md_score, f"Missing is_tie in matchday {md}"
                    
                    # Validate types
                    assert isinstance(md_score['points'], int), "points should be int"
                    assert isinstance(md_score['correct'], int), "correct should be int"
                    assert isinstance(md_score['total'], int), "total should be int"
                    assert isinstance(md_score['is_winner'], bool), "is_winner should be bool"
                    assert isinstance(md_score['is_tie'], bool), "is_tie should be bool"
                    
                    print(f"✅ Matchday {md} score structure is correct")
    
    def test_scoring_logic_3_pts_sole_winner(self):
        """Test that sole winner gets 3 points"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        
        sole_winner_found = False
        for league_data in data:
            for entry in league_data['leaderboard']:
                for md, md_score in entry['matchday_scores'].items():
                    if md_score['is_winner'] and not md_score['is_tie']:
                        # Sole winner should have 3 points
                        assert md_score['points'] == 3, f"Sole winner should have 3 pts, got {md_score['points']}"
                        sole_winner_found = True
                        print(f"✅ Sole winner '{entry['username']}' in matchday {md} has 3 points")
        
        if not sole_winner_found:
            print("⚠️ No sole winner found in data - scoring logic not fully testable")
    
    def test_scoring_logic_1_pt_tied_winner(self):
        """Test that tied winners get 1 point each"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        
        tied_winner_found = False
        for league_data in data:
            for entry in league_data['leaderboard']:
                for md, md_score in entry['matchday_scores'].items():
                    if md_score['is_winner'] and md_score['is_tie']:
                        # Tied winner should have 1 point
                        assert md_score['points'] == 1, f"Tied winner should have 1 pt, got {md_score['points']}"
                        tied_winner_found = True
                        print(f"✅ Tied winner '{entry['username']}' in matchday {md} has 1 point")
        
        if not tied_winner_found:
            print("⚠️ No tied winner found in data - tie scoring logic not fully testable")
    
    def test_scoring_logic_0_pts_non_winner(self):
        """Test that non-winners get 0 points"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        
        for league_data in data:
            for entry in league_data['leaderboard']:
                for md, md_score in entry['matchday_scores'].items():
                    if not md_score['is_winner']:
                        # Non-winner should have 0 points
                        assert md_score['points'] == 0, f"Non-winner should have 0 pts, got {md_score['points']}"
                        print(f"✅ Non-winner '{entry['username']}' in matchday {md} has 0 points")
    
    def test_leaderboard_sorted_by_points(self):
        """Test that leaderboard is sorted by total_points descending"""
        response = requests.get(f"{BASE_URL}/api/teams/{TEST_TEAM_ID}/leaderboard/by-league")
        assert response.status_code == 200
        data = response.json()
        
        for league_data in data:
            leaderboard = league_data['leaderboard']
            if len(leaderboard) > 1:
                for i in range(len(leaderboard) - 1):
                    current_pts = leaderboard[i]['total_points']
                    next_pts = leaderboard[i + 1]['total_points']
                    assert current_pts >= next_pts, f"Leaderboard not sorted: {current_pts} < {next_pts}"
                print(f"✅ League '{league_data['league_name']}' leaderboard is sorted correctly")
    
    def test_invalid_team_id_returns_empty(self):
        """Test that invalid team ID returns empty list (not error)"""
        response = requests.get(f"{BASE_URL}/api/teams/invalid-team-id-12345/leaderboard/by-league")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Should return list even for invalid team"
        assert len(data) == 0, "Should return empty list for invalid team"
        print("✅ Invalid team ID returns empty list")


class TestWorldCupGroupsAPI:
    """Tests for World Cup 2026 groups endpoint"""
    
    def test_world_cup_groups_returns_200(self):
        """Test that world cup groups endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/world-cup/groups")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✅ World Cup groups endpoint returns 200 OK")
    
    def test_world_cup_groups_returns_list(self):
        """Test that world cup groups returns a list"""
        response = requests.get(f"{BASE_URL}/api/world-cup/groups")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"✅ World Cup groups returns list with {len(data)} groups")
    
    def test_world_cup_has_12_groups(self):
        """Test that World Cup 2026 has exactly 12 groups (A-L)"""
        response = requests.get(f"{BASE_URL}/api/world-cup/groups")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 12, f"Expected 12 groups for WC 2026, got {len(data)}"
        print("✅ World Cup 2026 has 12 groups")
    
    def test_world_cup_groups_a_to_l(self):
        """Test that groups are named A through L"""
        response = requests.get(f"{BASE_URL}/api/world-cup/groups")
        assert response.status_code == 200
        data = response.json()
        
        expected_groups = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        actual_groups = sorted([g.get('group') or g.get('group_name') for g in data])
        
        assert actual_groups == expected_groups, f"Expected groups A-L, got {actual_groups}"
        print("✅ World Cup groups are A through L")
    
    def test_world_cup_group_structure(self):
        """Test that each group has correct structure"""
        response = requests.get(f"{BASE_URL}/api/world-cup/groups")
        assert response.status_code == 200
        data = response.json()
        
        for group in data:
            # Check required fields
            assert 'group' in group or 'group_name' in group, "Missing group identifier"
            assert 'teams' in group, "Missing teams field"
            
            # Validate teams is a list
            assert isinstance(group['teams'], list), "teams should be a list"
            
            # Each group should have 4 teams
            assert len(group['teams']) == 4, f"Group {group.get('group', group.get('group_name'))} should have 4 teams, got {len(group['teams'])}"
            
            print(f"✅ Group {group.get('group', group.get('group_name'))} has correct structure with 4 teams")
    
    def test_world_cup_group_name_field(self):
        """Test that group_name field is present (normalized for frontend)"""
        response = requests.get(f"{BASE_URL}/api/world-cup/groups")
        assert response.status_code == 200
        data = response.json()
        
        for group in data:
            assert 'group_name' in group, f"Missing group_name field in group {group}"
            print(f"✅ Group {group['group_name']} has group_name field")


class TestLeaguesAPI:
    """Tests for leagues endpoint"""
    
    def test_leagues_returns_200(self):
        """Test that leagues endpoint returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/leagues")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ Leagues endpoint returns 200 OK")
    
    def test_leagues_includes_world_cup(self):
        """Test that leagues list includes World Cup"""
        response = requests.get(f"{BASE_URL}/api/leagues")
        assert response.status_code == 200
        data = response.json()
        
        world_cup_found = any(l.get('name') == 'World Cup' or l.get('id') == 1 for l in data)
        assert world_cup_found, "World Cup should be in leagues list"
        print("✅ World Cup is in leagues list")


class TestHealthAndBasicEndpoints:
    """Basic health and connectivity tests"""
    
    def test_api_root_returns_200(self):
        """Test that API root returns 200"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✅ API root returns 200 OK")
    
    def test_user_endpoint(self):
        """Test that user endpoint works for test user"""
        response = requests.get(f"{BASE_URL}/api/users/{TEST_USER}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get('username') == TEST_USER, f"Expected username {TEST_USER}"
        print(f"✅ User endpoint returns data for {TEST_USER}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
