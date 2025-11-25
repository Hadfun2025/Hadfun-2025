from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from api_football_service import APIFootballService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize API Football Service
api_football = APIFootballService()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ========== MODELS ==========

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_points: int = 0

class UserCreate(BaseModel):
    username: str
    email: str

class League(BaseModel):
    id: int
    name: str
    country: str
    logo: Optional[str] = None
    season: int

class Fixture(BaseModel):
    fixture_id: int
    league_id: int
    league_name: str
    home_team: str
    away_team: str
    home_logo: Optional[str] = None
    away_logo: Optional[str] = None
    match_date: str
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None

class Prediction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    fixture_id: int
    prediction: str  # "home", "draw", "away"
    league_id: int
    match_date: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    points: Optional[int] = None
    result: Optional[str] = None  # "correct", "incorrect", "pending"

class PredictionCreate(BaseModel):
    user_id: str
    fixture_id: int
    prediction: str
    league_id: int
    match_date: str

class LeaderboardEntry(BaseModel):
    username: str
    total_points: int
    correct_predictions: int
    total_predictions: int
    rank: int


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
    return {"message": "Football Predictions Platform API"}


@api_router.get("/leagues", response_model=List[Dict])
async def get_leagues():
    """Get list of supported leagues"""
    return SUPPORTED_LEAGUES


@api_router.get("/fixtures")
async def get_fixtures(
    league_ids: str = "39,140,78",  # Comma-separated league IDs
    days_ahead: int = 7
):
    """
    Get upcoming fixtures for specified leagues
    Args:
        league_ids: Comma-separated league IDs (e.g., "39,140,78")
        days_ahead: Number of days to look ahead (default: 7)
    """
    try:
        league_id_list = [int(lid.strip()) for lid in league_ids.split(',')]
        
        # Check if API key is set
        if api_football.api_key == "YOUR_API_KEY_HERE":
            # Return mock data if API key not set
            logger.warning("API key not set, returning mock fixtures")
            return get_mock_fixtures(league_id_list, days_ahead)
        
        fixtures = await api_football.get_upcoming_fixtures(league_id_list, days_ahead)
        
        # Transform to our format
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


@api_router.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    # Check if username exists
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


@api_router.post("/predictions", response_model=Prediction)
async def create_prediction(pred: PredictionCreate):
    """Submit a prediction"""
    # Validate prediction value
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
    
    pred_obj = Prediction(**pred.model_dump(), result="pending")
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
async def get_leaderboard(limit: int = 20):
    """Get leaderboard of top predictors"""
    # Aggregate user statistics
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
    
    # Get user details and combine
    leaderboard = []
    for stat in stats:
        user = await db.users.find_one({"id": stat["_id"]}, {"_id": 0})
        if user:
            leaderboard.append({
                "username": user['username'],
                "total_points": user.get('total_points', 0),
                "correct_predictions": stat['correct_predictions'],
                "total_predictions": stat['total_predictions'],
                "rank": 0  # Will be set after sorting
            })
    
    # Sort by points
    leaderboard.sort(key=lambda x: x['total_points'], reverse=True)
    
    # Assign ranks
    for idx, entry in enumerate(leaderboard[:limit]):
        entry['rank'] = idx + 1
    
    return leaderboard[:limit]


# Include the router
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
