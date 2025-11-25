from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from api_football_service import APIFootballService
from paypal_service import PayPalService
from models import *

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
api_football = APIFootballService()
paypal_service = PayPalService()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== HELPER FUNCTIONS ==========

def get_week_id(date: datetime) -> str:
    """Get week identifier (e.g., '2024-W42')"""
    return date.strftime("%Y-W%W")


def get_current_week_dates():
    """Get current week Monday-Wednesday dates"""
    today = datetime.now()
    # Find Monday of current week
    monday = today - timedelta(days=today.weekday())
    wednesday = monday + timedelta(days=2)
    sunday = monday + timedelta(days=6)
    
    return {
        "week_id": get_week_id(monday),
        "week_start": monday.replace(hour=0, minute=0, second=0),
        "cutoff": wednesday.replace(hour=23, minute=59, second=59),
        "week_end": sunday.replace(hour=23, minute=59, second=59)
    }


async def get_or_create_weekly_cycle():
    """Get or create current weekly cycle"""
    week_dates = get_current_week_dates()
    
    # Check if cycle exists
    cycle = await db.weekly_cycles.find_one({"week_id": week_dates["week_id"]})
    
    if not cycle:
        # Get team settings
        settings = await db.team_settings.find_one({})
        if not settings:
            # Create default settings
            settings = {
                "stake_amount": 5.0,
                "admin_fee_percentage": 10.0,
                "charity_mode": False
            }
            await db.team_settings.insert_one(settings)
        
        # Create new cycle
        stake = settings.get("stake_amount", 5.0)
        cycle = {
            "week_id": week_dates["week_id"],
            "week_start": week_dates["week_start"].isoformat(),
            "week_end": week_dates["week_end"].isoformat(),
            "cutoff_date": week_dates["cutoff"].isoformat(),
            "stake_amount": stake,
            "total_pot": 0,
            "admin_fee": 0,
            "distributable_pot": 0,
            "status": "active",
            "is_tie": False,
            "tied_users": [],
            "rollover_amount": 0,
            "charity_mode": settings.get("charity_mode", False),
            "charity_name": settings.get("charity_name")
        }
        await db.weekly_cycles.insert_one(cycle)
    
    return cycle


def get_mock_fixtures(league_ids: List[int], days_ahead: int) -> List[Dict]:
    """Generate mock fixtures for testing without API key"""
    mock_fixtures = []
    league_map = {l['id']: l for l in SUPPORTED_LEAGUES}
    
    teams = {
        39: [
            ("West Ham", "Brentford"),  # Monday fixture
            ("Manchester United", "Liverpool"), 
            ("Chelsea", "Arsenal"), 
            ("Tottenham", "Manchester City"),
            ("Newcastle", "Brighton"),
            ("Aston Villa", "Wolves")
        ],
        140: [("Real Madrid", "Barcelona"), ("Atletico Madrid", "Sevilla"), ("Valencia", "Athletic Bilbao")],
        78: [("Bayern Munich", "Borussia Dortmund"), ("RB Leipzig", "Bayer Leverkusen")],
        40: [("Leeds United", "Leicester City"), ("Southampton", "Norwich City")],
    }
    
    # Start from today to capture Monday's fixture
    base_date = datetime.now()
    
    for league_id in league_ids:
        if league_id not in league_map or league_id not in teams:
            continue
            
        league_info = league_map[league_id]
        league_teams = teams[league_id]
        
        for idx, (home, away) in enumerate(league_teams):
            match_date = base_date + timedelta(days=idx % days_ahead)
            
            mock_fixtures.append({
                "fixture_id": int(f"{league_id}{idx:03d}"),
                "league_id": league_id,
                "league_name": league_info['name'],
                "home_team": home,
                "away_team": away,
                "home_logo": None,
                "away_logo": None,
                "match_date": match_date.isoformat(),
                "status": "NS",
            })
    
    return mock_fixtures


