#!/usr/bin/env python3
"""
Focused Social Feature Testing
Tests the specific social feature endpoints that were failing
"""

import requests
import json
from datetime import datetime

class SocialFeatureTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = "https://gameforecast-4.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        
        # Test user from review request
        self.aysin_user_id = "ff88ef75-1201-477a-91d4-1e896d3ef6fc"
        
        print(f"Testing social features at: {self.api_url}")
        
    def make_request(self, method: str, endpoint: str, **kwargs):
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
    
    def test_profile_status_fix(self):
        """Test the profile status endpoint that was failing"""
        print("\n=== Testing Profile Status Fix ===")
        
        result = self.make_request("GET", f"/users/{self.aysin_user_id}/profile-status")
        
        if result["success"]:
            status_data = result["data"]
            print("✅ Profile status check working")
            print(f"   Profile Completed: {status_data.get('profile_completed')}")
            print(f"   Username: {status_data.get('username')}")
            return True
        else:
            print(f"❌ Profile status check failed: {result.get('data')}")
            return False
    
    def test_like_functionality(self):
        """Test the like functionality that was failing"""
        print("\n=== Testing Like Functionality ===")
        
        # First create a test post
        post_data = {
            "content": "Test post for like functionality"
        }
        
        create_result = self.make_request("POST", f"/posts?user_id={self.aysin_user_id}", json=post_data)
        
        if not create_result["success"]:
            print(f"❌ Failed to create test post: {create_result.get('data')}")
            return False
        
        post_id = create_result["data"]["id"]
        print(f"✅ Created test post: {post_id}")
        
        # Test like functionality
        like_result = self.make_request("POST", f"/posts/{post_id}/like?user_id={self.aysin_user_id}")
        
        if like_result["success"]:
            print("✅ Post like successful")
            
            # Test duplicate like (should fail)
            duplicate_result = self.make_request("POST", f"/posts/{post_id}/like?user_id={self.aysin_user_id}")
            
            if not duplicate_result["success"] and duplicate_result["status_code"] == 400:
                print("✅ Duplicate like prevention working")
                
                # Test unlike
                unlike_result = self.make_request("DELETE", f"/posts/{post_id}/like?user_id={self.aysin_user_id}")
                
                if unlike_result["success"]:
                    print("✅ Post unlike successful")
                    
                    # Clean up - delete test post
                    delete_result = self.make_request("DELETE", f"/posts/{post_id}?user_id={self.aysin_user_id}")
                    if delete_result["success"]:
                        print("✅ Test post cleaned up")
                    
                    return True
                else:
                    print(f"❌ Post unlike failed: {unlike_result.get('data')}")
                    return False
            else:
                print(f"❌ Duplicate like prevention failed: {duplicate_result.get('data')}")
                return False
        else:
            print(f"❌ Post like failed: {like_result.get('data')}")
            return False
    
    def test_all_social_endpoints(self):
        """Test all social feature endpoints comprehensively"""
        print("\n" + "=" * 60)
        print("🌟 FOCUSED SOCIAL FEATURE TESTING")
        print("=" * 60)
        
        results = {}
        
        # 1. Profile Status Fix
        results["profile_status"] = self.test_profile_status_fix()
        
        # 2. Like Functionality
        results["like_functionality"] = self.test_like_functionality()
        
        # 3. Test all endpoints with aysin user
        print("\n=== Testing All Social Endpoints ===")
        
        # Get user aysin
        user_result = self.make_request("GET", "/users/aysin")
        results["get_user"] = user_result["success"]
        if user_result["success"]:
            print("✅ GET /users/aysin working")
        else:
            print(f"❌ GET /users/aysin failed: {user_result.get('data')}")
        
        # Get profile status
        status_result = self.make_request("GET", f"/users/{self.aysin_user_id}/profile-status")
        results["profile_status_endpoint"] = status_result["success"]
        if status_result["success"]:
            print("✅ GET /users/{user_id}/profile-status working")
        else:
            print(f"❌ GET /users/{{user_id}}/profile-status failed: {status_result.get('data')}")
        
        # Update profile
        profile_update = {"bio": "Updated bio for testing"}
        update_result = self.make_request("PUT", f"/users/{self.aysin_user_id}/profile", json=profile_update)
        results["update_profile"] = update_result["success"]
        if update_result["success"]:
            print("✅ PUT /users/{user_id}/profile working")
        else:
            print(f"❌ PUT /users/{{user_id}}/profile failed: {update_result.get('data')}")
        
        # Create post
        post_data = {"content": "Comprehensive test post for social features"}
        post_result = self.make_request("POST", f"/posts?user_id={self.aysin_user_id}", json=post_data)
        results["create_post"] = post_result["success"]
        post_id = None
        
        if post_result["success"]:
            post_id = post_result["data"]["id"]
            print(f"✅ POST /posts working - Created post {post_id}")
        else:
            print(f"❌ POST /posts failed: {post_result.get('data')}")
        
        # Get posts (public)
        posts_result = self.make_request("GET", "/posts")
        results["get_posts"] = posts_result["success"]
        if posts_result["success"]:
            print(f"✅ GET /posts working - Retrieved {len(posts_result['data'])} posts")
        else:
            print(f"❌ GET /posts failed: {posts_result.get('data')}")
        
        if post_id:
            # Get single post
            single_post_result = self.make_request("GET", f"/posts/{post_id}")
            results["get_single_post"] = single_post_result["success"]
            if single_post_result["success"]:
                print("✅ GET /posts/{post_id} working")
            else:
                print(f"❌ GET /posts/{{post_id}} failed: {single_post_result.get('data')}")
            
            # Create comment
            comment_data = {"content": "Test comment for comprehensive testing"}
            comment_result = self.make_request("POST", f"/posts/{post_id}/comments?user_id={self.aysin_user_id}", json=comment_data)
            results["create_comment"] = comment_result["success"]
            if comment_result["success"]:
                print("✅ POST /posts/{post_id}/comments working")
            else:
                print(f"❌ POST /posts/{{post_id}}/comments failed: {comment_result.get('data')}")
            
            # Get comments (public)
            comments_result = self.make_request("GET", f"/posts/{post_id}/comments")
            results["get_comments"] = comments_result["success"]
            if comments_result["success"]:
                print(f"✅ GET /posts/{{post_id}}/comments working - Retrieved {len(comments_result['data'])} comments")
            else:
                print(f"❌ GET /posts/{{post_id}}/comments failed: {comments_result.get('data')}")
            
            # Like post
            like_result = self.make_request("POST", f"/posts/{post_id}/like?user_id={self.aysin_user_id}")
            results["like_post"] = like_result["success"]
            if like_result["success"]:
                print("✅ POST /posts/{post_id}/like working")
            else:
                print(f"❌ POST /posts/{{post_id}}/like failed: {like_result.get('data')}")
            
            # Get likes
            likes_result = self.make_request("GET", f"/posts/{post_id}/likes")
            results["get_likes"] = likes_result["success"]
            if likes_result["success"]:
                print(f"✅ GET /posts/{{post_id}}/likes working - Retrieved {len(likes_result['data'])} likes")
            else:
                print(f"❌ GET /posts/{{post_id}}/likes failed: {likes_result.get('data')}")
            
            # Unlike post
            unlike_result = self.make_request("DELETE", f"/posts/{post_id}/like?user_id={self.aysin_user_id}")
            results["unlike_post"] = unlike_result["success"]
            if unlike_result["success"]:
                print("✅ DELETE /posts/{post_id}/like working")
            else:
                print(f"❌ DELETE /posts/{{post_id}}/like failed: {unlike_result.get('data')}")
            
            # Clean up - delete post
            delete_result = self.make_request("DELETE", f"/posts/{post_id}?user_id={self.aysin_user_id}")
            results["delete_post"] = delete_result["success"]
            if delete_result["success"]:
                print("✅ DELETE /posts/{post_id} working")
            else:
                print(f"❌ DELETE /posts/{{post_id}} failed: {delete_result.get('data')}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SOCIAL FEATURE TEST RESULTS")
        print("=" * 60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<30} {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All social feature tests passed!")
        else:
            print("⚠️  Some social feature tests failed")
        
        return results

def main():
    """Main test execution"""
    tester = SocialFeatureTester()
    results = tester.test_all_social_endpoints()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        exit(1)

if __name__ == "__main__":
    main()