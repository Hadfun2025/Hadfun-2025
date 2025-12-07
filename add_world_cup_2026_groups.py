"""
Add World Cup 2026 Groups to Database
Draw completed: December 5, 2025
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

WORLD_CUP_GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Winner of Uefa play-off D"],
    "B": ["Canada", "Winner of Uefa play-off A", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Winner of Uefa play-off C"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Winner of Uefa play-off B", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Winner of Fifa play-off 2", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "Winner of Fifa play-off 1", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"]
}

PLAY_OFF_NOTES = {
    "Uefa play-off A": "Italy, Wales, Bosnia-Herzegovina or Northern Ireland",
    "Uefa play-off B": "Ukraine, Poland, Albania or Sweden",
    "Uefa play-off C": "Turkey, Slovakia, Kosovo or Romania",
    "Uefa play-off D": "Denmark, Czech Republic, Republic of Ireland or North Macedonia",
    "Fifa play-off 1": "DR Congo, Jamaica or New Caledonia",
    "Fifa play-off 2": "Iraq, Bolivia or Suriname"
}

async def add_world_cup_groups():
    """Add World Cup 2026 groups to database"""
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client.test_database
    
    print("🌍 Adding World Cup 2026 Groups...")
    print("=" * 60)
    
    # Clear existing World Cup groups
    await db.world_cup_groups.delete_many({"tournament": "World Cup 2026"})
    
    # Add all groups
    for group_letter, teams in WORLD_CUP_GROUPS.items():
        group_doc = {
            "tournament": "World Cup 2026",
            "group": group_letter,
            "teams": teams,
            "draw_date": "2025-12-05",
            "status": "confirmed"
        }
        
        await db.world_cup_groups.insert_one(group_doc)
        print(f"✅ Group {group_letter}: {', '.join(teams)}")
    
    print("\n" + "=" * 60)
    print("📝 Play-off Notes:")
    for playoff, info in PLAY_OFF_NOTES.items():
        print(f"  • {playoff}: {info}")
    
    print("\n" + "=" * 60)
    print("✅ World Cup 2026 groups added successfully!")
    print(f"Total groups: {len(WORLD_CUP_GROUPS)}")
    print(f"Total teams/slots: {sum(len(teams) for teams in WORLD_CUP_GROUPS.values())}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_world_cup_groups())