# ========== PREDEFINED LEAGUES ==========
SUPPORTED_LEAGUES = [
    {"id": 39, "name": "Premier League", "country": "England", "season": 2024},
    {"id": 140, "name": "La Liga", "country": "Spain", "season": 2024},
    {"id": 78, "name": "Bundesliga", "country": "Germany", "season": 2024},
    {"id": 135, "name": "Serie A", "country": "Italy", "season": 2024},
    {"id": 61, "name": "Ligue 1", "country": "France", "season": 2024},
    {"id": 40, "name": "Championship", "country": "England", "season": 2024},
    {"id": 94, "name": "Primeira Liga", "country": "Portugal", "season": 2024},
    {"id": 88, "name": "Eredivisie", "country": "Netherlands", "season": 2024},
]


# ========== ENDPOINTS ==========

@api_router.get("/")
async def root():
    return {"message": "Football Predictions Platform API with Weekly Pot System"}


@api_router.get("/leagues", response_model=List[Dict])
async def get_leagues():
    """Get list of supported leagues"""
    return SUPPORTED_LEAGUES


@api_router.get("/fixtures")
async def get_fixtures(
    league_ids: str = "39,140,78",
    days_ahead: int = 7
):
    """Get upcoming fixtures"""
    try:
        league_id_list = [int(lid.strip()) for lid in league_ids.split(',')]
        
        if api_football.api_key == "YOUR_API_KEY_HERE":
            logger.warning("API key not set, returning mock fixtures")
            return get_mock_fixtures(league_id_list, days_ahead)
        
        fixtures = await api_football.get_upcoming_fixtures(league_id_list, days_ahead)
        
        result = []
        for f in fixtures:
            fixture_data = f.get('fixture', {})
            teams = f.get('teams', {})
            league = f.get('league', {})
            
            result.append({
                "fixture_id": fixture_data.get('id'),
                "league_id": league.get('id'),
                "league_name": league.get('name'),
                "home_team": teams.get('home', {}).get('name'),
                "away_team": teams.get('away', {}).get('name'),
                "home_logo": teams.get('home', {}).get('logo'),
                "away_logo": teams.get('away', {}).get('logo'),
                "match_date": fixture_data.get('date'),
                "status": fixture_data.get('status', {}).get('short'),
            })
        
        return result
    
    except Exception as e:
        logger.error(f"Error fetching fixtures: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching fixtures: {str(e)}")


# ========== USER ENDPOINTS ==========

