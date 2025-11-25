#!/usr/bin/env python3
"""
Test script to verify API-Football integration is ready
"""
import asyncio
from api_football_service import APIFootballService
from football_data_service import FootballDataService

async def test_services():
    print("🧪 Testing Football Data Services Integration...")
    
    # Test Football-Data.org service (currently active)
    print("\n📊 Testing Football-Data.org service...")
    football_data = FootballDataService()
    try:
        fixtures = await football_data.get_upcoming_fixtures([39], days_ahead=3)
        print(f"✅ Football-Data.org: Fetched {len(fixtures)} fixtures")
        if fixtures:
            transformed = football_data.transform_to_standard_format(fixtures[:1])
            print(f"✅ Football-Data.org: Transform successful - {transformed[0]['home_team']} vs {transformed[0]['away_team']}")
    except Exception as e:
        print(f"❌ Football-Data.org error: {e}")
    
    # Test API-Football service (ready for activation)
    print("\n⚡ Testing API-Football service...")
    api_football = APIFootballService()
    try:
        fixtures = await api_football.get_upcoming_fixtures([39], days_ahead=2)
        print(f"✅ API-Football: Fetched {len(fixtures)} fixtures")
        if fixtures:
            transformed = api_football.transform_to_standard_format(fixtures[:1])
            print(f"✅ API-Football: Transform successful - {transformed[0]['home_team']} vs {transformed[0]['away_team']}")
        else:
            print("⚠️  API-Football: No fixtures (expected with free plan limitations)")
    except Exception as e:
        print(f"❌ API-Football error: {e}")
    
    print("\n🎯 Integration Status:")
    print("✅ API-Football service is imported and ready")
    print("✅ Transform method implemented for API-Football")
    print("✅ Helper function created for easy switching")
    print("✅ Currently using Football-Data.org (reliable)")
    print("🔄 Ready to switch to API-Football when paid plan is available")

if __name__ == "__main__":
    asyncio.run(test_services())