@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    existing = await db.users.find_one({"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_obj = User(**user.model_dump())
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    return user_obj


@api_router.get("/users/{username}", response_model=User)
async def get_user(username: str):
    """Get user by username"""
    user = await db.users.find_one({"username": username}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if isinstance(user.get('created_at'), str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    
    return user


# ========== PREDICTION ENDPOINTS ==========

@api_router.post("/predictions", response_model=Prediction)
async def create_prediction(pred: PredictionCreate):
    """Submit a prediction"""
    if pred.prediction not in ["home", "draw", "away"]:
        raise HTTPException(status_code=400, detail="Prediction must be 'home', 'draw', or 'away'")
    
    # Check if user exists
    user = await db.users.find_one({"id": pred.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if prediction already exists
    existing = await db.predictions.find_one({
        "user_id": pred.user_id,
        "fixture_id": pred.fixture_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Prediction already exists for this fixture")
    
    # Check cutoff date
    cycle = await get_or_create_weekly_cycle()
    cutoff = datetime.fromisoformat(cycle['cutoff_date'])
    if datetime.now() > cutoff:
        raise HTTPException(status_code=400, detail="Prediction deadline has passed for this week")
    
    # Get week_id from match date
    match_date = datetime.fromisoformat(pred.match_date)
    week_id = get_week_id(match_date)
    
    pred_obj = Prediction(**pred.model_dump(), week_id=week_id, result="pending")
    doc = pred_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.predictions.insert_one(doc)
    return pred_obj


@api_router.get("/predictions/user/{user_id}")
async def get_user_predictions(user_id: str):
    """Get all predictions for a user"""
    predictions = await db.predictions.find({"user_id": user_id}, {"_id": 0}).to_list(1000)
    
    for pred in predictions:
        if isinstance(pred.get('created_at'), str):
            pred['created_at'] = datetime.fromisoformat(pred['created_at'])
    
    return predictions


@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 20, season: bool = False):
    """Get leaderboard (overall or season)"""
    pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "total_predictions": {"$sum": 1},
                "correct_predictions": {
                    "$sum": {"$cond": [{"$eq": ["$result", "correct"]}, 1, 0]}
                }
            }
        }
    ]
    
    stats = await db.predictions.aggregate(pipeline).to_list(None)
    
    leaderboard = []
    for stat in stats:
        user = await db.users.find_one({"id": stat["_id"]}, {"_id": 0})
        if user:
            leaderboard.append({
                "username": user['username'],
                "total_points": user.get('total_points', 0),
                "season_points": user.get('season_points', 0),
                "correct_predictions": stat['correct_predictions'],
                "total_predictions": stat['total_predictions'],
                "weekly_wins": user.get('weekly_wins', 0),
                "rank": 0
            })
    
    # Sort by season_points if season=True, else total_points
    sort_key = 'season_points' if season else 'total_points'
    leaderboard.sort(key=lambda x: x[sort_key], reverse=True)
    
    for idx, entry in enumerate(leaderboard[:limit]):
        entry['rank'] = idx + 1
    
    return leaderboard[:limit]


# ========== WEEKLY POT ENDPOINTS ==========

@api_router.get("/pot/current")
async def get_current_pot():
    """Get current week pot information"""
    cycle = await get_or_create_weekly_cycle()
    
    # Get payment count
    payment_count = await db.payments.count_documents({
        "week_id": cycle['week_id'],
        "status": "completed"
    })
    
    # Calculate pot
    stake = cycle['stake_amount']
    total_pot = payment_count * stake
    admin_fee = total_pot * 0.10
    distributable = total_pot - admin_fee + cycle.get('rollover_amount', 0)
    
    return {
        "week_id": cycle['week_id'],
        "week_start": cycle['week_start'],
        "cutoff_date": cycle['cutoff_date'],
        "stake_amount": stake,
        "participants": payment_count,
        "total_pot": total_pot,
        "admin_fee": admin_fee,
        "rollover_amount": cycle.get('rollover_amount', 0),
        "distributable_pot": distributable,
        "status": cycle['status'],
        "charity_mode": cycle.get('charity_mode', False)
    }


@api_router.get("/pot/weekly-results")
async def get_weekly_results(limit: int = 10):
    """Get past weekly results"""
    cycles = await db.weekly_cycles.find(
        {"status": {"$in": ["distributed", "rollover"]}},
        {"_id": 0}
    ).sort("week_start", -1).limit(limit).to_list(limit)
    
    return cycles


@api_router.post("/pot/calculate-winner")
async def calculate_weekly_winner():
    """Calculate winner for current week (Admin only)"""
    cycle = await get_or_create_weekly_cycle()
    week_id = cycle['week_id']
    
    # Get all predictions for this week
    pipeline = [
        {"$match": {"week_id": week_id, "result": "correct"}},
        {
            "$group": {
                "_id": "$user_id",
                "username": {"$first": "$username"},
                "correct_count": {"$sum": 1}
            }
        },
        {"$sort": {"correct_count": -1}}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(None)
    
    if not results:
        # No winners, rollover pot
        await db.weekly_cycles.update_one(
            {"week_id": week_id},
            {"$set": {"status": "rollover"}}
        )
        return {"message": "No predictions or no correct predictions. Pot rolls over."}
    
    top_score = results[0]['correct_count']
    winners = [r for r in results if r['correct_count'] == top_score]
    
    # Calculate pot
    payment_count = await db.payments.count_documents({
        "week_id": week_id,
        "status": "completed"
    })
    
    stake = cycle['stake_amount']
    total_pot = payment_count * stake
    admin_fee = total_pot * 0.10
    rollover = cycle.get('rollover_amount', 0)
    distributable = total_pot - admin_fee + rollover
    
    if len(winners) > 1:
        # Tie - give points, rollover pot
        for winner in winners:
            await db.users.update_one(
                {"id": winner['_id']},
                {"$inc": {"season_points": 1}}
            )
        
        # Rollover pot (minus admin fee)
        await db.weekly_cycles.update_one(
            {"week_id": week_id},
            {
                "$set": {
                    "status": "rollover",
                    "is_tie": True,
                    "tied_users": [w['username'] for w in winners],
                    "total_pot": total_pot,
                    "admin_fee": admin_fee
                }
            }
        )
        
        # Set rollover for next week
        next_week_id = get_week_id(datetime.now() + timedelta(days=7))
        await db.weekly_cycles.update_one(
            {"week_id": next_week_id},
            {"$set": {"rollover_amount": distributable}},
            upsert=True
        )
        
        return {
            "message": "Tie detected. Points awarded, pot rolls over.",
            "tied_users": [w['username'] for w in winners],
            "rollover_amount": distributable
        }
    
    # Single winner
    winner = winners[0]
    
    # Update winner
    await db.users.update_one(
        {"id": winner['_id']},
        {
            "$inc": {
                "season_points": 3,
                "weekly_wins": 1
            }
        }
    )
    
    # Update cycle
    await db.weekly_cycles.update_one(
        {"week_id": week_id},
        {
            "$set": {
                "status": "distributed",
                "winner_id": winner['_id'],
                "winner_username": winner['username'],
                "total_pot": total_pot,
                "admin_fee": admin_fee,
                "distributable_pot": distributable
            }
        }
    )
    
    return {
        "message": "Winner calculated",
        "winner": winner['username'],
        "correct_predictions": top_score,
        "payout": distributable
    }


# ========== PAYMENT ENDPOINTS ==========

@api_router.post("/payments/create-order")
async def create_payment_order(payment: PaymentCreate):
    """Create PayPal order for weekly payment"""
    if not paypal_service.is_configured():
        # Mock payment for testing
        payment_obj = Payment(**payment.model_dump(), status="completed")
        doc = payment_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['completed_at'] = datetime.utcnow().isoformat()
        await db.payments.insert_one(doc)
        
        return {
            "payment_id": payment_obj.id,
            "status": "completed",
            "message": "Payment completed (TEST MODE - PayPal not configured)"
        }
    
    # Create PayPal order
    order = paypal_service.create_order(
        amount=payment.amount,
        currency="GBP",
        description=f"Weekly Pot Payment - Week {payment.week_id}"
    )
    
    if not order:
        raise HTTPException(status_code=500, detail="Failed to create PayPal order")
    
    # Save payment record
    payment_obj = Payment(**payment.model_dump(), paypal_order_id=order['order_id'], status="pending")
    doc = payment_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.payments.insert_one(doc)
    
    return {
        "payment_id": payment_obj.id,
        "order_id": order['order_id'],
        "approval_url": order['approval_url']
    }


@api_router.post("/payments/capture/{order_id}")
async def capture_payment(order_id: str):
    """Capture PayPal payment after user approval"""
    if not paypal_service.is_configured():
        return {"message": "Payment completed (TEST MODE)"}
    
    # Capture order
    result = paypal_service.capture_order(order_id)
    
    if not result:
        raise HTTPException(status_code=500, detail="Failed to capture payment")
    
    # Update payment record
    await db.payments.update_one(
        {"paypal_order_id": order_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat()
            }
        }
    )
    
    return result


@api_router.get("/payments/user/{user_id}")
async def get_user_payments(user_id: str):
    """Get user payment history"""
    payments = await db.payments.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return payments


# ========== TEAM SETTINGS ENDPOINTS ==========

@api_router.get("/settings/team")
async def get_team_settings():
    """Get team settings"""
    settings = await db.team_settings.find_one({}, {"_id": 0})
    if not settings:
        settings = {
            "stake_amount": 5.0,
            "admin_fee_percentage": 10.0,
            "charity_mode": False,
            "season_prize_pool": 0
        }
        await db.team_settings.insert_one(settings)
    
    return settings


@api_router.put("/settings/team")
async def update_team_settings(settings: dict):
    """Update team settings (Admin only)"""
    await db.team_settings.update_one(
        {},
        {"$set": settings},
        upsert=True
    )
    return {"message": "Settings updated"}


# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
