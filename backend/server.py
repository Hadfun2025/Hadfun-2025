from fastapi import FastAPI, APIRouter, HTTPException, Request, File, UploadFile
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from api_football_service import APIFootballService
from football_data_service import FootballDataService
from paypal_service import PayPalService
from matchweek_service import MatchweekService
from stripe_service import StripePaymentService
from email_service import EmailService
from models import *
from team_models import Team, TeamCreate, TeamMember, TeamJoin, TeamMessage, MessageCreate, TeamStats, TeamNomination, NominationCreate, WinnerDonation, TeamInvitation, InvitationCreate

# Import new route modules
from routes import posts as posts_router
from routes import auth as auth_router

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize services
api_football = APIFootballService()  # Ready for use when paid plan is available
football_data = FootballDataService()  # Currently active for result updates
paypal_service = PayPalService()
matchweek_service = MatchweekService()
email_service = EmailService()

# Helper function for sending emails
async def send_email(to_email: str, subject: str, html_content: str):
    """Send an email using the email service"""
    try:
        import resend
        resend.api_key = os.environ.get('RESEND_API_KEY')
        sender_email = os.environ.get('SENDER_EMAIL', 'noreply@hadfun.co.uk')
        
        params = {
            "from": f"HadFun Predictor <{sender_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }
        
        response = resend.Emails.send(params)
        return response
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise



async def send_prediction_email(to_email: str, username: str, prediction_data: dict, is_update: bool = False):
    """Send prediction confirmation email to user"""
    action = "updated" if is_update else "recorded"
    prediction_text = prediction_data['prediction'].upper()
    
    if prediction_text == "HOME":
        prediction_display = f"✅ {prediction_data['home_team']} to WIN"
    elif prediction_text == "AWAY":
        prediction_display = f"✅ {prediction_data['away_team']} to WIN"
    else:
        prediction_display = "🤝 DRAW"
    
    match_date_str = prediction_data.get('match_date', '')
    if isinstance(match_date_str, str):
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            match_date_display = dt.strftime('%A, %B %d, %Y at %H:%M UTC')
        except:
            match_date_display = match_date_str[:16]
    else:
        match_date_display = str(match_date_str)[:16]
    
    subject = f"{'Updated' if is_update else 'New'} Prediction: {prediction_data['home_team']} vs {prediction_data['away_team']}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
            <h1 style="margin: 0;">🎯 Prediction {'Updated' if is_update else 'Confirmed'}!</h1>
        </div>
        
        <div style="background: #f7fafc; padding: 30px; border-radius: 0 0 10px 10px;">
            <p style="font-size: 16px; color: #2d3748;">Hi <strong>{username}</strong>,</p>
            
            <p style="font-size: 16px; color: #2d3748;">Your prediction has been {action}:</p>
            
            <div style="background: white; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 5px;">
                <h2 style="margin: 0 0 15px 0; color: #2d3748; font-size: 20px;">
                    ⚽ {prediction_data['home_team']} vs {prediction_data['away_team']}
                </h2>
                <p style="margin: 5px 0; color: #4a5568;">
                    <strong>League:</strong> {prediction_data.get('league', 'Unknown')}
                </p>
                <p style="margin: 5px 0; color: #4a5568;">
                    <strong>Match Date:</strong> {match_date_display}
                </p>
                <div style="background: #edf2f7; padding: 15px; margin-top: 15px; border-radius: 5px; text-align: center;">
                    <p style="margin: 0; font-size: 18px; font-weight: bold; color: #667eea;">
                        Your Prediction: {prediction_display}
                    </p>
                </div>
            </div>
            
            <p style="font-size: 14px; color: #718096; margin-top: 30px;">
                💡 <strong>Tip:</strong> You can update your prediction anytime before the match starts or until Wednesday 23:59 UTC (whichever comes first).
            </p>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://www.hadfun.co.uk" style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                    View All Predictions
                </a>
            </div>
            
            <p style="font-size: 12px; color: #a0aec0; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0;">
                Good luck! 🍀<br>
                HadFun Predictions App
            </p>
        </div>
    </body>
    </html>
    """
    
    await send_email(to_email, subject, html_content)


# Helper function to get the active football service
def get_active_football_service():
    """
    Returns the active football service for fetching fixtures and results.
    Switch to api_football when paid plan is available for faster updates.
    """
    # NOW USING API-FOOTBALL with paid plan for real-time updates!
    return api_football

# Stripe service will be initialized per request to get the webhook URL
def get_stripe_service(request: Request) -> StripePaymentService:
    """Get Stripe service with proper webhook URL"""
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    api_key = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')
    return StripePaymentService(api_key=api_key, webhook_url=webhook_url)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Add CORS middleware FIRST (before mounting static files)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Mount static files for uploads
UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
# Mount at /api/uploads to work with Kubernetes ingress routing
app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

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
    # British Isles
    {"id": 39, "name": "Premier League", "country": "England", "season": 2025},
    {"id": 40, "name": "Championship", "country": "England", "season": 2025},
    {"id": 179, "name": "Scottish Premiership", "country": "Scotland", "season": 2025},
    # European Leagues
    {"id": 140, "name": "La Liga", "country": "Spain", "season": 2025},
    {"id": 78, "name": "Bundesliga", "country": "Germany", "season": 2025},
    {"id": 135, "name": "Serie A", "country": "Italy", "season": 2025},
    {"id": 61, "name": "Ligue 1", "country": "France", "season": 2025},
    {"id": 94, "name": "Primeira Liga", "country": "Portugal", "season": 2025},
    {"id": 88, "name": "Eredivisie", "country": "Netherlands", "season": 2025},
    {"id": 203, "name": "Süper Lig", "country": "Turkey", "season": 2025},
    # Americas Leagues
    {"id": 253, "name": "MLS", "country": "USA", "season": 2025},
    {"id": 71, "name": "Brasileirão", "country": "Brazil", "season": 2025},
    {"id": 239, "name": "Liga BetPlay", "country": "Colombia", "season": 2025},
    # European Competitions (2025/26 Season)
    {"id": 2, "name": "UEFA Champions League", "country": "Europe", "season": 2025},
    {"id": 3, "name": "UEFA Europa League", "country": "Europe", "season": 2025},
    {"id": 848, "name": "UEFA Conference League", "country": "Europe", "season": 2025},
    # International Tournaments
    {"id": 1, "name": "World Cup", "country": "World", "season": 2026},
]


# ========== ENDPOINTS ==========

@api_router.get("/")
async def root():
    return {"message": "HadFun - Football Predictions Platform API"}


@api_router.get("/leagues", response_model=List[Dict])
async def get_leagues():
    """Get list of supported leagues"""
    return SUPPORTED_LEAGUES


@api_router.post("/admin/refresh-fixtures")
async def refresh_fixtures_from_api():
    """
    Refresh fixtures from API-Football for the current season
    Only updates fixtures from last 7 days to save API calls
    """
    try:
        import subprocess
        result = subprocess.run(
            ['python3', '/app/backend/update_fixtures_endpoint.py'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": "Fixtures updated successfully",
                "output": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": "Failed to update fixtures",
                "error": result.stderr
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/cleanup-duplicates")
async def cleanup_duplicate_fixtures():
    """
    Remove duplicate fixtures from database
    Keeps the fixture with the highest fixture_id (most recent)
    Handles team name variations with aggressive normalization
    """
    try:
        def normalize_team_name(name):
            """Universal normalization - strips FC/AFC/CF but keeps City/United in team names"""
            if not name:
                return ""
            
            # Convert to lowercase and strip
            normalized = name.lower().strip()
            
            # Remove number prefixes (1., 1899, 1846, etc.)
            import re
            normalized = re.sub(r'^\d+\.?\s*', '', normalized)
            normalized = re.sub(r'\s+\d{2,4}$', '', normalized)
            
            # Remove common prefixes FIRST
            prefixes = ['afc ', 'fc ', 'tsg ', 'fsv ', 'sv ', 'sc ', 'rb ', 'vfb ', 'vfl ', 
                       'cd ', 'gd ', 'us ', 'ss ', 'ssc ', 'acf ', 'as ', 'rc ', 'rcd ']
            for prefix in prefixes:
                if normalized.startswith(prefix):
                    normalized = normalized[len(prefix):].strip()
                    break
            
            # Special handling for teams that need "bayer" prefix kept
            if 'bayer' in normalized and 'leverkusen' in normalized:
                normalized = 'bayer leverkusen'
            
            # Handle Espanyol separately (has Barcelona in name but different team)
            if 'espanyol' in normalized:
                return 'espanyol'
            
            # Handle teams with "and" or "&" in name
            normalized = normalized.replace('&', 'and')
            
            # Strip common suffixes UNIVERSALLY (but keep City/United/Hotspur as part of name)
            # Remove these suffixes from the END
            suffixes_to_remove = [
                ' & hove albion fc',
                ' & hove albion',
                ' hove albion fc', 
                ' hove albion',
                ' hotspur fc',
                ' wanderers fc',
                ' athletic fc',
                ' rovers fc',
                ' albion fc',
                ' county fc',
                ' north end fc',
                ' park rangers fc',
                ' balompié',
                ' de fútbol',
                ' calcio',
                ' bc',
                ' ac',
                ' fc',  # Strip FC universally
                ' afc', # Strip AFC universally
                ' cf',  # Strip CF universally
                ' ec',
                ' sv',
                ' sc'
            ]
            
            for suffix in suffixes_to_remove:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)].strip()
                    break  # Only remove one suffix
            
            # Additional specific handlers for known problem cases
            # Keep these AFTER suffix removal to handle any edge cases
            
            # Netherlands - keep short forms
            if normalized == 'ajax amsterdam' or normalized == 'ajax':
                return 'ajax'
            elif normalized == 'psv eindhoven' or normalized == 'psv':
                return 'psv'
            elif normalized == 'feyenoord rotterdam' or normalized == 'feyenoord':
                return 'feyenoord'
            
            # Portugal
            elif normalized == 'sport lisboa e benfica' or normalized == 'benfica':
                return 'benfica'
            elif 'sporting' in normalized and 'braga' not in normalized and ('portugal' in normalized or 'cp' in normalized or normalized == 'sporting'):
                return 'sporting'
            elif normalized == 'sporting braga' or (normalized == 'braga' and 'sporting' in name.lower()):
                return 'sporting braga'
            elif 'porto' in normalized:
                return 'porto'
            
            # Spain
            elif normalized == 'real madrid':
                return 'real madrid'
            elif normalized == 'barcelona':
                return 'barcelona'
            elif normalized == 'atletico madrid' or normalized == 'atletico de madrid':
                return 'atletico madrid'
            elif normalized == 'athletic bilbao' or normalized == 'athletic club':
                return 'athletic club'
            
            # France - Ligue 1
            elif 'paris saint-germain' in normalized or 'paris saint germain' in normalized or normalized == 'paris':
                return 'paris saint-germain'
            
            # Italy
            elif 'inter' in normalized and 'milan' in normalized:
                return 'inter milan'
            elif normalized == 'inter' or normalized == 'internazionale':
                return 'inter'
            elif normalized == 'milan' or normalized == 'ac milan':
                return 'milan'
            elif normalized == 'juventus':
                return 'juventus'
            
            # Scotland - keep separate
            elif normalized == 'dundee united' or normalized == 'dundee utd':
                return 'dundee united'
            elif normalized == 'dundee':
                return 'dundee'
            
            # Germany
            elif 'hoffenheim' in normalized:
                return 'hoffenheim'
            elif 'heidenheim' in normalized:
                return 'heidenheim'
            elif 'bayern' in normalized and ('münchen' in normalized or 'munich' in normalized):
                return 'bayern munich'
            elif 'borussia' in normalized and 'dortmund' in normalized:
                return 'borussia dortmund'
            elif 'borussia' in normalized and ('monchengladbach' in normalized or 'mönchengladbach' in normalized):
                return 'borussia monchengladbach'
            
            # Clean up double spaces
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            
            return normalized
        
        # Find all fixtures
        all_fixtures = await db.fixtures.find({}).to_list(length=None)
        
        # Track unique matches with normalized names
        seen = {}
        duplicates_to_remove = []
        
        for fixture in all_fixtures:
            home = fixture.get('home_team', '')
            away = fixture.get('away_team', '')
            date = fixture.get('utc_date')
            fixture_id = fixture.get('fixture_id')
            league_id = fixture.get('league_id')
            
            # Normalize team names for comparison
            home_norm = normalize_team_name(home)
            away_norm = normalize_team_name(away)
            
            # Create key with normalized names and league
            key = f"{league_id}|{home_norm}|{away_norm}|{date}"
            
            if key in seen:
                # Duplicate found - keep the one with higher fixture_id (more recent)
                existing_id, existing_original = seen[key]
                if fixture_id > existing_id:
                    # Remove old one, keep new one
                    duplicates_to_remove.append(existing_id)
                    seen[key] = (fixture_id, (home, away))
                else:
                    # Remove this one, keep existing
                    duplicates_to_remove.append(fixture_id)
            else:
                seen[key] = (fixture_id, (home, away))
        
        removed_count = 0
        if duplicates_to_remove:
            result = await db.fixtures.delete_many({'fixture_id': {'$in': duplicates_to_remove}})
            removed_count = result.deleted_count
        
        remaining = await db.fixtures.count_documents({})
        
        logger.info(f"✅ Cleaned up {removed_count} duplicate fixtures (aggressive normalization). {remaining} remaining.")
        
        return {
            "message": "Duplicates cleaned up successfully",
            "duplicates_removed": removed_count,
            "remaining_fixtures": remaining
        }
    except Exception as e:
        logger.error(f"Error cleaning up duplicates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/admin/score-predictions")
async def score_all_pending_predictions():
    """
    Score all pending predictions by checking fixture statuses
    """
    try:
        # Get all pending predictions
        pending_predictions = await db.predictions.find({"result": "pending"}).to_list(1000)
        
        scored_count = 0
        not_finished_count = 0
        
        for pred in pending_predictions:
            fixture_id = pred.get('fixture_id')
            
            # Get fixture from database
            fixture = await db.fixtures.find_one({"fixture_id": fixture_id})
            
            if not fixture:
                logger.warning(f"Fixture {fixture_id} not found for prediction {pred.get('id')}")
                continue
            
            # Only score if fixture is finished and has scores
            if fixture.get('status') == 'FINISHED' and fixture.get('home_score') is not None:
                home_score = fixture.get('home_score')
                away_score = fixture.get('away_score')
                
                # Determine actual result
                if home_score > away_score:
                    actual_result = 'home'
                elif away_score > home_score:
                    actual_result = 'away'
                else:
                    actual_result = 'draw'
                
                # Score prediction - mark as correct/incorrect
                # But DON'T add points yet - points awarded weekly by calculate_weekly_winners
                is_correct = pred.get('prediction') == actual_result
                
                await db.predictions.update_one(
                    {"id": pred['id']},
                    {"$set": {
                        "result": "correct" if is_correct else "incorrect",
                        "actual_result": actual_result,
                        "home_score": home_score,
                        "away_score": away_score
                    }}
                )
                scored_count += 1
                
                # Note: User points calculated weekly, not per prediction
            else:
                not_finished_count += 1
        
        logger.info(f"✅ Scored {scored_count} predictions, {not_finished_count} still pending (fixtures not finished)")
        
        return {
            "message": "Predictions scored successfully",
            "predictions_scored": scored_count,
            "still_pending": not_finished_count,
            "total_checked": len(pending_predictions)
        }
        
    except Exception as e:
        logger.error(f"Error scoring predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/update-results")
async def update_match_results():
    """
    Fetch latest scores for finished matches and update predictions
    This should be called periodically (e.g., after match days)
    """
    try:
        updated_count = 0
        scored_predictions = 0
        
        # Fetch all fixtures from API to get latest scores
        # British Isles, European, then Rest of World
        league_ids = [39, 40, 179, 140, 78, 135, 61, 94, 88, 203, 253, 71, 239]  # All leagues including new ones
        service = get_active_football_service()
        
        # Get fixtures for actual season dates (not simulated future dates)
        from datetime import datetime, timedelta
        
        # Fetch recent matches from the 2025-26 season (last 7 days)
        recent_dates = []
        today = datetime.now(timezone.utc)
        for i in range(7):
            date = today - timedelta(days=i)
            recent_dates.append(date.strftime('%Y-%m-%d'))
        
        all_fixtures = []
        for date_str in recent_dates:
            for league_id in league_ids:
                fixtures = await service.get_fixtures_by_date(date_str, league_id, season=2025)
                all_fixtures.extend(fixtures)
        
        if not all_fixtures:
            return {"message": "No fixtures data available", "updated": 0}
        
        # Transform and update fixtures in database
        transformed = service.transform_to_standard_format(all_fixtures)
        
        for fixture in transformed:
            # Only process finished matches with scores
            if fixture['status'] == 'FINISHED' and fixture.get('home_score') is not None:
                # Update fixture in database
                result = await db.fixtures.update_one(
                    {"fixture_id": fixture['fixture_id']},
                    {"$set": {
                        "home_score": fixture['home_score'],
                        "away_score": fixture['away_score'],
                        "status": fixture['status'],
                        "home_team": fixture['home_team'],
                        "away_team": fixture['away_team'],
                        "league_name": fixture['league_name']
                    }}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    
                    # Determine actual result
                    home_score = fixture['home_score']
                    away_score = fixture['away_score']
                    
                    if home_score > away_score:
                        actual_result = 'home'
                    elif away_score > home_score:
                        actual_result = 'away'
                    else:
                        actual_result = 'draw'
                    
                    # Find all predictions for this fixture
                    predictions = await db.predictions.find({
                        "fixture_id": fixture['fixture_id'],
                        "result": "pending"  # Only update pending predictions
                    }).to_list(1000)
                    
                    # Score each prediction
                    for pred in predictions:
                        is_correct = pred['prediction'] == actual_result
                        points = 3 if is_correct else 0
                        
                        await db.predictions.update_one(
                            {"id": pred['id']},
                            {"$set": {
                                "result": "correct" if is_correct else "incorrect",
                                "points": points
                            }}
                        )
                        scored_predictions += 1
                        
                        # Note: User points calculated weekly, not per prediction
        
        logger.info(f"Updated {updated_count} fixtures and scored {scored_predictions} predictions")
        
        return {
            "message": "Results updated successfully",
            "fixtures_updated": updated_count,
            "predictions_scored": scored_predictions
        }
        
    except Exception as e:
        logger.error(f"Error updating results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating results: {str(e)}")


@api_router.post("/admin/load-upcoming-fixtures")
async def load_upcoming_fixtures():
    """
    Load upcoming fixtures (next 30 days) for all leagues
    Faster than historical update - use this to quickly populate upcoming matches
    """
    try:
        from datetime import datetime, timedelta, timezone
        
        logger.info("🔄 Loading upcoming fixtures for all leagues...")
        
        # Get all league IDs from SUPPORTED_LEAGUES
        league_configs = {league['id']: league['season'] for league in SUPPORTED_LEAGUES}
        service = get_active_football_service()
        
        # Get fixtures for next 30 days
        all_fixtures = []
        today = datetime.now(timezone.utc)
        
        for days_offset in range(30):
            check_date = today + timedelta(days=days_offset)
            date_str = check_date.strftime('%Y-%m-%d')
            
            for league_id, season in league_configs.items():
                try:
                    fixtures = await service.get_fixtures_by_date(date_str, league_id, season=season)
                    all_fixtures.extend(fixtures)
                except Exception as e:
                    logger.warning(f"Error fetching {date_str} league {league_id}: {str(e)}")
                    continue
        
        logger.info(f"   Retrieved {len(all_fixtures)} total fixtures")
        
        if not all_fixtures:
            return {"message": "No upcoming fixtures found", "loaded": 0}
        
        # Transform and save to database
        transformed = service.transform_to_standard_format(all_fixtures)
        
        loaded_count = 0
        for fixture in transformed:
            # Insert or update fixture
            await db.fixtures.update_one(
                {"fixture_id": fixture['fixture_id']},
                {"$set": fixture},
                upsert=True
            )
            loaded_count += 1
        
        logger.info(f"✅ Loaded {loaded_count} upcoming fixtures")
        
        return {
            "message": "Upcoming fixtures loaded successfully",
            "fixtures_loaded": loaded_count
        }
        
    except Exception as e:
        logger.error(f"❌ Error loading upcoming fixtures: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/update-all-historical-results")
async def update_all_historical_results():
    """
    Fetch ALL historical match results from August 2024 (start of season) to present
    This updates fixtures and scores all predictions for the entire season
    Use this to backfill historical data
    """
    try:
        from datetime import datetime, timedelta, timezone
        
        logger.info("🔄 Starting FULL HISTORICAL result update (August 2024 - Present)...")
        
        updated_count = 0
        scored_predictions = 0
        
        # All supported leagues
        league_ids = [39, 40, 179, 140, 78, 135, 61, 94, 88, 203, 253, 71, 239]
        service = get_active_football_service()
        
        # Season start: August 1, 2024 through today
        start_date = datetime(2024, 8, 1, tzinfo=timezone.utc)
        end_date = datetime.now(timezone.utc)
        
        # Calculate number of days to fetch
        days_to_fetch = (end_date - start_date).days + 1
        logger.info(f"   Fetching {days_to_fetch} days of fixtures from {start_date.date()} to {end_date.date()}")
        
        all_fixtures = []
        
        # Fetch fixtures day by day (API limitation)
        for day_offset in range(days_to_fetch):
            check_date = start_date + timedelta(days=day_offset)
            date_str = check_date.strftime('%Y-%m-%d')
            
            for league_id in league_ids:
                try:
                    fixtures = await service.get_fixtures_by_date(date_str, league_id, season=2025)
                    all_fixtures.extend(fixtures)
                except Exception as e:
                    logger.warning(f"   Error fetching {date_str} league {league_id}: {str(e)}")
                    continue
        
        logger.info(f"   Retrieved {len(all_fixtures)} total fixtures from API")
        
        if not all_fixtures:
            return {
                "message": "No fixtures found for historical period",
                "fixtures_updated": 0,
                "predictions_scored": 0
            }
        
        # Transform fixtures to standard format
        transformed = service.transform_to_standard_format(all_fixtures)
        
        # Process each finished fixture
        for fixture in transformed:
            if fixture['status'] == 'FINISHED' and fixture.get('home_score') is not None:
                # Update fixture in database
                result = await db.fixtures.update_one(
                    {"fixture_id": fixture['fixture_id']},
                    {"$set": {
                        "home_score": fixture['home_score'],
                        "away_score": fixture['away_score'],
                        "status": fixture['status'],
                        "home_team": fixture['home_team'],
                        "away_team": fixture['away_team'],
                        "league_name": fixture['league_name']
                    }},
                    upsert=True
                )
                
                if result.modified_count > 0 or result.upserted_id:
                    updated_count += 1
                
                # Determine actual result
                home_score = fixture['home_score']
                away_score = fixture['away_score']
                
                if home_score > away_score:
                    actual_result = 'home'
                elif away_score > home_score:
                    actual_result = 'away'
                else:
                    actual_result = 'draw'
                
                # Find all pending predictions for this fixture
                predictions = await db.predictions.find({
                    "fixture_id": fixture['fixture_id'],
                    "result": "pending"
                }).to_list(1000)
                
                # Score each prediction
                for pred in predictions:
                    is_correct = pred['prediction'] == actual_result
                    points = 3 if is_correct else 0
                    
                    # Update prediction with result AND match details
                    await db.predictions.update_one(
                        {"id": pred['id']},
                        {"$set": {
                            "result": "correct" if is_correct else "incorrect",
                            "points": points,
                            "home_team": fixture['home_team'],
                            "away_team": fixture['away_team'],
                            "league": fixture['league_name'],
                            "home_score": home_score,
                            "away_score": away_score,
                            "status": fixture['status']
                        }}
                    )
                    scored_predictions += 1
        
        logger.info(f"✅ Historical update complete: {updated_count} fixtures updated, {scored_predictions} predictions scored")
        
        return {
            "message": "Historical results updated successfully",
            "fixtures_updated": updated_count,
            "predictions_scored": scored_predictions,
            "date_range": f"{start_date.date()} to {end_date.date()}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in historical update: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating historical results: {str(e)}")


@api_router.get("/fixtures")
async def get_fixtures(
    league_ids: str = "39,140,78",
    days_ahead: int = 14,
    matchday: Optional[str] = None,
    status: Optional[str] = None,
    upcoming_only: bool = False
):
    """
    Get fixtures from database (loaded via API-Football)
    Args:
        league_ids: Comma-separated league IDs
        days_ahead: Number of days ahead to fetch (default: 14, use 365 for full season)
        matchday: Optional matchday filter (e.g., "1", "10", "Regular Season - 10")
        status: Optional status filter (SCHEDULED, FINISHED, LIVE)
        upcoming_only: If true, only show future fixtures (ignores days_ahead for past)
    """
    try:
        from datetime import datetime, timedelta, timezone
        
        # Parse league IDs - if single league, use direct match, otherwise use $in
        league_id_list = [int(lid.strip()) for lid in league_ids.split(',')]
        
        # Build query
        if len(league_id_list) == 1:
            query = {"league_id": league_id_list[0]}
        else:
            query = {"league_id": {"$in": league_id_list}}
        
        # Filter by status if specified
        if status:
            query["status"] = status
        
        # Filter by matchday if specified
        if matchday:
            # Support both "10" and "Regular Season - 10" formats
            query["matchday"] = {"$regex": f".*{matchday}.*", "$options": "i"}
        else:
            # Query fixtures from database (loaded by API-Football via refresh endpoint)
            now = datetime.now(timezone.utc)
            
            if upcoming_only:
                # Only show upcoming fixtures (from now onwards)
                # Use naive datetime for comparison (MongoDB stores as naive UTC)
                query["utc_date"] = {"$gte": now.replace(tzinfo=None)}
            else:
                # For full season (365 days), go back to start of season
                # For "Next X weeks" view (days_ahead < 180), only show upcoming fixtures
                if days_ahead >= 180:  # Full season or long range
                    # For international competitions (2024 season) go back to Jan 2024
                    # For domestic leagues (2025 season) go back to August 2024
                    # This covers Champions League 2024/25, Nations League 2024, etc.
                    start_date = datetime(2024, 1, 1)  # Naive datetime - covers all competitions
                    end_date = now.replace(tzinfo=None) + timedelta(days=days_ahead)
                else:
                    # For "Next 2 weeks" or "Next 4 weeks" view: show last 3 days + upcoming fixtures
                    # This allows users to see recent weekend results while focusing on upcoming games
                    start_date = now.replace(tzinfo=None) - timedelta(days=3)
                    end_date = now.replace(tzinfo=None) + timedelta(days=days_ahead)
                
                logger.info(f"📅 Date range query: {start_date} to {end_date} (days_ahead={days_ahead})")
                
                # Filter by date - only include fixtures with valid dates
                query["utc_date"] = {
                    "$gte": start_date, 
                    "$lte": end_date,
                    "$ne": None  # Exclude fixtures without dates
                }
        
        # Get fixtures from database - sort by date, with current/future matches first
        if upcoming_only:
            fixtures_cursor = db.fixtures.find(query).sort("utc_date", 1)
        else:
            # For current week view, prioritize recent and upcoming fixtures
            fixtures_cursor = db.fixtures.find(query).sort([
                ("utc_date", 1),  # Sort by date ascending
            ])
        fixtures = await fixtures_cursor.to_list(length=None)  # Convert to list asynchronously
        
        # Convert MongoDB _id and datetime objects to strings
        for fixture in fixtures:
            if '_id' in fixture:
                fixture['_id'] = str(fixture['_id'])
            # Convert datetime to ISO string for frontend
            if 'utc_date' in fixture and hasattr(fixture['utc_date'], 'isoformat'):
                fixture['utc_date'] = fixture['utc_date'].isoformat()
        
        logger.info(f"Retrieved {len(fixtures)} fixtures from database for leagues: {league_id_list}")
        
        return fixtures
    
    except Exception as e:
        logger.error(f"Error fetching fixtures: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching fixtures: {str(e)}")


@api_router.get("/admin/debug-fixtures")
async def debug_fixtures():
    """Debug: Check what fixtures exist for Dec 6-8, 2025"""
    try:
        from datetime import datetime
        
        # Check fixtures for Dec 6-8
        fixtures = await db.fixtures.find(
            {
                "utc_date": {
                    "$gte": datetime(2025, 12, 6, 0, 0, 0),
                    "$lte": datetime(2025, 12, 8, 23, 59, 59)
                }
            },
            {"_id": 0}
        ).to_list(50)
        
        summary = {
            "total_found": len(fixtures),
            "date_range": "Dec 6-8, 2025",
            "current_server_time": datetime.now().isoformat(),
            "fixtures": []
        }
        
        for fix in fixtures[:20]:
            summary["fixtures"].append({
                "date": str(fix.get('utc_date'))[:16],
                "status": fix.get('status'),
                "match": f"{fix.get('home_team')} vs {fix.get('away_team')}",
                "league": fix.get('league_name'),
                "has_scores": fix.get('home_score') is not None
            })
        
        return summary
    except Exception as e:
        return {"error": str(e)}


@api_router.get("/admin/test-date-query")
async def test_date_query(days_ahead: int = 28):
    """Test what the date query returns"""
    try:
        from datetime import datetime, timedelta, timezone
        
        now = datetime.now(timezone.utc)
        start_date = now.replace(tzinfo=None) - timedelta(days=3)
        end_date = now.replace(tzinfo=None) + timedelta(days=days_ahead)
        
        # Same query as get_fixtures
        count = await db.fixtures.count_documents({
            "utc_date": {
                "$gte": start_date,
                "$lte": end_date,
                "$ne": None
            }
        })
        
        # Sample fixtures
        samples = await db.fixtures.find(
            {
                "utc_date": {
                    "$gte": start_date,
                    "$lte": end_date,
                    "$ne": None
                }
            },
            {"_id": 0, "home_team": 1, "away_team": 1, "utc_date": 1, "matchday": 1}
        ).sort("utc_date", 1).limit(20).to_list(20)
        
        return {
            "query_params": {
                "days_ahead": days_ahead,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "now": str(now)
            },
            "total_found": count,
            "sample_fixtures": [
                {
                    "date": str(f.get('utc_date'))[:16] if f.get('utc_date') else "NO DATE",
                    "match": f"{f.get('home_team')} vs {f.get('away_team')}",
                    "matchday": f.get('matchday')
                }
                for f in samples
            ]
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@api_router.get("/admin/check-future-fixtures")
async def check_future_fixtures():
    """Check what fixtures exist after Dec 8, 2025"""
    try:
        from datetime import datetime
        
        # Count fixtures after Dec 8
        after_dec8 = await db.fixtures.count_documents({
            "utc_date": {"$gt": datetime(2025, 12, 8, 23, 59, 59)}
        })
        
        # Count fixtures with NULL dates
        null_dates = await db.fixtures.count_documents({
            "utc_date": None
        })
        
        # Sample fixtures Dec 9-15
        sample = await db.fixtures.find(
            {
                "utc_date": {
                    "$gte": datetime(2025, 12, 9, 0, 0, 0),
                    "$lte": datetime(2025, 12, 15, 23, 59, 59)
                }
            },
            {"_id": 0, "home_team": 1, "away_team": 1, "utc_date": 1, "matchday": 1}
        ).limit(10).to_list(10)
        
        return {
            "fixtures_after_dec8": after_dec8,
            "fixtures_with_null_dates": null_dates,
            "sample_dec9_15": [
                {
                    "match": f"{f.get('home_team')} vs {f.get('away_team')}",
                    "date": str(f.get('utc_date'))[:16],
                    "matchday": f.get('matchday')
                }
                for f in sample
            ]
        }
    except Exception as e:
        return {"error": str(e)}

# Fixtures endpoint continues...


@api_router.get("/matchdays")
async def get_available_matchdays(league_id: int = 39):
    """
    Get list of available matchdays for a league
    Returns sorted list of matchdays with fixture counts
    """
    try:
        # Get all fixtures for this league from database
        fixtures = await db.fixtures.find(
            {"league_id": league_id},
            {"matchday": 1, "status": 1, "_id": 0}
        ).to_list(1000)
        
        # Group by matchday
        matchday_counts = {}
        for fixture in fixtures:
            md = fixture.get('matchday', 'Unknown')
            # Extract number from matchday string (e.g., "Regular Season - 10" -> "10")
            md_number = md.split('-')[-1].strip() if '-' in md else md
            
            if md_number not in matchday_counts:
                matchday_counts[md_number] = {'total': 0, 'finished': 0}
            
            matchday_counts[md_number]['total'] += 1
            if fixture.get('status') == 'FINISHED':
                matchday_counts[md_number]['finished'] += 1
        
        # Format response
        result = []
        for md, counts in sorted(matchday_counts.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
            result.append({
                'matchday': md,
                'total_fixtures': counts['total'],
                'finished_fixtures': counts['finished'],
                'label': f"Matchday {md}"
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching matchdays: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/matchweeks")
async def get_matchweeks():
    """Get current and upcoming matchweeks with fixtures grouped"""
    try:
        # Get Premier League fixtures (14 days to cover 2 matchweeks)
        fixtures = await football_data.get_upcoming_fixtures([39], days_ahead=14)
        
        if not fixtures:
            return {"matchweeks": [], "current": None}
        
        # Group by matchweek
        matchweeks_data = matchweek_service.get_matchweek_from_fixtures(fixtures)
        current_matchweek = matchweek_service.get_current_matchweek(fixtures)
        
        # Get detailed info for each matchweek
        result = []
        for matchweek in sorted(matchweeks_data.keys()):
            info = matchweek_service.get_matchweek_info(fixtures, matchweek)
            status = matchweek_service.get_matchweek_status(info)
            
            result.append({
                "matchweek": matchweek,
                "status": status,
                "date_range": matchweek_service.format_matchweek_dates(info),
                "total_matches": info['total_matches'],
                "start_date": info['start_date'].isoformat() if info['start_date'] else None,
                "end_date": info['end_date'].isoformat() if info['end_date'] else None,
            })
        
        return {
            "matchweeks": result,
            "current": current_matchweek
        }
    
    except Exception as e:
        logger.error(f"Error fetching matchweeks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/standings")
async def get_league_standings(league_ids: str = "39"):
    """
    Get current league standings/tables for specified leagues
    Args:
        league_ids: Comma-separated league IDs (e.g., "39,140,78")
    Returns:
        Dictionary with standings for each league
    """
    try:
        league_id_list = [int(lid.strip()) for lid in league_ids.split(',')]
        service = get_active_football_service()
        
        all_standings = {}
        
        for league_id in league_id_list:
            try:
                # Find the correct season for this league
                league_season = 2025  # default
                for league in SUPPORTED_LEAGUES:
                    if league['id'] == league_id:
                        league_season = league['season']
                        break
                
                standings_data = await service.get_league_standings(league_id, season=league_season)
                
                if standings_data and len(standings_data) > 0:
                    league_data = standings_data[0]
                    league_info = league_data.get('league', {})
                    standings_list = league_info.get('standings', [[]])[0]  # Get first standings group
                    
                    # Transform to simpler format
                    formatted_standings = []
                    for team_data in standings_list:
                        formatted_standings.append({
                            'rank': team_data.get('rank'),
                            'team_name': team_data['team']['name'],
                            'team_logo': team_data['team'].get('logo'),
                            'played': team_data['all']['played'],
                            'won': team_data['all']['win'],
                            'drawn': team_data['all']['draw'],
                            'lost': team_data['all']['lose'],
                            'goals_for': team_data['all']['goals']['for'],
                            'goals_against': team_data['all']['goals']['against'],
                            'goal_difference': team_data['goalsDiff'],
                            'points': team_data['points'],
                            'form': team_data.get('form', ''),
                            'description': team_data.get('description')
                        })
                    
                    all_standings[str(league_id)] = {
                        'league_name': league_info.get('name'),
                        'country': league_info.get('country'),
                        'logo': league_info.get('logo'),
                        'season': league_info.get('season'),
                        'standings': formatted_standings
                    }
            except Exception as e:
                logger.error(f"Error fetching standings for league {league_id}: {str(e)}")
                continue
        
        return all_standings
        
    except Exception as e:
        logger.error(f"Error fetching league standings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching standings: {str(e)}")


# ========== USER ENDPOINTS ==========
# NOTE: User endpoints have been moved to routes/auth.py
# Keeping this section marker for reference


# ========== PREDICTION ENDPOINTS ==========

@api_router.post("/predictions", response_model=Prediction)
async def create_or_update_prediction(pred: PredictionCreate):
    """Submit or update a prediction - allows changes until deadline"""
    if pred.prediction not in ["home", "draw", "away"]:
        raise HTTPException(status_code=400, detail="Prediction must be 'home', 'draw', or 'away'")
    
    # Check if user exists
    user = await db.users.find_one({"id": pred.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check deadline - Wednesday 23:59 OR match kickoff (whichever comes first)
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    # Check 1: Weekly deadline (Wednesday 23:59 UTC)
    # Get the next Wednesday at 23:59
    days_until_wednesday = (2 - now.weekday()) % 7  # Wednesday is day 2
    if days_until_wednesday == 0 and now.hour >= 23 and now.minute >= 59:
        days_until_wednesday = 7  # If past deadline, next Wednesday
    
    weekly_deadline = now.replace(hour=23, minute=59, second=59, microsecond=0)
    weekly_deadline = weekly_deadline + timedelta(days=days_until_wednesday)
    
    # Check 2: Match kickoff time - ensure timezone-aware
    match_date = datetime.fromisoformat(pred.match_date.replace('Z', '+00:00'))
    # Ensure match_date is timezone-aware (convert if naive)
    if match_date.tzinfo is None:
        match_date = match_date.replace(tzinfo=timezone.utc)
    
    # Determine which deadline applies (both are now timezone-aware)
    effective_deadline = min(weekly_deadline, match_date)
    
    if now >= effective_deadline:
        hours_until = int((effective_deadline - now).total_seconds() / 3600)
        if hours_until < 0:
            raise HTTPException(
                status_code=400, 
                detail="Predictions are locked. Deadline has passed."
            )
    
    # Check if prediction already exists
    existing = await db.predictions.find_one({
        "user_id": pred.user_id,
        "fixture_id": pred.fixture_id
    })
    
    # Get week_id from match date
    week_id = get_week_id(match_date)
    
    if existing:
        # UPDATE existing prediction - also refresh fixture details
        fixture = await db.fixtures.find_one({"fixture_id": pred.fixture_id})
        
        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")
        
        # Get user email from database
        user = await db.users.find_one({"id": pred.user_id})
        
        # Update prediction with refreshed fixture details
        match_date_value = fixture.get('utc_date') or fixture.get('match_date')
        if isinstance(match_date_value, datetime):
            match_date_value = match_date_value.isoformat()
        
        await db.predictions.update_one(
            {"user_id": pred.user_id, "fixture_id": pred.fixture_id},
            {"$set": {
                "prediction": pred.prediction,
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "home_team": fixture.get('home_team'),
                "away_team": fixture.get('away_team'),
                "league": fixture.get('league_name'),
                "match_date": match_date_value,
                "status": fixture.get('status', 'SCHEDULED'),
                "user_email": user.get("email") if user else existing.get("user_email")
            }}
        )
        
        # Send email confirmation
        try:
            if user and user.get('email'):
                await send_prediction_email(user.get('email'), user.get('username'), {
                    'home_team': fixture.get('home_team'),
                    'away_team': fixture.get('away_team'),
                    'prediction': pred.prediction,
                    'league': fixture.get('league_name'),
                    'match_date': match_date_value
                }, is_update=True)
        except Exception as e:
            logger.error(f"Failed to send prediction email: {str(e)}")
        
        # Return updated prediction
        updated = await db.predictions.find_one({
            "user_id": pred.user_id,
            "fixture_id": pred.fixture_id
        }, {"_id": 0})
        
        return Prediction(**updated)
    else:
        # CREATE new prediction - fetch fixture details to store with prediction
        fixture = await db.fixtures.find_one({"fixture_id": pred.fixture_id})
        
        if not fixture:
            raise HTTPException(status_code=404, detail="Fixture not found")
        
        # Create prediction with fixture details embedded
        pred_dict = pred.model_dump()
        
        # Get user email from database
        user = await db.users.find_one({"id": pred.user_id})
        
        # Convert match_date to ISO format if it's a datetime object
        match_date_value = fixture.get('utc_date') or fixture.get('match_date')
        if isinstance(match_date_value, datetime):
            match_date_value = match_date_value.isoformat()
        
        pred_dict.update({
            "week_id": week_id,
            "result": "pending",
            "user_email": user.get("email") if user else None,
            "home_team": fixture.get('home_team'),
            "away_team": fixture.get('away_team'),
            "league": fixture.get('league_name'),
            "match_date": match_date_value,
            "home_score": None,
            "away_score": None
        })
        
        pred_obj = Prediction(**pred_dict)
        doc = pred_obj.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        
        await db.predictions.insert_one(doc)
        
        # Send email confirmation
        try:
            if user and user.get('email'):
                await send_prediction_email(user.get('email'), user.get('username'), {
                    'home_team': fixture.get('home_team'),
                    'away_team': fixture.get('away_team'),
                    'prediction': pred.prediction,
                    'league': fixture.get('league_name'),
                    'match_date': match_date_value
                }, is_update=False)
        except Exception as e:
            logger.error(f"Failed to send prediction email: {str(e)}")
        
        return pred_obj


@api_router.get("/predictions/user/{user_id}")
async def get_user_predictions(user_id: str):
    """Get all predictions for a user with fixture details"""
    # Use aggregation to join predictions with fixtures
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "fixtures",
            "localField": "fixture_id",
            "foreignField": "fixture_id",
            "as": "fixture_data"
        }},
        {"$unwind": "$fixture_data"},
        {"$sort": {"fixture_data.match_date": 1}}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(length=1000)
    return [Prediction(**{**r, "_id": str(r["_id"])}) if "_id" in r else Prediction(**r) for r in results]



@api_router.delete("/predictions/{prediction_id}")
async def delete_prediction(prediction_id: str, user_id: str):
    """
    Delete a prediction
    - Only allows deleting your own predictions
    - Cannot delete predictions for matches that have already started
    """
    from datetime import datetime, timezone
    
    # Find the prediction
    prediction = await db.predictions.find_one({"id": prediction_id}, {"_id": 0})
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Verify ownership
    if prediction.get('user_id') != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own predictions")
    
    # Get the fixture to check if it's started
    fixture = await db.fixtures.find_one({"fixture_id": prediction['fixture_id']}, {"_id": 0})
    
    if fixture:
        # Check if match has started (status is not SCHEDULED)
        if fixture.get('status') not in ['SCHEDULED', 'TBD', 'NS']:
            raise HTTPException(status_code=400, detail="Cannot delete prediction for a match that has already started")
        
        # Also check by date - if match date is in the past, don't allow deletion
        match_date_str = fixture.get('utc_date')
        if match_date_str:
            try:
                match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
                if match_date < datetime.now(timezone.utc):
                    raise HTTPException(status_code=400, detail="Cannot delete prediction for a match that has already started")
            except:
                pass  # If date parsing fails, allow deletion (better safe than blocking)
    
    # Delete the prediction
    result = await db.predictions.delete_one({"id": prediction_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    logger.info(f"Deleted prediction {prediction_id} for user {user_id}")
    return {"message": "Prediction deleted successfully", "prediction_id": prediction_id}


@api_router.get("/predictions/deadline-status")
async def get_deadline_status():
    """
    Get current deadline status for predictions
    Returns info about when predictions lock
    """
    from datetime import datetime, timezone, timedelta
    
    now = datetime.now(timezone.utc)
    
    # Calculate next Wednesday 23:59
    days_until_wednesday = (2 - now.weekday()) % 7
    if days_until_wednesday == 0 and now.hour >= 23 and now.minute >= 59:
        days_until_wednesday = 7
    
    weekly_deadline = now.replace(hour=23, minute=59, second=59, microsecond=0)
    weekly_deadline = weekly_deadline + timedelta(days=days_until_wednesday)
    
    # Calculate time remaining
    time_remaining = weekly_deadline - now
    hours_remaining = int(time_remaining.total_seconds() / 3600)
    minutes_remaining = int((time_remaining.total_seconds() % 3600) / 60)
    
    is_locked = now >= weekly_deadline
    
    return {
        "is_locked": is_locked,
        "weekly_deadline": weekly_deadline.isoformat(),
        "hours_remaining": hours_remaining,
        "minutes_remaining": minutes_remaining,
        "message": f"Predictions close in {hours_remaining}h {minutes_remaining}m" if not is_locked else "Predictions are locked",
        "can_change": not is_locked
    }


@api_router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 20, season: bool = False, weekly: bool = False):
    """Get global leaderboard - ALL players across ALL teams"""
    try:
        # Choose which points to use
        if weekly:
            sort_field = "weekly_points"
        else:
            sort_field = "season_points"
        
        # Get all users with points
        pipeline = [
            {"$match": {sort_field: {"$exists": True}}},
            {
                "$lookup": {
                    "from": "predictions",
                    "localField": "id",
                    "foreignField": "user_id",
                    "as": "predictions"
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "username": 1,
                    "email": 1,
                    "season_points": {"$ifNull": ["$season_points", 0]},
                    "weekly_points": {"$ifNull": ["$weekly_points", 0]},
                    "weekly_wins": {"$ifNull": ["$weekly_wins", 0]},
                    "total_predictions": {"$size": "$predictions"},
                    "correct_predictions": {
                        "$size": {
                            "$filter": {
                                "input": "$predictions",
                                "as": "pred",
                                "cond": {"$eq": ["$$pred.result", "correct"]}
                            }
                        }
                    }
                }
            },
            {"$sort": {sort_field: -1}},
            {"$limit": limit}
        ]
        
        results = await db.users.aggregate(pipeline).to_list(None)
        
        # Assign ranks and add team names
        for user in results:
            user['total_points'] = user[sort_field]
            
            # Get user's primary team (first team they joined)
            membership = await db.team_members.find_one({"user_id": user['id']}, {"_id": 0})
            if membership:
                team = await db.teams.find_one({"id": membership['team_id']}, {"_id": 0, "name": 1})
                # Normalize team name to uppercase for consistency
                team_name = team.get('name') if team else 'No Team'
                user['team_name'] = team_name.upper() if team_name != 'No Team' else 'No Team'
            else:
                user['team_name'] = 'No Team'
        
        # Sort: Team members first (sorted by points), then non-team members (sorted by points)
        results.sort(key=lambda x: (
            x['team_name'] == 'No Team',  # False (team members) come before True (no team)
            -x['total_points'],           # Higher points first
            -x['correct_predictions']      # Tie-breaker: more correct predictions
        ))
        
        # Assign ranks after sorting
        for idx, user in enumerate(results):
            user['rank'] = idx + 1
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/leaderboard/weekly")
async def get_weekly_leaderboard(limit: int = 20):
    """Get weekly leaderboard (resets each matchday)"""
    return await get_leaderboard(limit=limit, weekly=True)


# ========== WEEKLY POT ENDPOINTS ==========

@api_router.get("/pot/current")
async def get_current_pot():
    """Get current week pot information"""
    # Get team settings to check play mode
    settings = await db.team_settings.find_one({}, {"_id": 0})
    play_mode = settings.get('play_mode', 'fun') if settings else 'fun'
    
    if play_mode == 'fun':
        # Fun mode - no money involved
        return {
            "play_mode": "fun",
            "message": "Playing for fun - no pot this week",
            "week_id": get_current_week_dates()['week_id']
        }
    
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
        "play_mode": "pot",
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
    settings = await db.team_settings.find_one({})
    if not settings:
        settings = {
            "team_name": "My Predictions Team",
            "play_mode": "fun",  # Default to fun mode
            "stake_amount": 5.0,
            "admin_fee_percentage": 10.0,
            "charity_mode": False,
            "min_members": 2,
            "max_members": 30,
            "season_prize_pool": 0
        }
        result = await db.team_settings.insert_one(settings)
        settings['_id'] = result.inserted_id
    
    # Remove MongoDB _id for JSON serialization
    if '_id' in settings:
        del settings['_id']
    
    # Get current member count
    member_count = await db.users.count_documents({})
    settings['current_members'] = member_count
    
    return settings


@api_router.put("/settings/team")
async def update_team_settings(settings: dict):
    """Update team settings (Admin only)"""
    # Validate team size limits
    if 'min_members' in settings and settings['min_members'] < 2:
        raise HTTPException(status_code=400, detail="Minimum members must be at least 2")
    
    if 'max_members' in settings and settings['max_members'] > 30:
        raise HTTPException(status_code=400, detail="Maximum members cannot exceed 30")
    
    await db.team_settings.update_one(
        {},
        {"$set": settings},
        upsert=True
    )
    return {"message": "Settings updated"}


@api_router.get("/admin/test-sportmonks")
async def test_sportmonks_connection():
    """Test Sportmonks API connection and functionality"""
    try:
        from sportmonks_service import SportmonksService
        
        service = SportmonksService()
        
        # Test connection
        connection_test = await service.test_connection()
        
        # Test getting fixtures for a recent date (try to find West Ham vs Sunderland)
        test_date = "2025-08-16"  # Opening day of 2025-26 season
        fixtures = await service.get_fixtures_by_date(test_date, league_id=39)  # Premier League
        
        return {
            "sportmonks_available": await service.is_available(),
            "connection_test": connection_test,
            "test_fixtures": {
                "date": test_date,
                "count": len(fixtures),
                "fixtures": fixtures[:3] if fixtures else []  # Show first 3 fixtures
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing Sportmonks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sportmonks test failed: {str(e)}")


    """Reset all user and team scores to zero (Admin only)"""
    try:
        # Reset all user scores
        users_result = await db.users.update_many({}, {
            "$set": {
                "total_points": 0,
                "season_points": 0, 
                "weekly_points": 0,
                "weekly_wins": 0,
                "correct_predictions": 0,
                "incorrect_predictions": 0,
                "total_predictions": 0
            }
        })
        
        # Reset team stats if they exist
        teams_result = await db.teams.update_many({}, {
            "$set": {
                "total_points": 0,
                "season_points": 0,
                "weekly_points": 0
            }
        })
        
        # Reset weekly pots to inactive status
        pots_result = await db.weekly_pots.update_many({}, {
            "$set": {
                "status": "inactive",
                "total_amount": 0,
                "winner": None
            }
        })
        
        # Reset all prediction scores
        predictions_result = await db.predictions.update_many({}, {
            "$set": {
                "correct": None,
                "points_awarded": 0
            }
        })
        
        logger.info(f"✅ Scores reset: {users_result.modified_count} users, {teams_result.modified_count} teams, {pots_result.modified_count} pots, {predictions_result.modified_count} predictions")
        
        return {
            "message": "All scores reset to zero successfully",
            "users_updated": users_result.modified_count,
            "teams_updated": teams_result.modified_count, 
            "pots_updated": pots_result.modified_count,
            "predictions_updated": predictions_result.modified_count
        }
        
    except Exception as e:
        logger.error(f"Error resetting scores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset scores: {str(e)}")


# ========== TEAM ENDPOINTS ==========

@api_router.post("/teams", response_model=Team)
async def create_team(team: TeamCreate):
    """Create a new team"""
    # Check if team name already exists
    existing = await db.teams.find_one({"name": team.name})
    if existing:
        raise HTTPException(status_code=400, detail="Team name already exists")
    
    team_obj = Team(**team.model_dump())
    doc = team_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.teams.insert_one(doc)
    
    # Add admin as first member
    member = TeamMember(
        team_id=team_obj.id,
        user_id=team.admin_user_id,
        username=team.admin_username,
        role="admin"
    )
    member_doc = member.model_dump()
    member_doc['joined_at'] = member_doc['joined_at'].isoformat()
    await db.team_members.insert_one(member_doc)
    
    # Update member count
    await db.teams.update_one(
        {"id": team_obj.id},
        {"$set": {"member_count": 1}}
    )
    
    return team_obj


@api_router.get("/teams/{team_id}")
async def get_team(team_id: str):
    """Get team details"""
    team = await db.teams.find_one({"id": team_id}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if isinstance(team.get('created_at'), str):
        team['created_at'] = datetime.fromisoformat(team['created_at'])
    
    return team


@api_router.post("/teams/join")
async def join_team(join_data: TeamJoin):
    """Join a team using join code"""
    # Find team by join code
    team = await db.teams.find_one({"join_code": join_data.join_code}, {"_id": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Invalid join code")
    
    # Check if user already in team
    existing = await db.team_members.find_one({
        "team_id": team['id'],
        "user_id": join_data.user_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already a member of this team")
    
    # Check team capacity (max 30)
    member_count = await db.team_members.count_documents({"team_id": team['id']})
    if member_count >= 30:
        raise HTTPException(status_code=400, detail="Team is full (30 members max)")
    
    # Add member
    member = TeamMember(
        team_id=team['id'],
        user_id=join_data.user_id,
        username=join_data.username
    )
    member_doc = member.model_dump()
    member_doc['joined_at'] = member_doc['joined_at'].isoformat()
    await db.team_members.insert_one(member_doc)
    
    # Update member count
    await db.teams.update_one(
        {"id": team['id']},
        {"$inc": {"member_count": 1}}
    )
    
    return {
        "message": f"Successfully joined {team['name']}",
        "team": team
    }


@api_router.get("/teams/{team_id}/members")
async def get_team_members(team_id: str):
    """Get all members of a team"""
    members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
    
    for member in members:
        if isinstance(member.get('joined_at'), str):
            member['joined_at'] = datetime.fromisoformat(member['joined_at'])
    
    return members


@api_router.get("/teams/{team_id}/leaderboard")
async def get_team_leaderboard(team_id: str, weekly: bool = False):
    """Get leaderboard for a specific team (PRIVATE to team) - Shows ALL members"""
    # Get team members
    members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
    member_ids = [m['user_id'] for m in members]
    
    # Choose which points to use
    sort_field = "weekly_points" if weekly else "season_points"
    
    # Get predictions stats for team members only
    pipeline = [
        {"$match": {"user_id": {"$in": member_ids}}},
        {
            "$group": {
                "_id": "$user_id",
                "username": {"$first": "$username"},
                "total_predictions": {"$sum": 1},
                "correct_predictions": {
                    "$sum": {"$cond": [{"$eq": ["$result", "correct"]}, 1, 0]}
                }
            }
        }
    ]
    
    stats = await db.predictions.aggregate(pipeline).to_list(None)
    
    # Create a map of user_id to their prediction stats
    stats_map = {stat["_id"]: stat for stat in stats}
    
    # Get user details for ALL team members (not just those with predictions)
    leaderboard = []
    for member_id in member_ids:
        user = await db.users.find_one({"id": member_id}, {"_id": 0})
        if user:
            stat = stats_map.get(member_id)
            leaderboard.append({
                "username": user['username'],
                "total_points": user.get(sort_field, 0),
                "correct_predictions": stat['correct_predictions'] if stat else 0,
                "total_predictions": stat['total_predictions'] if stat else 0,
                "weekly_wins": user.get('weekly_wins', 0),
                "rank": 0
            })
    
    # Sort by points (then by correct predictions as tiebreaker)
    leaderboard.sort(key=lambda x: (x['total_points'], x['correct_predictions']), reverse=True)
    
    # Assign ranks
    for idx, entry in enumerate(leaderboard):
        entry['rank'] = idx + 1
    
    return leaderboard


@api_router.get("/teams/{team_id}/leaderboard")
async def get_team_leaderboard(team_id: str):
    """
    Get unified team leaderboard showing all members and their overall stats
    Single leaderboard per team - no league tabs needed
    """
    # Get team members
    members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
    member_ids = [m['user_id'] for m in members]
    
    if not member_ids:
        return []
    
    # Get overall stats for each team member
    leaderboard = []
    
    for member_id in member_ids:
        # Get user details
        user = await db.users.find_one({"id": member_id}, {"_id": 0})
        if not user:
            continue
        
        # Get total points from user record
        total_points = user.get('season_points', 0)
        
        # Get prediction stats
        predictions = await db.predictions.find({"user_id": member_id}, {"_id": 0}).to_list(10000)
        total_predictions = len(predictions)
        correct_predictions = len([p for p in predictions if p.get('result') == 'correct'])
        
        # Get matchday wins count
        matchday_wins = await db.user_league_points.count_documents({"user_id": member_id})
        
        leaderboard.append({
            'username': user.get('username', 'Unknown'),
            'total_points': total_points,
            'matchday_wins': matchday_wins,
            'correct_predictions': correct_predictions,
            'total_predictions': total_predictions,
            'rank': 0  # Will be assigned after sorting
        })
    
    # Sort by total points, then by correct predictions
    leaderboard.sort(key=lambda x: (x['total_points'], x['correct_predictions']), reverse=True)
    
    # Assign ranks
    for idx, entry in enumerate(leaderboard):
        entry['rank'] = idx + 1
    
    return leaderboard


@api_router.get("/user/{user_id}/team")
async def get_user_team(user_id: str):
    """Get user's team membership"""
    team_member = await db.team_members.find_one({"user_id": user_id}, {"_id": 0})
    if not team_member:
        return {"team": None, "membership": None}
    
    team = await db.teams.find_one({"id": team_member['team_id']}, {"_id": 0})
    return {"team": team, "membership": team_member}


def normalize_league_name(league_name: str) -> str:
    """Normalize league names to merge duplicates"""
    if not league_name:
        return "Unknown League"
    
    # Remove country suffixes in parentheses
    import re
    normalized = re.sub(r'\s*\([^)]*\)\s*$', '', league_name).strip()
    return normalized if normalized else league_name


@api_router.get("/teams/{team_id}/leaderboard/by-league")
async def get_team_leaderboard_by_league(team_id: str):
    """SIMPLIFIED team leaderboard by league - NO DUPLICATES ALL USERS"""
    logger.info(f"📊 Leaderboard request for team: {team_id}")
    # Get team members
    members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
    member_ids = [m['user_id'] for m in members]
    logger.info(f"Found {len(member_ids)} members")
    
    if not member_ids:
        logger.warning("No members found, returning empty list")
        return []
    
    # Build leaderboard by getting ALL predictions for each member
    leagues = {}
    
    for member_id in member_ids:
        # Get user info
        user = await db.users.find_one({"id": member_id}, {"_id": 0})
        if not user:
            continue
        
        username = user.get('username', 'Unknown')
        
        # Get all predictions for this user
        predictions = await db.predictions.find({"user_id": member_id}, {"_id": 0}).to_list(10000)
        
        # Group predictions by NORMALIZED league name
        user_leagues = {}
        for pred in predictions:
            league_name = normalize_league_name(pred.get('league', 'Unknown'))
            
            if league_name not in user_leagues:
                user_leagues[league_name] = {
                    'correct': 0,
                    'total': 0
                }
            
            user_leagues[league_name]['total'] += 1
            if pred.get('result') == 'correct':
                user_leagues[league_name]['correct'] += 1
        
        # Get matchday wins for this user
        wins_by_league = {}
        league_points_docs = await db.user_league_points.find({"user_id": member_id}, {"_id": 0}).to_list(10000)
        
        for lp in league_points_docs:
            league_name = normalize_league_name(lp.get('league_name', 'Unknown'))
            if league_name not in wins_by_league:
                wins_by_league[league_name] = {'wins': 0, 'points': 0}
            wins_by_league[league_name]['wins'] += 1
            wins_by_league[league_name]['points'] += lp.get('points', 0)
        
        # Add user to each league they participated in
        for league_name, stats in user_leagues.items():
            if league_name not in leagues:
                leagues[league_name] = []
            
            wins_data = wins_by_league.get(league_name, {'wins': 0, 'points': 0})
            
            leagues[league_name].append({
                'username': username,
                'total_points': wins_data['points'],
                'matchday_wins': wins_data['wins'],
                'correct_predictions': stats['correct'],
                'total_predictions': stats['total']
            })
    
    # Build result with current matchday info
    result = []
    for league_name, members_data in leagues.items():
        # Sort by points, then correct predictions
        members_data.sort(key=lambda x: (x['total_points'], x['correct_predictions']), reverse=True)
        
        # Assign ranks
        for idx, member in enumerate(members_data):
            member['rank'] = idx + 1
        
        # Get current matchday for this league (most recent matchday with fixtures)
        latest_fixture = await db.fixtures.find_one(
            {"league_name": {"$regex": league_name.split("(")[0].strip(), "$options": "i"}},
            {"_id": 0, "matchday": 1},
            sort=[("utc_date", -1)]
        )
        current_matchday = latest_fixture.get('matchday') if latest_fixture else None
        
        result.append({
            'league_name': league_name,
            'current_matchday': current_matchday,
            'leaderboard': members_data
        })
    
    # Sort leagues alphabetically
    result.sort(key=lambda x: x['league_name'])
    
    return result


@api_router.get("/admin/debug/team-database/{team_id}")
async def debug_team_database(team_id: str):
    """
    🔍 Debug endpoint to inspect raw database state for a team
    Shows: members, predictions grouped by league name, potential duplicates
    
    Usage after deployment:
    curl "https://your-app-url.com/api/admin/debug/team-database/{team_id}"
    """
    try:
        # Get team info
        team = await db.teams.find_one({"id": team_id}, {"_id": 0})
        if not team:
            return {"error": "Team not found"}
        
        # Get all team members
        members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
        member_ids = [m['user_id'] for m in members]
        
        # Get all users
        users = await db.users.find({"id": {"$in": member_ids}}, {"_id": 0}).to_list(100)
        user_map = {u['id']: u.get('username', 'Unknown') for u in users}
        
        # Get all predictions for team members
        predictions = await db.predictions.find(
            {"user_id": {"$in": member_ids}}, 
            {"_id": 0}
        ).to_list(10000)
        
        # Group predictions by league name (RAW - showing duplicates if any)
        league_summary = {}
        for pred in predictions:
            league_name = pred.get('league', 'Unknown')
            league_id = pred.get('league_id', 'N/A')
            user_id = pred.get('user_id')
            username = user_map.get(user_id, 'Unknown')
            
            key = f"{league_name} (ID: {league_id})"
            if key not in league_summary:
                league_summary[key] = {
                    'raw_name': league_name,
                    'normalized_name': normalize_league_name(league_name),
                    'league_id': league_id,
                    'total_predictions': 0,
                    'users': {}
                }
            
            league_summary[key]['total_predictions'] += 1
            
            if username not in league_summary[key]['users']:
                league_summary[key]['users'][username] = 0
            league_summary[key]['users'][username] += 1
        
        # Get league points
        league_points = await db.user_league_points.find(
            {"user_id": {"$in": member_ids}},
            {"_id": 0}
        ).to_list(10000)
        
        # Check for duplicate league names
        duplicate_leagues = {}
        league_ids = {}
        for key, data in league_summary.items():
            league_id = data['league_id']
            if league_id not in league_ids:
                league_ids[league_id] = []
            league_ids[league_id].append(data['raw_name'])
        
        for league_id, names in league_ids.items():
            if len(names) > 1:
                duplicate_leagues[league_id] = {
                    'league_id': league_id,
                    'duplicate_names': names,
                    'normalized_to': normalize_league_name(names[0])
                }
        
        return {
            "team": {
                "id": team_id,
                "name": team.get('name'),
                "member_count": len(members)
            },
            "members": [
                {
                    "username": user_map.get(m['user_id'], 'Unknown'),
                    "user_id": m['user_id']
                }
                for m in members
            ],
            "league_summary": league_summary,
            "duplicate_leagues": duplicate_leagues,
            "league_points_count": len(league_points),
            "total_predictions": len(predictions),
            "note": "duplicate_leagues shows which leagues have inconsistent naming that will be normalized"
        }
        
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@api_router.get("/admin/debug/test-normalization")
async def debug_test_normalization():
    """
    🧪 Test the league name normalization function
    Shows how different league names will be normalized
    """
    test_cases = [
        "Championship",
        "Championship (England)",
        "Premier League",
        "Premier League (England)",
        "La Liga",
        "La Liga (Spain)",
        "UEFA Champions League",
        "UEFA Europa League (Europe)",
    ]
    
    results = {}
    for name in test_cases:
        results[name] = normalize_league_name(name)
    
    return {
        "normalization_examples": results,
        "note": "Names with the same normalized value will be merged in leaderboards"
    }


@api_router.get("/admin/debug/user-team-data/{username}")
async def debug_user_team_data(username: str):
    """
    🔍 Debug endpoint - Find team and database state by username
    Easier than needing team_id
    
    Usage: /api/admin/debug/user-team-data/aysin
    """
    try:
        # Find user
        user = await db.users.find_one({"username": username}, {"_id": 0})
        if not user:
            return {"error": f"User '{username}' not found"}
        
        user_id = user['id']
        
        # Find team membership
        team_member = await db.team_members.find_one({"user_id": user_id}, {"_id": 0})
        if not team_member:
            return {"error": f"User '{username}' is not in any team"}
        
        team_id = team_member['team_id']
        
        # Get team info
        team = await db.teams.find_one({"id": team_id}, {"_id": 0})
        
        # Get all team members
        members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
        member_ids = [m['user_id'] for m in members]
        
        # Get all users
        users = await db.users.find({"id": {"$in": member_ids}}, {"_id": 0}).to_list(100)
        user_map = {u['id']: u.get('username', 'Unknown') for u in users}
        
        # Get all predictions for team members
        predictions = await db.predictions.find(
            {"user_id": {"$in": member_ids}}, 
            {"_id": 0}
        ).to_list(10000)
        
        # Group predictions by league and user
        league_summary = {}
        for pred in predictions:
            league_name = pred.get('league', 'Unknown')
            league_id = pred.get('league_id', 'N/A')
            user_id_pred = pred.get('user_id')
            username_pred = user_map.get(user_id_pred, 'Unknown')
            result = pred.get('result', 'pending')
            
            # Use normalized name as key
            normalized = normalize_league_name(league_name)
            key = f"{normalized} (ID: {league_id})"
            
            if key not in league_summary:
                league_summary[key] = {
                    'normalized_name': normalized,
                    'league_id': league_id,
                    'raw_names_seen': set(),
                    'users': {}
                }
            
            # Track raw names
            league_summary[key]['raw_names_seen'].add(league_name)
            
            if username_pred not in league_summary[key]['users']:
                league_summary[key]['users'][username_pred] = {
                    'total': 0,
                    'correct': 0,
                    'incorrect': 0,
                    'pending': 0
                }
            
            league_summary[key]['users'][username_pred]['total'] += 1
            league_summary[key]['users'][username_pred][result] += 1
        
        # Convert sets to lists for JSON serialization
        for league in league_summary.values():
            league['raw_names_seen'] = list(league['raw_names_seen'])
        
        # Check for users with NO predictions
        users_with_no_predictions = []
        for uid, uname in user_map.items():
            user_pred_count = len([p for p in predictions if p['user_id'] == uid])
            if user_pred_count == 0:
                users_with_no_predictions.append(uname)
        
        return {
            "requested_user": username,
            "team": {
                "id": team_id,
                "name": team.get('name'),
                "total_members": len(members)
            },
            "all_team_members": list(user_map.values()),
            "users_with_no_predictions": users_with_no_predictions,
            "league_summary": league_summary,
            "total_predictions": len(predictions),
            "note": "Check 'users' under each league to see who has predictions and who is missing"
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e), 
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }



@api_router.get("/teams/{team_id}/leaderboard/by-league-old")
async def get_team_leaderboard_by_league_old(team_id: str):
    """
    Get team leaderboard grouped by league
    Returns separate leaderboard for each league showing who won in that league
    Used by main Leaderboard tab to show league-specific standings
    """
    # Get team members
    members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
    member_ids = [m['user_id'] for m in members]
    
    if not member_ids:
        return []
    
    # Get all league points for team members
    league_points = await db.user_league_points.find(
        {"user_id": {"$in": member_ids}},
        {"_id": 0}
    ).to_list(10000)
    
    # Also get prediction stats for each user per league
    pipeline = [
        {"$match": {"user_id": {"$in": member_ids}}},
        {
            "$group": {
                "_id": {
                    "user_id": "$user_id",
                    "league_id": "$league_id"
                },
                "username": {"$first": "$username"},
                "league_name": {"$first": "$league"},
                "total_predictions": {"$sum": 1},
                "correct_predictions": {
                    "$sum": {"$cond": [{"$eq": ["$result", "correct"]}, 1, 0]}
                }
            }
        }
    ]
    
    prediction_stats = await db.predictions.aggregate(pipeline).to_list(None)
    
    # Create a map of (user_id, league_id) -> stats
    stats_map = {
        (stat["_id"]["user_id"], stat["_id"]["league_id"]): stat
        for stat in prediction_stats
    }
    
    # Group league points by user and league
    user_league_totals = {}
    for lp in league_points:
        user_id = lp['user_id']
        league_id = lp['league_id']
        league_name = normalize_league_name(lp['league_name'])  # Normalize here
        
        key = (user_id, league_id)
        if key not in user_league_totals:
            user_league_totals[key] = {
                'user_id': user_id,
                'username': lp['username'],
                'league_id': league_id,
                'league_name': league_name,
                'total_points': 0,
                'matchday_wins': 0
            }
        user_league_totals[key]['total_points'] += lp['points']
        user_league_totals[key]['matchday_wins'] += 1
    
    # Build leaderboard per league  
    # Group by normalized league name to merge variants
    leagues = {}
    
    # Track which users are in which league to avoid duplicates (moved outside loops)
    user_in_league = {}
    
    for key, data in user_league_totals.items():
        user_id, league_id = key
        league_name = data['league_name']  # Already normalized
        
        # Check if this user already exists in this league (from different league_id variant)
        league_user_key = (league_name, user_id)
        if league_user_key in user_in_league:
            # User already in this normalized league - merge points but DON'T duplicate prediction counts
            existing_idx = user_in_league[league_user_key]
            leagues[league_name][existing_idx]['total_points'] += data['total_points']
            leagues[league_name][existing_idx]['matchday_wins'] += data['matchday_wins']
            # Note: NOT adding correct/total predictions here - they should be the same fixtures
            continue
        
        # Get prediction stats for this user
        # Note: After deduplication, there should only be one entry per (user, league)
        stat = stats_map.get((user_id, league_id))
        
        if league_name not in leagues:
            leagues[league_name] = []
        
        entry_idx = len(leagues[league_name])
        user_in_league[league_user_key] = entry_idx
        
        leagues[league_name].append({
            'username': data['username'],
            'total_points': data['total_points'],
            'matchday_wins': data['matchday_wins'],
            'correct_predictions': stat['correct_predictions'] if stat else 0,
            'total_predictions': stat['total_predictions'] if stat else 0
        })
    
    # Also add users who have made predictions but haven't won any matchdays yet
    for stat in prediction_stats:
        user_id = stat["_id"]["user_id"]
        league_id = stat["_id"]["league_id"]
        league_name = normalize_league_name(stat.get("league_name", "Unknown League"))  # Normalize here
        username = stat.get("username", "Unknown Player")
        
        # Check if this user is already in the league leaderboard (by normalized name)
        league_user_key = (league_name, user_id)
        if league_user_key in user_in_league:
            # User already in leaderboard - DON'T add predictions (would duplicate counts)
            # The predictions are the same, just stored with different league name variants
            continue
        
        # Check if this user has points in ANY variant of this league
        key = (user_id, league_id)
        if key not in user_league_totals:
            # User has predictions but no matchday wins yet
            if league_name not in leagues:
                leagues[league_name] = []
            
            # Verify we have username before adding
            if username and username != "Unknown Player":
                entry_idx = len(leagues[league_name])
                user_in_league[league_user_key] = entry_idx
                
                leagues[league_name].append({
                    'username': username,
                    'total_points': 0,
                    'matchday_wins': 0,
                    'correct_predictions': stat['correct_predictions'],
                    'total_predictions': stat['total_predictions']
                })
    
    # Sort each league's leaderboard by total points
    result = []
    for league_name, members_data in leagues.items():
        members_data.sort(key=lambda x: (x['total_points'], x['correct_predictions']), reverse=True)
        
        # Assign ranks
        for idx, member in enumerate(members_data):
            member['rank'] = idx + 1
        
        result.append({
            'league_name': league_name,  # Already normalized
            'leaderboard': members_data
        })
    
    # Sort leagues alphabetically
    result.sort(key=lambda x: x['league_name'])
    
    logger.info(f"Returning {len(result)} leagues for team {team_id}")
    for league in result:
        logger.info(f"  {league['league_name']}: {len(league['leaderboard'])} members")
    
    return result

    """Get the team a user belongs to (legacy - returns first team)"""
    membership = await db.team_members.find_one({"user_id": user_id}, {"_id": 0})
    if not membership:
        return {"team": None, "message": "Not in any team"}
    
    team = await db.teams.find_one({"id": membership['team_id']}, {"_id": 0})
    return {"team": team, "membership": membership}


@api_router.get("/user/{user_id}/teams")
async def get_user_teams(user_id: str):
    """Get all teams a user belongs to"""
    memberships = await db.team_members.find({"user_id": user_id}, {"_id": 0}).to_list(100)
    
    if not memberships:
        return {"teams": [], "message": "Not in any team"}
    
    # Get all team details
    team_ids = [m['team_id'] for m in memberships]
    teams = await db.teams.find({"id": {"$in": team_ids}}, {"_id": 0}).to_list(100)
    
    # Combine team data with membership data
    result = []
    for membership in memberships:
        team = next((t for t in teams if t['id'] == membership['team_id']), None)
        if team:
            result.append({
                "team": team,
                "membership": membership
            })
    
    return {"teams": result}


# ========== TEAM FORUM ENDPOINTS ==========

@api_router.post("/teams/{team_id}/messages")
async def post_message(team_id: str, message_data: MessageCreate):
    """Post a message to team forum"""
    # Verify user is team member
    member = await db.team_members.find_one({
        "team_id": team_id,
        "user_id": message_data.user_id
    })
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this team")
    
    # Create message
    message = TeamMessage(**message_data.model_dump())
    doc = message.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.team_messages.insert_one(doc)
    return message


@api_router.get("/teams/{team_id}/messages")
async def get_team_messages(team_id: str, limit: int = 50):
    """Get messages from team forum"""
    messages = await db.team_messages.find(
        {"team_id": team_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Reverse to show oldest first
    messages.reverse()
    
    for msg in messages:
        if isinstance(msg.get('created_at'), str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return messages


@api_router.post("/teams/{team_id}/messages/{message_id}/like")
async def like_message(team_id: str, message_id: str, user_id: str):
    """Like a team message"""
    await db.team_messages.update_one(
        {"id": message_id, "team_id": team_id},
        {"$inc": {"likes": 1}}
    )
    return {"message": "Liked"}


@api_router.get("/teams")
async def list_all_teams():
    """List all public teams (for discovery)"""
    teams = await db.teams.find({"is_private": False}, {"_id": 0}).to_list(100)
    
    for team in teams:
        if isinstance(team.get('created_at'), str):
            team['created_at'] = datetime.fromisoformat(team['created_at'])
    
    return teams


# ========== TEAM NOMINATIONS (Community Support) ==========

@api_router.post("/teams/{team_id}/nominations", response_model=TeamNomination)
async def create_nomination(team_id: str, nomination: NominationCreate):
    """
    Create a nomination for a team member in need
    Any team member can nominate someone with a reason
    """
    try:
        # Verify both nominator and nominee are in the team
        nominator = await db.team_members.find_one({
            "team_id": team_id,
            "user_id": nomination.nominated_by_user_id
        }, {"_id": 0})
        
        nominee = await db.team_members.find_one({
            "team_id": team_id,
            "user_id": nomination.nominee_user_id
        }, {"_id": 0})
        
        if not nominator or not nominee:
            raise HTTPException(status_code=400, detail="Both users must be team members")
        
        # Create nomination
        nomination_doc = TeamNomination(**nomination.dict())
        await db.team_nominations.insert_one(nomination_doc.dict())
        
        logger.info(f"✨ New nomination in team {team_id}: {nomination.nominee_username} nominated by {nomination.nominated_by_username}")
        
        return nomination_doc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating nomination: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/teams/{team_id}/nominations")
async def get_team_nominations(team_id: str, status: str = "active"):
    """
    Get active nominations for a team
    Returns active nominations that winners can choose to support
    """
    try:
        query = {"team_id": team_id}
        if status:
            query["status"] = status
            
        nominations = await db.team_nominations.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
        
        return nominations
    except Exception as e:
        logger.error(f"Error fetching nominations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/teams/{team_id}/nominations/{nomination_id}/cancel")
async def cancel_nomination(team_id: str, nomination_id: str, user_id: str):
    """
    Cancel a nomination (only by nominator or team admin)
    """
    try:
        nomination = await db.team_nominations.find_one({"id": nomination_id, "team_id": team_id}, {"_id": 0})
        
        if not nomination:
            raise HTTPException(status_code=404, detail="Nomination not found")
        
        # Check if user is nominator or team admin
        team = await db.teams.find_one({"id": team_id}, {"_id": 0})
        is_admin = team and team.get('admin_user_id') == user_id
        is_nominator = nomination.get('nominated_by_user_id') == user_id
        
        if not (is_admin or is_nominator):
            raise HTTPException(status_code=403, detail="Only nominator or admin can cancel")
        
        # Update status
        await db.team_nominations.update_one(
            {"id": nomination_id},
            {"$set": {"status": "cancelled"}}
        )
        
        return {"message": "Nomination cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling nomination: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/teams/{team_id}/donations", response_model=WinnerDonation)
async def record_winner_donation(team_id: str, donation: WinnerDonation):
    """
    Record when a winner donates to a nominated team member
    """
    try:
        # Verify winner is in team
        winner = await db.team_members.find_one({
            "team_id": team_id,
            "user_id": donation.winner_user_id
        }, {"_id": 0})
        
        if not winner:
            raise HTTPException(status_code=400, detail="Winner must be a team member")
        
        # Save donation record
        donation_doc = donation.dict()
        await db.winner_donations.insert_one(donation_doc)
        
        # Mark nomination as fulfilled if specified
        if donation.recipient_user_id:
            await db.team_nominations.update_many(
                {
                    "team_id": team_id,
                    "nominee_user_id": donation.recipient_user_id,
                    "status": "active"
                },
                {"$set": {"status": "fulfilled"}}
            )
        
        logger.info(f"❤️ Winner {donation.winner_username} donated £{donation.amount} to {donation.recipient_username} in team {team_id}")
        
        return donation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording donation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/teams/{team_id}/donations")
async def get_team_donations(team_id: str):
    """
    Get donation history for a team
    Shows community support acts
    """
    try:
        donations = await db.winner_donations.find(
            {"team_id": team_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        return donations
    except Exception as e:
        logger.error(f"Error fetching donations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



# ============================================
# USER SEARCH & TEAM INVITATION ENDPOINTS
# ============================================



# ============================================
# FILE UPLOAD ENDPOINT
# ============================================

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a photo or video file
    Supports: images (jpg, jpeg, png, gif, webp) and videos (mp4, mov, avi)
    Max size: 50MB
    """
    try:
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.mov', '.avi', '.heic'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not allowed. Supported: images (jpg, png, gif, webp) and videos (mp4, mov, avi)"
            )
        
        # Check file size (50MB limit)
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > 50:
            raise HTTPException(status_code=400, detail=f"File too large ({file_size_mb:.1f}MB). Maximum size is 50MB")
        
        # Generate unique filename
        import uuid
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return URL (must be /api/uploads for Kubernetes ingress routing)
        file_url = f"/api/uploads/{unique_filename}"
        
        logger.info(f"File uploaded successfully: {unique_filename} ({file_size_mb:.2f}MB)")
        
        return {
            "url": file_url,
            "filename": unique_filename,
            "size_mb": round(file_size_mb, 2),
            "type": "image" if file_ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic'} else "video"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/users/search")
async def search_users(q: str):
    """
    Search for users by username (case-insensitive)
    Returns username and id only (no email for privacy)
    """
    if not q or len(q) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    try:
        # Case-insensitive search using regex
        users = await db.users.find(
            {"username": {"$regex": q, "$options": "i"}},
            {"_id": 0, "id": 1, "username": 1}
        ).limit(20).to_list(20)
        
        return users
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/teams/{team_id}/invite-user", response_model=TeamInvitation)
async def invite_user_to_team(team_id: str, inviter_user_id: str, invited_user_id: str):
    """
    Send a team invitation to a user
    Only team admin or members can invite
    """
    try:
        # Verify team exists
        team = await db.teams.find_one({"id": team_id}, {"_id": 0})
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Verify inviter is a team member
        inviter_membership = await db.team_members.find_one({
            "team_id": team_id,
            "user_id": inviter_user_id
        }, {"_id": 0})
        
        if not inviter_membership:
            raise HTTPException(status_code=403, detail="Only team members can send invitations")
        
        # Get invited user details
        invited_user = await db.users.find_one({"id": invited_user_id}, {"_id": 0})
        if not invited_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user is already a member
        existing_member = await db.team_members.find_one({
            "team_id": team_id,
            "user_id": invited_user_id
        })
        if existing_member:
            raise HTTPException(status_code=400, detail="User is already a team member")
        
        # Check for existing pending invitation
        existing_invitation = await db.team_invitations.find_one({
            "team_id": team_id,
            "invited_user_id": invited_user_id,
            "status": "pending"
        })
        if existing_invitation:
            raise HTTPException(status_code=400, detail="User already has a pending invitation")
        
        # Create invitation
        invitation = TeamInvitation(
            team_id=team_id,
            team_name=team["name"],
            inviter_user_id=inviter_user_id,
            inviter_username=inviter_membership["username"],
            invited_user_id=invited_user_id,
            invited_username=invited_user["username"]
        )
        
        await db.team_invitations.insert_one(invitation.model_dump())
        
        logger.info(f"User {inviter_user_id} invited {invited_user_id} to team {team_id}")
        return invitation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/users/{user_id}/invitations")
async def get_user_invitations(user_id: str):
    """
    Get all pending team invitations for a user
    """
    try:
        invitations = await db.team_invitations.find(
            {
                "invited_user_id": user_id,
                "status": "pending"
            },
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        
        return invitations
    except Exception as e:
        logger.error(f"Error fetching invitations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/teams/{team_id}/sent-invitations")
async def get_team_sent_invitations(team_id: str):
    """
    Get all invitations sent by a team (for invitation tracking)
    Shows pending, accepted, and declined invitations
    """
    try:
        invitations = await db.team_invitations.find(
            {"team_id": team_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        
        return invitations
    except Exception as e:
        logger.error(f"Error fetching sent invitations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/force-results-update")
async def force_results_update():
    """Force update results from API"""
    try:
        await automated_result_update()
        return {"status": "success", "message": "Results updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@api_router.get("/admin/wipe-predictions")
async def wipe_all_predictions(confirm_code: str):
    """
    ADMIN ENDPOINT: Wipe all predictions and reset points
    Requires confirmation code to prevent accidental wipes
    
    Usage: POST /api/admin/wipe-predictions?confirm_code=WIPE2024
    """
    # Safety check - require confirmation code
    if confirm_code != "WIPE2024":
        raise HTTPException(status_code=403, detail="Invalid confirmation code")
    
    try:
        # Count before deletion
        predictions_count = await db.predictions.count_documents({})
        league_points_count = await db.user_league_points.count_documents({})
        
        # Delete all predictions
        result1 = await db.predictions.delete_many({})
        
        # Delete all league points
        result2 = await db.user_league_points.delete_many({})
        
        # Reset user points to zero
        result3 = await db.users.update_many(
            {},
            {
                "$set": {
                    "total_points": 0,
                    "season_points": 0,
                    "points": 0,
                    "correct_predictions": 0,
                    "total_predictions": 0,
                    "weekly_wins": 0
                }
            }
        )
        
        logger.info(f"🧹 WIPE COMPLETE: Deleted {result1.deleted_count} predictions, {result2.deleted_count} league points, reset {result3.modified_count} users")
        
        return {
            "status": "success",
            "message": "All predictions and points wiped successfully",
            "details": {
                "predictions_deleted": result1.deleted_count,
                "league_points_deleted": result2.deleted_count,
                "users_reset": result3.modified_count,
                "users_preserved": await db.users.count_documents({}),
                "teams_preserved": await db.teams.count_documents({})
            }
        }
        
    except Exception as e:
        logger.error(f"Error wiping predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


        logger.error(f"Error fetching sent invitations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@api_router.post("/teams/invitations/{invitation_id}/accept")
async def accept_team_invitation(invitation_id: str, user_id: str):
    """
    Accept a team invitation and join the team
    """
    try:
        # Get invitation
        invitation = await db.team_invitations.find_one(
            {"id": invitation_id, "invited_user_id": user_id, "status": "pending"},
            {"_id": 0}
        )
        
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found or already responded")
        
        # Check if already a member
        existing_member = await db.team_members.find_one({
            "team_id": invitation["team_id"],
            "user_id": user_id
        })
        if existing_member:
            # Update invitation status
            await db.team_invitations.update_one(
                {"id": invitation_id},
                {"$set": {"status": "accepted", "responded_at": datetime.now(timezone.utc)}}
            )
            raise HTTPException(status_code=400, detail="Already a member of this team")
        
        # Add user to team
        member = TeamMember(
            team_id=invitation["team_id"],
            user_id=user_id,
            username=invitation["invited_username"],
            role="member"
        )
        await db.team_members.insert_one(member.model_dump())
        
        # Update team member count
        await db.teams.update_one(
            {"id": invitation["team_id"]},
            {"$inc": {"member_count": 1}}
        )
        
        # Update invitation status
        await db.team_invitations.update_one(
            {"id": invitation_id},
            {"$set": {"status": "accepted", "responded_at": datetime.now(timezone.utc)}}
        )
        
        logger.info(f"User {user_id} accepted invitation {invitation_id}")
        return {"message": f"Successfully joined {invitation['team_name']}!", "team": invitation["team_id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/teams/invitations/{invitation_id}/decline")
async def decline_team_invitation(invitation_id: str, user_id: str):
    """
    Decline a team invitation
    """
    try:
        # Get invitation
        invitation = await db.team_invitations.find_one(
            {"id": invitation_id, "invited_user_id": user_id, "status": "pending"},
            {"_id": 0}
        )
        
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found or already responded")
        
        # Update invitation status
        await db.team_invitations.update_one(
            {"id": invitation_id},
            {"$set": {"status": "declined", "responded_at": datetime.now(timezone.utc)}}
        )
        
        logger.info(f"User {user_id} declined invitation {invitation_id}")
        return {"message": "Invitation declined"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error declining invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@api_router.get("/team/members")
async def get_team_members():
    """Get all team members"""
    members = await db.users.find({}, {"_id": 0}).to_list(100)
    return members


@api_router.get("/team/can-join")
async def can_join_team():
    """Check if team is accepting new members"""
    settings = await db.team_settings.find_one({}, {"_id": 0})
    if not settings:
        return {"can_join": True, "reason": None}
    
    member_count = await db.users.count_documents({})
    max_members = settings.get('max_members', 30)
    
    if member_count >= max_members:
        return {
            "can_join": False,
            "reason": f"Team is full ({max_members} members max)"
        }
    
    return {"can_join": True, "reason": None}


# ========== NOTIFICATION ENDPOINTS ==========

@api_router.get("/notifications/{user_id}")
async def get_user_notifications(user_id: str, unread_only: bool = False):
    """Get notifications for a user"""
    query = {"user_id": user_id}
    if unread_only:
        query["read"] = False
    
    notifications = await db.notifications.find(query, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return notifications


@api_router.post("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@api_router.post("/notifications/{user_id}/read-all")
async def mark_all_notifications_read(user_id: str):
    """Mark all notifications as read for a user"""
    await db.notifications.update_many(
        {"user_id": user_id, "read": False},
        {"$set": {"read": True, "read_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "All notifications marked as read"}


@api_router.get("/notifications/{user_id}/unread-count")
async def get_unread_count(user_id: str):
    """Get count of unread notifications"""
    count = await db.notifications.count_documents({"user_id": user_id, "read": False})
    return {"count": count}


async def create_notification(user_id: str, notification_type: str, title: str, message: str, data: dict = None):
    """Helper function to create a notification"""
    from uuid import uuid4
    notification = {
        "id": str(uuid4()),
        "user_id": user_id,
        "type": notification_type,  # 'winner', 'loser', 'tie', 'weekly_summary'
        "title": title,
        "message": message,
        "data": data or {},
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.notifications.insert_one(notification)
    return notification


# ========== STRIPE PAYMENT ENDPOINTS ==========

@api_router.post("/stripe/create-checkout")
async def create_stripe_checkout(
    request: Request,
    user_email: str,
    user_name: str,
    stake_amount: float,
    origin_url: str
):
    """
    Create a Stripe checkout session for weekly pot contribution
    
    Args:
        user_email: User's email
        user_name: User's display name
        stake_amount: Total amount including Stripe fees (2.27, 3.30, 5.36 or 0.0)
        origin_url: Frontend origin URL for redirect URLs
    """
    try:
        # Validate stake amount (with 50/50 Stripe fees split)
        valid_stakes = [2.13, 3.15, 5.18, 0.0]  # 0.0 for "play for fun"
        
        # Allow small floating point differences
        if stake_amount not in valid_stakes and not any(abs(stake_amount - valid) < 0.01 for valid in valid_stakes):
            raise HTTPException(status_code=400, detail="Invalid stake amount")
        
        # If play for fun (0.0), no payment needed
        if stake_amount == 0.0:
            return {
                "status": "success",
                "message": "Playing for fun - no payment required",
                "play_for_fun": True
            }
        
        # Map charge amount to actual stake for pot calculation
        stake_mapping = {
            2.13: 2.0,
            3.15: 3.0,
            5.18: 5.0
        }
        
        # Find the closest match for actual stake
        actual_stake = stake_mapping.get(stake_amount)
        if not actual_stake:
            # Find closest match
            for charge, stake in stake_mapping.items():
                if abs(stake_amount - charge) < 0.01:
                    actual_stake = stake
                    break
        
        if not actual_stake:
            raise HTTPException(status_code=400, detail="Invalid stake amount")
        
        # Get current week
        cycle = await get_or_create_weekly_cycle()
        week_id = cycle["week_id"]
        
        # Check if user already paid for this week
        existing_payment = await db.payment_transactions.find_one({
            "user_email": user_email,
            "week_id": week_id,
            "payment_status": "paid"
        })
        
        if existing_payment:
            return {
                "status": "already_paid",
                "message": "You've already paid for this week's pot"
            }
        
        # Initialize Stripe service
        stripe_service = get_stripe_service(request)
        
        # Create success and cancel URLs
        success_url = f"{origin_url}/?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
        cancel_url = f"{origin_url}/?payment=cancel"
        
        # Create checkout session with the full charge amount
        session = await stripe_service.create_pot_payment_session(
            amount=stake_amount,  # Charge full amount (includes Stripe fees)
            user_email=user_email,
            user_name=user_name,
            week_id=week_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        # Create pending payment record with actual stake for pot calculation
        payment_record = {
            "session_id": session.session_id,
            "user_email": user_email,
            "user_name": user_name,
            "week_id": week_id,
            "amount": stake_amount,  # What user was charged
            "actual_stake": actual_stake,  # What goes into pot calculation
            "currency": "gbp",
            "payment_status": "pending",
            "status": "initiated",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payment_transactions.insert_one(payment_record)
        
        return {
            "url": session.url,
            "session_id": session.session_id
        }
        
    except Exception as e:
        logger.error(f"Failed to create Stripe checkout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/stripe/checkout-status/{session_id}")
async def get_checkout_status(session_id: str, request: Request):
    """
    Get the status of a Stripe checkout session and update records
    
    Args:
        session_id: Stripe checkout session ID
    """
    try:
        # Get payment record
        payment = await db.payment_transactions.find_one({"session_id": session_id})
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # If already processed as paid, return the status
        if payment.get("payment_status") == "paid":
            return {
                "status": "complete",
                "payment_status": "paid",
                "amount": payment.get("amount"),
                "currency": payment.get("currency")
            }
        
        # Initialize Stripe service
        stripe_service = get_stripe_service(request)
        
        # Get status from Stripe
        checkout_status = await stripe_service.get_payment_status(session_id)
        
        # Update payment record
        update_data = {
            "payment_status": checkout_status.payment_status,
            "status": checkout_status.status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        # If payment is successful, update the weekly pot
        if checkout_status.payment_status == "paid" and payment.get("payment_status") != "paid":
            week_id = payment.get("week_id")
            actual_stake = payment.get("actual_stake", payment.get("amount", 0))  # Use actual_stake for pot
            
            # Calculate admin fee (10%) on the actual stake
            admin_fee = actual_stake * 0.10
            distributable = actual_stake - admin_fee
            
            # Update weekly cycle
            await db.weekly_cycles.update_one(
                {"week_id": week_id},
                {
                    "$inc": {
                        "total_pot": actual_stake,
                        "admin_fee": admin_fee,
                        "distributable_pot": distributable
                    }
                }
            )
            
            logger.info(f"Updated pot for week {week_id}: +£{actual_stake}")
        
        return {
            "status": checkout_status.status,
            "payment_status": checkout_status.payment_status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency
        }
        
    except Exception as e:
        logger.error(f"Failed to get checkout status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    """
    try:
        # Get raw body and signature
        body = await request.body()
        signature = request.headers.get("Stripe-Signature", "")
        
        # Initialize Stripe service
        stripe_service = get_stripe_service(request)
        
        # Handle webhook
        webhook_data = await stripe_service.handle_webhook(body, signature)
        
        logger.info(f"Processed Stripe webhook: {webhook_data}")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))




# ========== PROMO CODE ENDPOINTS ==========

@api_router.post("/admin/update-promo-code")
async def update_promo_code(code: str, discount_value: float, description: str = None):
    """
    Admin endpoint to update an existing promo code's discount value and description
    """
    try:
        code_upper = code.upper()
        
        # Check if code exists
        existing = await db.promo_codes.find_one({"code": code_upper})
        if not existing:
            raise HTTPException(status_code=404, detail=f"Promo code {code_upper} not found")
        
        # Update fields
        update_data = {"discount_value": discount_value}
        if description:
            update_data["description"] = description
        
        result = await db.promo_codes.update_one(
            {"code": code_upper},
            {"$set": update_data}
        )
        
        logger.info(f"Updated promo code {code_upper}: discount_value={discount_value}")
        
        return {
            "status": "success",
            "message": f"Promo code {code_upper} updated successfully",
            "updated_fields": update_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating promo code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/calculate-weekly-winners")
async def trigger_weekly_winners_admin():
    """
    Admin endpoint to manually calculate and award weekly winner points
    Call this at the end of each week after all matches are finished
    Normally runs automatically via scheduler (Wed 2PM + Daily 6PM)
    """
    try:
        await calculate_weekly_winners()
        return {
            "status": "success",
            "message": "Weekly winners calculated and points awarded"
        }
    except Exception as e:
        logger.error(f"Error calculating weekly winners: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/reset-season")
async def reset_season():
    """
    ADMIN ONLY: Reset all user stats and predictions for fresh start
    - Clears all predictions
    - Resets all user points to 0
    - Clears weekly pots
    - DANGEROUS: Cannot be undone
    """
    try:
        logger.info("🔄 Starting season reset...")
        
        # Delete all predictions
        predictions_deleted = await db.predictions.delete_many({})
        logger.info(f"   Deleted {predictions_deleted.deleted_count} predictions")
        
        # Reset all user stats to 0
        users_updated = await db.users.update_many(
            {},
            {"$set": {
                "season_points": 0,
                "weekly_points": 0,
                "weekly_wins": 0
            }}
        )
        logger.info(f"   Reset stats for {users_updated.modified_count} users")
        
        # Delete all weekly pots
        pots_deleted = await db.weekly_pots.delete_many({})
        logger.info(f"   Deleted {pots_deleted.deleted_count} weekly pots")
        
        # Create fresh weekly pot for each team in "fun" mode
        teams = await db.teams.find({}, {"_id": 0}).to_list(100)
        pots_created = 0
        for team in teams:
            new_pot = {
                "id": str(uuid.uuid4()),
                "team_id": team['id'],
                "team_name": team['name'],
                "total_pot": 0,
                "rollover": 0,
                "paid_entries": 0,
                "status": "active",
                "week_start": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.weekly_pots.insert_one(new_pot)
            pots_created += 1
        
        logger.info(f"   Created {pots_created} fresh weekly pots")
        logger.info("✅ Season reset complete!")
        
        return {
            "status": "success",
            "message": "Season reset complete - fresh start!",
            "predictions_deleted": predictions_deleted.deleted_count,
            "users_reset": users_updated.modified_count,
            "pots_deleted": pots_deleted.deleted_count,
            "pots_created": pots_created
        }
        
    except Exception as e:
        logger.error(f"❌ Error resetting season: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/promo-codes/create")
async def create_promo_code(promo_data: PromoCodeCreate):
    """
    Create a new promo code
    """
    try:
        # Check if code already exists
        existing = await db.promo_codes.find_one({"code": promo_data.code.upper()})
        if existing:
            raise HTTPException(status_code=400, detail="Promo code already exists")
        
        # Create promo code
        promo_code = PromoCode(
            code=promo_data.code.upper(),
            description=promo_data.description,
            discount_type=promo_data.discount_type,
            discount_value=promo_data.discount_value,
            stake_amount=promo_data.stake_amount,
            max_uses=promo_data.max_uses,
            max_uses_per_user=promo_data.max_uses_per_user,
            valid_from=promo_data.valid_from or datetime.now(timezone.utc),
            valid_until=promo_data.valid_until,
            requires_review=promo_data.requires_review,
            current_uses=0,
            is_active=True
        )
        
        await db.promo_codes.insert_one(promo_code.model_dump())
        
        logger.info(f"Created promo code: {promo_code.code}")
        
        return {
            "status": "success",
            "message": "Promo code created successfully",
            "promo_code": promo_code.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating promo code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/promo-codes/validate")
async def validate_promo_code(validation: PromoCodeValidation):
    """
    Validate a promo code for a user
    """
    try:
        # Find promo code
        promo_code = await db.promo_codes.find_one({"code": validation.code.upper()})
        
        if not promo_code:
            return {
                "valid": False,
                "message": "Promo code not found"
            }
        
        # Check if active
        if not promo_code.get("is_active", True):
            return {
                "valid": False,
                "message": "Promo code is no longer active"
            }
        
        # Check date validity
        now = datetime.now(timezone.utc)
        valid_from = promo_code.get("valid_from")
        valid_until = promo_code.get("valid_until")
        
        if valid_from and isinstance(valid_from, str):
            valid_from = datetime.fromisoformat(valid_from.replace('Z', '+00:00'))
        if valid_until and isinstance(valid_until, str):
            valid_until = datetime.fromisoformat(valid_until.replace('Z', '+00:00'))
        
        if valid_from and now < valid_from:
            return {
                "valid": False,
                "message": "Promo code is not yet valid"
            }
        
        if valid_until and now > valid_until:
            return {
                "valid": False,
                "message": "Promo code has expired"
            }
        
        # Check total uses
        max_uses = promo_code.get("max_uses")
        current_uses = promo_code.get("current_uses", 0)
        
        if max_uses and current_uses >= max_uses:
            return {
                "valid": False,
                "message": "Promo code has reached maximum uses"
            }
        
        # Check user-specific uses
        max_uses_per_user = promo_code.get("max_uses_per_user", 1)
        user_uses = await db.promo_code_usage.count_documents({
            "promo_code": validation.code.upper(),
            "user_email": validation.user_email
        })
        
        if user_uses >= max_uses_per_user:
            return {
                "valid": False,
                "message": f"You have already used this promo code {max_uses_per_user} time(s)"
            }
        
        # Valid!
        return {
            "valid": True,
            "message": "Promo code is valid",
            "discount_value": promo_code.get("discount_value", 0),
            "discount_type": promo_code.get("discount_type", "fixed"),
            "stake_amount": promo_code.get("stake_amount", 3.0),
            "description": promo_code.get("description", "")
        }
        
    except Exception as e:
        logger.error(f"Error validating promo code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/promo-codes/apply")
async def apply_promo_code(
    promo_code: str,
    user_email: str,
    team_id: Optional[str] = None,
    referred_by: Optional[str] = None
):
    """
    Apply a promo code and record its usage
    """
    try:
        # Validate promo code first
        validation = PromoCodeValidation(
            code=promo_code,
            user_email=user_email,
            team_id=team_id
        )
        
        valid_result = await validate_promo_code(validation)
        
        if not valid_result.get("valid"):
            raise HTTPException(status_code=400, detail=valid_result.get("message", "Invalid promo code"))
        
        # Get promo code details
        promo = await db.promo_codes.find_one({"code": promo_code.upper()})
        
        if not promo:
            raise HTTPException(status_code=404, detail="Promo code not found")
        
        # Get team name if team_id provided
        team_name = None
        if team_id:
            team = await db.teams.find_one({"id": team_id})
            team_name = team.get("name") if team else None
        
        # Calculate discount
        stake_amount = promo.get("stake_amount", 3.0)
        discount_value = promo.get("discount_value", 0)
        discount_type = promo.get("discount_type", "fixed")
        
        if discount_type == "fixed":
            final_amount = max(0, stake_amount - discount_value)
            discount_applied = discount_value
        else:  # percentage
            discount_applied = stake_amount * (discount_value / 100)
            final_amount = stake_amount - discount_applied
        
        # Record usage
        usage = PromoCodeUsage(
            promo_code_id=promo.get("id"),
            promo_code=promo_code.upper(),
            user_id="",  # Will be filled by frontend
            user_email=user_email,
            team_id=team_id,
            team_name=team_name,
            payment_amount=final_amount,
            discount_applied=discount_applied,
            referred_by=referred_by
        )
        
        await db.promo_code_usage.insert_one(usage.model_dump())
        
        # Update promo code usage count
        await db.promo_codes.update_one(
            {"code": promo_code.upper()},
            {"$inc": {"current_uses": 1}}
        )
        
        logger.info(f"Applied promo code {promo_code} for user {user_email}")
        
        return {
            "status": "success",
            "message": "Promo code applied successfully",
            "original_amount": stake_amount,
            "discount_applied": discount_applied,
            "final_amount": final_amount,
            "stake_amount": stake_amount
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying promo code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/promo-codes/stats/{code}")
async def get_promo_code_stats(code: str):
    """
    Get usage statistics for a promo code
    """
    try:
        promo = await db.promo_codes.find_one({"code": code.upper()})
        
        if not promo:
            raise HTTPException(status_code=404, detail="Promo code not found")
        
        # Get usage records
        usages = await db.promo_code_usage.find({"promo_code": code.upper()}).to_list(1000)
        
        # Calculate stats
        total_uses = len(usages)
        unique_users = len(set(u.get("user_email") for u in usages))
        unique_teams = len(set(u.get("team_id") for u in usages if u.get("team_id")))
        total_discount = sum(u.get("discount_applied", 0) for u in usages)
        total_revenue = sum(u.get("payment_amount", 0) for u in usages)
        
        # Referral stats
        referred_users = len([u for u in usages if u.get("referred_by")])
        
        return {
            "code": code.upper(),
            "description": promo.get("description", ""),
            "is_active": promo.get("is_active", True),
            "total_uses": total_uses,
            "max_uses": promo.get("max_uses"),
            "unique_users": unique_users,
            "unique_teams": unique_teams,
            "total_discount_given": round(total_discount, 2),
            "total_revenue_generated": round(total_revenue, 2),
            "referred_users": referred_users,
            "valid_from": promo.get("valid_from"),
            "valid_until": promo.get("valid_until")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting promo code stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/promo-codes/list")
async def list_promo_codes():
    """
    List all active promo codes (admin endpoint)
    """
    try:
        promo_codes = await db.promo_codes.find({"is_active": True}).to_list(100)
        
        return {
            "status": "success",
            "promo_codes": promo_codes,
            "count": len(promo_codes)
        }
        
    except Exception as e:
        logger.error(f"Error listing promo codes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== EMAIL INVITATION ENDPOINTS ==========

@api_router.post("/teams/{team_id}/invite")
async def send_team_invitation(
    team_id: str,
    recipient_email: str,
    inviter_name: str,
    request: Request
):
    """
    Send an email invitation to join a team
    
    Args:
        team_id: ID of the team
        recipient_email: Email address to send invitation to
        inviter_name: Name of person sending invite
    """
    try:
        # Get team details
        team = await db.teams.find_one({"id": team_id})
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get app URL from request
        app_url = str(request.base_url).rstrip('/')
        
        # Send invitation email
        result = await email_service.send_team_invitation(
            recipient_email=recipient_email,
            team_name=team.get("name", "Unknown Team"),
            team_code=team.get("join_code", ""),
            inviter_name=inviter_name,
            app_url=app_url
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        # Log the invitation
        invitation_record = {
            "team_id": team_id,
            "recipient_email": recipient_email,
            "inviter_name": inviter_name,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent"
        }
        
        await db.team_invitations.insert_one(invitation_record)
        
        return {
            "status": "success",
            "message": f"Invitation sent to {recipient_email}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send team invitation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/teams/{team_id}/invitations")
async def get_team_invitations(team_id: str):
    """
    Get all invitations sent for a team
    
    Args:
        team_id: ID of the team
    """
    try:
        invitations = await db.team_invitations.find(
            {"team_id": team_id},
            {"_id": 0}
        ).sort("sent_at", -1).to_list(100)
        
        return invitations
        
    except Exception as e:
        logger.error(f"Failed to get team invitations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include main API router
app.include_router(api_router)

# Include new modular routes for social features
posts_router.set_db(db)
auth_router.set_db(db)
app.include_router(posts_router.router, prefix="/api", tags=["posts"])
app.include_router(auth_router.router, prefix="/api", tags=["auth"])

# ========== AUTOMATED RESULT CHECKER ==========

scheduler = AsyncIOScheduler()


async def live_match_update():
    """
    Check for LIVE/IN-PLAY matches and update scores in real-time
    Runs every 2 minutes during match days
    Does NOT score predictions - only updates current scores for display
    """
    try:
        logger.info("🔴 Checking for live matches...")
        
        # All leagues
        league_ids = [39, 40, 179, 140, 78, 135, 61, 94, 88, 203, 253, 71, 239]
        
        service = get_active_football_service()
        
        from datetime import datetime, timezone
        
        # Only check TODAY's matches for live updates
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        all_fixtures = []
        for league_id in league_ids:
            fixtures = await service.get_fixtures_by_date(today, league_id, season=2025)
            all_fixtures.extend(fixtures)
        
        if not all_fixtures:
            logger.info("No fixtures today")
            return
        
        # Transform to standard format
        transformed = service.transform_to_standard_format(all_fixtures)
        
        live_count = 0
        
        for fixture in transformed:
            status = fixture.get('status', 'SCHEDULED')
            
            # Update if match is LIVE, IN_PLAY, or any in-progress status
            if status in ['LIVE', 'IN_PLAY', '1H', '2H', 'HT', 'ET', 'BT', 'P']:
                # Update fixture with current score (don't score predictions yet)
                await db.fixtures.update_one(
                    {"fixture_id": fixture['fixture_id']},
                    {"$set": {
                        "home_score": fixture.get('home_score'),
                        "away_score": fixture.get('away_score'),
                        "status": status,
                        "home_team": fixture['home_team'],
                        "away_team": fixture['away_team'],
                        "league_name": fixture['league_name'],
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }},
                    upsert=True
                )
                live_count += 1
        
        if live_count > 0:
            logger.info(f"🔴 {live_count} live matches updated")
        else:
            logger.info("No live matches at the moment")
        
    except Exception as e:
        logger.error(f"❌ Error in live match update: {str(e)}")


async def automated_result_update():
    """
    Automatically check and update match results
    Runs periodically to score predictions
    """
    try:
        logger.info("🔄 Starting automated result update...")
        
        # ALL leagues including NEW ones: Premier League, La Liga, Bundesliga, Serie A, Ligue 1, 
        # Eredivisie, Primeira Liga, Championship, Scottish Premiership, Turkish Süper Lig, MLS, Brazilian Serie A, Colombian Liga
        # British Isles, European, then Rest of World
        league_ids = [39, 40, 179, 140, 78, 135, 61, 94, 88, 203, 253, 71, 239]
        
        updated_count = 0
        scored_predictions = 0
        
        # Fetch fixtures from current season (2025)
        service = get_active_football_service()
        
        from datetime import datetime, timedelta, timezone
        
        # Dynamically check last 7 days INCLUDING TODAY for finished matches
        all_fixtures = []
        today = datetime.now(timezone.utc)
        
        for i in range(8):  # Last 7 days PLUS today (0 to 7 days ago)
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime('%Y-%m-%d')
            logger.info(f"Checking fixtures for {date_str}...")
            for league_id in league_ids:
                fixtures = await service.get_fixtures_by_date(date_str, league_id, season=2025)
                all_fixtures.extend(fixtures)
        
        if not all_fixtures:
            logger.warning("No fixtures data available from API for 2025 season")
            return
        
        # Transform and process fixtures
        transformed = service.transform_to_standard_format(all_fixtures)
        
        logger.info(f"Found {len(transformed)} fixtures from API")
        
        for fixture in transformed:
            # Only process finished matches with scores
            if fixture['status'] == 'FINISHED' and fixture.get('home_score') is not None:
                # Update fixture in database (also update team names in case they were mock data)
                result = await db.fixtures.update_one(
                    {"fixture_id": fixture['fixture_id']},
                    {"$set": {
                        "home_score": fixture['home_score'],
                        "away_score": fixture['away_score'],
                        "status": fixture['status'],
                        "home_team": fixture['home_team'],
                        "away_team": fixture['away_team'],
                        "league_name": fixture['league_name']
                    }},
                    upsert=True  # Create if doesn't exist
                )
                
                if result.modified_count > 0 or result.upserted_id:
                    updated_count += 1
                
                # Determine actual result
                home_score = fixture['home_score']
                away_score = fixture['away_score']
                
                if home_score > away_score:
                    actual_result = 'home'
                elif away_score > home_score:
                    actual_result = 'away'
                else:
                    actual_result = 'draw'
                
                # Find all pending predictions for this fixture
                predictions = await db.predictions.find({
                    "fixture_id": fixture['fixture_id'],
                    "result": "pending"
                }).to_list(1000)
                
                # Score each prediction and update with match details
                for pred in predictions:
                    is_correct = pred['prediction'] == actual_result
                    
                    # Update prediction with result AND match details (team names, scores, status)
                    # NOTE: Points are NOT assigned here - they are calculated by matchday winners
                    await db.predictions.update_one(
                        {"id": pred['id']},
                        {"$set": {
                            "result": "correct" if is_correct else "incorrect",
                            "home_team": fixture['home_team'],
                            "away_team": fixture['away_team'],
                            "league": fixture['league_name'],
                            "home_score": home_score,
                            "away_score": away_score,
                            "status": fixture['status']
                        }}
                    )
                    scored_predictions += 1
        
        logger.info(f"✅ Automated update complete: {updated_count} fixtures updated, {scored_predictions} predictions scored")
        
        # After scoring predictions, calculate matchday winners and award points
        if scored_predictions > 0:
            await calculate_matchday_winners()
        
    except Exception as e:
        logger.error(f"❌ Error in automated result update: {str(e)}")




@api_router.get("/admin/force-update-results")
async def force_update_results():
    """
    Manually trigger the automated result checker
    Fetches scores from API-Football and updates database
    """
    try:
        logger.info("🔄 Manual result update triggered...")
        await automated_result_update()
        return {
            "status": "success",
            "message": "Result update completed. Check fixtures for updated scores."
        }
    except Exception as e:
        logger.error(f"Error in manual result update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



async def calculate_matchday_winners():
    """
    Calculate and award points based on matchday winners per league.
    
    SCORING RULE (Winner-Takes-All):
    - Group predictions by (league_id, matchday)
    - Within each group, count correct predictions per user
    - Award 3 points ONLY to user(s) with the most correct predictions
    - If multiple users tie for most correct, they each get 3 points
    
    This function should be called after automated_result_update() 
    to ensure all predictions are scored (marked correct/incorrect).
    """
    from uuid import uuid4
    try:
        logger.info("🏆 Calculating matchday winners per league...")
        
        # Get all fixtures with their matchday and league info
        fixtures = await db.fixtures.find(
            {"status": "FINISHED", "matchday": {"$exists": True, "$ne": None}},
            {"_id": 0, "fixture_id": 1, "league_id": 1, "matchday": 1, "league_name": 1}
        ).to_list(10000)
        
        if not fixtures:
            logger.info("No finished fixtures with matchday info found")
            return
        
        # Group fixtures by (league_id, matchday)
        league_matchday_groups = {}
        for fixture in fixtures:
            league_id = fixture.get('league_id')
            matchday = fixture.get('matchday', '').strip()
            
            if not league_id or not matchday:
                continue
            
            key = (league_id, matchday)
            if key not in league_matchday_groups:
                league_matchday_groups[key] = {
                    'league_id': league_id,
                    'league_name': fixture.get('league_name', 'Unknown'),
                    'matchday': matchday,
                    'fixture_ids': []
                }
            league_matchday_groups[key]['fixture_ids'].append(fixture['fixture_id'])
        
        logger.info(f"Found {len(league_matchday_groups)} unique (league, matchday) combinations")
        
        # For each group, find winners and award points
        total_winners = 0
        for (league_id, matchday), group_data in league_matchday_groups.items():
            fixture_ids = group_data['fixture_ids']
            league_name = group_data['league_name']
            
            # Get all correct predictions for these fixtures
            correct_predictions = await db.predictions.find({
                "fixture_id": {"$in": fixture_ids},
                "result": "correct"
            }, {"_id": 0, "user_id": 1, "username": 1}).to_list(10000)
            
            if not correct_predictions:
                logger.info(f"  {league_name} - {matchday}: No correct predictions")
                continue
            
            # Count correct predictions per user
            user_correct_counts = {}
            for pred in correct_predictions:
                user_id = pred['user_id']
                if user_id not in user_correct_counts:
                    user_correct_counts[user_id] = {
                        'count': 0,
                        'username': pred.get('username', 'Unknown')
                    }
                user_correct_counts[user_id]['count'] += 1
            
            # Find the maximum correct count
            max_correct = max(user_correct_counts.values(), key=lambda x: x['count'])['count']
            
            # Find all users with max correct predictions (winners)
            winners = [uid for uid, data in user_correct_counts.items() if data['count'] == max_correct]
            
            # Award 3 points to each winner
            for winner_id in winners:
                # Update user's total season points
                await db.users.update_one(
                    {"id": winner_id},
                    {"$inc": {"season_points": 3}}
                )
                
                # Track league-specific points for leaderboard
                # Check if this user already won this matchday in this league (prevent duplicates)
                existing = await db.user_league_points.find_one({
                    "user_id": winner_id,
                    "league_id": league_id,
                    "matchday": matchday
                })
                
                if not existing:
                    await db.user_league_points.insert_one({
                        "id": str(uuid4()),
                        "user_id": winner_id,
                        "username": user_correct_counts[winner_id]['username'],
                        "league_id": league_id,
                        "league_name": league_name,
                        "matchday": matchday,
                        "points": 3,
                        "correct_count": max_correct,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
                
                username = user_correct_counts[winner_id]['username']
                logger.info(f"  ✅ {league_name} - {matchday}: {username} wins with {max_correct} correct → +3 points")
                total_winners += 1
        
        logger.info(f"🎉 Matchday winners calculation complete: {total_winners} winners awarded 3 points each")
        
    except Exception as e:
        logger.error(f"❌ Error calculating matchday winners: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


async def calculate_weekly_winners():
    """
    Calculate weekly winners for each team
    
    WEEKLY CYCLE:
    - Friday-Monday: Fixtures are played (weekend + Monday night football)
    - Wednesday: Calculate winners and send notifications (run this function)
    - Thursday: New week begins
    
    SCORING:
    - 3 points: Sole winner (most correct predictions)
    - 1 point each: Multiple winners tied for most correct
    - 0 points: Everyone else
    
    POT RULES:
    - Sole winner: Gets pot minus 10% admin fee (admin pays manually)
    - Tie: No payment, pot rolls over to next week
    - No correct predictions: Pot rolls over to next week
    
    Sends email notifications and handles pot rollover automatically
    """
    try:
        logger.info("🏆 Calculating weekly winners for all teams...")
        
        # Get all teams
        teams = await db.teams.find({}, {"_id": 0}).to_list(1000)
        
        for team in teams:
            team_id = team.get('id')
            team_name = team.get('name', 'Unknown')
            
            # Get all team members
            members = await db.team_members.find({"team_id": team_id}, {"_id": 0}).to_list(100)
            member_ids = [m['user_id'] for m in members]
            
            if not member_ids:
                continue
            
            # Get current week's pot info (or initialize)
            pot_info = await db.weekly_pots.find_one({"team_id": team_id, "status": "active"})
            
            if not pot_info:
                logger.info(f"  Team '{team_name}': No active weekly pot")
                continue
            
            current_pot = pot_info.get('total_pot', 0)
            paid_entries = pot_info.get('paid_entries', 0)
            rollover_amount = pot_info.get('rollover', 0)
            
            # Count correct predictions for each member THIS WEEK
            # Filter by this week's fixtures (created_at within current week)
            from datetime import datetime, timedelta
            week_start = datetime.now() - timedelta(days=7)
            
            user_scores = {}
            user_details = {}
            
            for user_id in member_ids:
                # Count correct predictions for this user this week
                correct_count = await db.predictions.count_documents({
                    "user_id": user_id,
                    "result": "correct",
                    "created_at": {"$gte": week_start.isoformat()}
                })
                
                if correct_count > 0:
                    user = await db.users.find_one({"id": user_id}, {"_id": 0})
                    user_scores[user_id] = correct_count
                    user_details[user_id] = {
                        "email": user.get('email'),
                        "username": user.get('username')
                    }
            
            if not user_scores:
                logger.info(f"  Team '{team_name}': No correct predictions this week - POT ROLLS OVER")
                
                # Roll over the pot to next week
                await db.weekly_pots.update_one(
                    {"team_id": team_id, "status": "active"},
                    {"$set": {"status": "rolled_over"}}
                )
                
                # Create next week's pot with rollover
                await db.weekly_pots.insert_one({
                    "id": str(uuid.uuid4()),
                    "team_id": team_id,
                    "team_name": team_name,
                    "total_pot": 0,  # Will be updated as people join
                    "rollover": current_pot,
                    "paid_entries": 0,
                    "status": "active",
                    "week_start": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat()
                })
                
                # Notify team admin about rollover
                team = await db.teams.find_one({"id": team_id}, {"_id": 0})
                admin_email = team.get('admin_email')
                if admin_email:
                    await send_rollover_notification(admin_email, team_name, current_pot)
                
                continue
            
            # Find the maximum score
            max_score = max(user_scores.values())
            
            # Find all users with max score (winners or tied winners)
            winners = [user_id for user_id, score in user_scores.items() if score == max_score]
            
            # Award points and send notifications based on winner count
            if len(winners) == 1:
                # SOLE WINNER - Gets the pot (minus 10% admin fee)
                winner_id = winners[0]
                winner = user_details[winner_id]
                
                points_to_award = 3
                await db.users.update_one(
                    {"id": winner_id},
                    {"$inc": {"season_points": points_to_award, "weekly_wins": 1}}
                )
                
                # Calculate winnings: Total pot - 10% admin fee
                total_pot_with_rollover = current_pot + rollover_amount
                admin_fee = total_pot_with_rollover * 0.10
                winner_amount = total_pot_with_rollover - admin_fee
                
                logger.info(f"  Team '{team_name}': WINNER {winner['username']} with {max_score} correct → 3 points, £{winner_amount:.2f}")
                
                # Get active nominations for this team
                nominations = await db.team_nominations.find(
                    {"team_id": team_id, "status": "active"},
                    {"_id": 0}
                ).sort("created_at", -1).to_list(10)
                
                # Get winner's correct prediction details
                correct_predictions = await db.predictions.find({
                    "user_id": winner_id,
                    "result": "correct",
                    "created_at": {"$gte": week_start.isoformat()}
                }, {"_id": 0, "home_team": 1, "away_team": 1, "prediction": 1}).to_list(100)
                
                # Send in-app notification to winner
                await create_notification(
                    user_id=winner_id,
                    notification_type='winner',
                    title='🏆 You Won This Week!',
                    message=f"Congratulations! You won with {max_score} correct predictions and earned £{winner_amount:.2f}! 🎉",
                    data={
                        "correct_predictions": max_score,
                        "payout": winner_amount,
                        "correct_predictions_details": correct_predictions
                    }
                )
                
                # Send winner notification email
                await send_winner_notification(
                    winner['email'],
                    winner['username'],
                    team_name,
                    max_score,
                    winner_amount,
                    admin_fee,
                    paid_entries,
                    team_id,
                    nominations
                )
                
                # Notify losers
                losers = [uid for uid in member_ids if uid not in winners]
                for loser_id in losers:
                    loser_score = user_scores.get(loser_id, 0)
                    await create_notification(
                        user_id=loser_id,
                        notification_type='loser',
                        title='😔 Not This Week!',
                        message=f"{winner['username']} won this week with {max_score} correct predictions. You got {loser_score} correct. Better luck next time! Keep coming back, keep predicting, and keep interacting with your friends. Football is unpredictable — anyone can win! 🎯⚽",
                        data={
                            "winner_username": winner['username'],
                            "winner_correct_predictions": max_score,
                            "your_correct_predictions": loser_score
                        }
                    )
                
                # Notify admin to pay the winner
                team = await db.teams.find_one({"id": team_id}, {"_id": 0})
                admin_email = team.get('admin_email')
                if admin_email:
                    await send_admin_payment_notification(
                        admin_email,
                        winner['username'],
                        winner['email'],
                        winner_amount,
                        team_name
                    )
                
                # Mark pot as paid out
                await db.weekly_pots.update_one(
                    {"team_id": team_id, "status": "active"},
                    {"$set": {
                        "status": "paid",
                        "winner": winner['username'],
                        "winner_amount": winner_amount,
                        "admin_fee": admin_fee,
                        "paid_at": datetime.now().isoformat()
                    }}
                )
                
                # Create new pot for next week (no rollover)
                await db.weekly_pots.insert_one({
                    "id": str(uuid.uuid4()),
                    "team_id": team_id,
                    "team_name": team_name,
                    "total_pot": 0,
                    "rollover": 0,
                    "paid_entries": 0,
                    "status": "active",
                    "week_start": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat()
                })
                
            else:
                # TIE - Each gets 1 point, POT ROLLS OVER
                points_to_award = 1
                
                winner_names = []
                for winner_id in winners:
                    await db.users.update_one(
                        {"id": winner_id},
                        {"$inc": {"season_points": points_to_award}}
                    )
                    winner = user_details[winner_id]
                    winner_names.append(winner['username'])
                    
                    # Get winner's correct prediction details
                    correct_predictions = await db.predictions.find({
                        "user_id": winner_id,
                        "result": "correct",
                        "created_at": {"$gte": week_start.isoformat()}
                    }, {"_id": 0, "home_team": 1, "away_team": 1, "prediction": 1}).to_list(100)
                    
                    # Send in-app notification for tie
                    other_winners = [w for w in winner_names if w != winner['username']]
                    await create_notification(
                        user_id=winner_id,
                        notification_type='tie',
                        title='🤝 You Tied This Week!',
                        message=f"You tied with {len(winners)-1} other player(s) with {max_score} correct predictions! Each of you earned 1 point. The pot of £{current_pot + rollover_amount:.2f} rolls over to next week. Keep predicting!",
                        data={
                            "correct_predictions": max_score,
                            "tied_with": other_winners,
                            "rollover_amount": current_pot + rollover_amount,
                            "correct_predictions_details": correct_predictions
                        }
                    )
                    
                    # Send tie notification email
                    await send_tie_notification(
                        winner['email'],
                        winner['username'],
                        team_name,
                        max_score,
                        len(winners),
                        current_pot + rollover_amount
                    )
                
                # Notify losers in tie scenario
                losers = [uid for uid in member_ids if uid not in winners]
                for loser_id in losers:
                    loser_score = user_scores.get(loser_id, 0)
                    await create_notification(
                        user_id=loser_id,
                        notification_type='loser',
                        title='😔 Not This Week!',
                        message=f"This week had a tie! {', '.join(winner_names)} tied with {max_score} correct predictions. You got {loser_score} correct. Better luck next time! Keep coming back, keep predicting, and keep interacting with your friends. Football is unpredictable — anyone can win! 🎯⚽",
                        data={
                            "winner_usernames": winner_names,
                            "winner_correct_predictions": max_score,
                            "your_correct_predictions": loser_score
                        }
                    )
                
                logger.info(f"  Team '{team_name}': TIE - {len(winners)} winners with {max_score} correct → 1 point each, POT ROLLS OVER")
                
                # Roll over the pot to next week
                await db.weekly_pots.update_one(
                    {"team_id": team_id, "status": "active"},
                    {"$set": {"status": "rolled_over"}}
                )
                
                # Create next week's pot with rollover
                new_rollover = current_pot + rollover_amount
                await db.weekly_pots.insert_one({
                    "id": str(uuid.uuid4()),
                    "team_id": team_id,
                    "team_name": team_name,
                    "total_pot": 0,
                    "rollover": new_rollover,
                    "paid_entries": 0,
                    "status": "active",
                    "week_start": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat()
                })
                
                # Notify team admin about tie and rollover
                team = await db.teams.find_one({"id": team_id}, {"_id": 0})
                admin_email = team.get('admin_email')
                if admin_email:
                    await send_admin_tie_notification(
                        admin_email,
                        team_name,
                        winner_names,
                        new_rollover
                    )
        
        logger.info("✅ Weekly winners calculated and notifications sent")
        
    except Exception as e:
        logger.error(f"❌ Error calculating weekly winners: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


async def send_winner_notification(email, username, team_name, correct_count, amount, admin_fee, entries, team_id, nominations=[]):
    """Send email to sole winner with optional community support nominations"""
    try:
        subject = f"🏆 You Won This Week's Pot! - {team_name}"
        
        # Build nominations section if any exist
        nominations_html = ""
        if nominations:
            nominations_html = """
                <div style="background: #fef3c7; padding: 25px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <h3 style="color: #d97706; margin-top: 0;">❤️ Community Support - Charity Begins at Home</h3>
                    <p style="font-size: 16px; color: #374151; line-height: 1.6;">
                        Your teammates have nominated members who could use support:
                    </p>
            """
            for nom in nominations[:3]:  # Show max 3
                reason_preview = nom.get('reason', '')[:100] + ('...' if len(nom.get('reason', '')) > 100 else '')
                nominations_html += f"""
                    <div style="background: white; padding: 15px; border-radius: 6px; margin: 10px 0;">
                        <p style="margin: 0 0 8px 0; font-size: 16px; font-weight: bold; color: #1f2937;">
                            🤝 {nom.get('nominee_username', 'Team member')}
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #6b7280; line-height: 1.4;">
                            {reason_preview}
                        </p>
                        <p style="margin: 8px 0 0 0; font-size: 12px; color: #9ca3af;">
                            Nominated by {nom.get('nominated_by_username', 'a teammate')}
                        </p>
                    </div>
                """
            nominations_html += f"""
                    <p style="font-size: 14px; color: #374151; line-height: 1.6; margin-top: 15px;">
                        💭 <em>You can choose to donate all or part of your winnings to help a teammate. 
                        No pressure - this is entirely your choice. See nominations in your team page.</em>
                    </p>
                </div>
            """
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🏆 Congratulations!</h1>
                </div>
                
                <div style="padding: 30px; background: #f9fafb;">
                    <h2 style="color: #1f2937;">Hi {username},</h2>
                    
                    <p style="font-size: 18px; color: #374151; line-height: 1.6;">
                        You are this week's <strong>SOLE WINNER</strong> for <strong>{team_name}</strong>!
                    </p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981;">
                        <h3 style="color: #059669; margin-top: 0;">Your Stats:</h3>
                        <p style="font-size: 16px; color: #374151;">✅ <strong>{correct_count}</strong> correct predictions</p>
                        <p style="font-size: 16px; color: #374151;">👥 <strong>{entries}</strong> players in this week's pot</p>
                    </div>
                    
                    <div style="background: #ecfdf5; padding: 25px; border-radius: 8px; margin: 20px 0; text-align: center;">
                        <h2 style="color: #059669; margin: 0 0 10px 0;">Your Winnings</h2>
                        <p style="font-size: 36px; font-weight: bold; color: #047857; margin: 10px 0;">£{amount:.2f}</p>
                        <p style="font-size: 14px; color: #6b7280; margin: 0;">(After 10% admin fee: £{admin_fee:.2f})</p>
                    </div>
                    
                    {nominations_html}
                    
                    <p style="font-size: 16px; color: #374151; line-height: 1.6;">
                        Your team admin will contact you shortly to arrange payment via bank transfer.
                    </p>
                    
                    <p style="font-size: 16px; color: #374151; line-height: 1.6;">
                        Keep up the great predictions! 🎯
                    </p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center;">
                        <p style="color: #6b7280; font-size: 14px;">
                            HadFun - Football With Purpose 💙
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        await send_email(email, subject, html_content)
        logger.info(f"✉️ Winner notification sent to {email} (with {len(nominations)} nominations)")
        
    except Exception as e:
        logger.error(f"Failed to send winner notification: {str(e)}")


async def send_tie_notification(email, username, team_name, correct_count, tie_count, rollover_amount):
    """Send email when there's a tie"""
    try:
        subject = f"🤝 This Week's Results - Pot Rolls Over! - {team_name}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🤝 It's a Tie!</h1>
                </div>
                
                <div style="padding: 30px; background: #f9fafb;">
                    <h2 style="color: #1f2937;">Hi {username},</h2>
                    
                    <p style="font-size: 18px; color: #374151; line-height: 1.6;">
                        This week in <strong>{team_name}</strong>, you tied with <strong>{tie_count - 1} other player(s)</strong> for most correct predictions!
                    </p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                        <h3 style="color: #d97706; margin-top: 0;">This Week's Result:</h3>
                        <p style="font-size: 16px; color: #374151;">✅ <strong>{correct_count}</strong> correct predictions (tied for best)</p>
                        <p style="font-size: 16px; color: #374151;">🏆 <strong>+1 point</strong> added to your season total</p>
                    </div>
                    
                    <div style="background: #fef3c7; padding: 25px; border-radius: 8px; margin: 20px 0; text-align: center;">
                        <h2 style="color: #d97706; margin: 0 0 10px 0;">Pot Rolls Over!</h2>
                        <p style="font-size: 28px; font-weight: bold; color: #b45309; margin: 10px 0;">£{rollover_amount:.2f}</p>
                        <p style="font-size: 14px; color: #78716c; margin: 0;">Added to next week's pot</p>
                    </div>
                    
                    <p style="font-size: 16px; color: #374151; line-height: 1.6;">
                        Since there was a tie, no payment this week. The pot rolls over to next week for an even bigger prize!
                    </p>
                    
                    <p style="font-size: 16px; color: #374151; line-height: 1.6;">
                        Good luck next week! 🍀
                    </p>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #e5e7eb; text-align: center;">
                        <p style="color: #6b7280; font-size: 14px;">
                            HadFun Predictor - Making Football Predictions Fun!
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        await send_email(email, subject, html_content)
        logger.info(f"✉️ Tie notification sent to {email}")
        
    except Exception as e:
        logger.error(f"Failed to send tie notification: {str(e)}")


async def send_admin_payment_notification(admin_email, winner_name, winner_email, amount, team_name):
    """Notify admin to pay the winner"""
    try:
        subject = f"💰 Payment Required - {team_name} Weekly Winner"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #1f2937; padding: 30px;">
                    <h1 style="color: white; margin: 0;">💰 Payment Required</h1>
                </div>
                
                <div style="padding: 30px; background: #f9fafb;">
                    <h2 style="color: #1f2937;">Weekly Winner - Action Required</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3b82f6;">
                        <h3 style="color: #1e40af; margin-top: 0;">Winner Details:</h3>
                        <p><strong>Team:</strong> {team_name}</p>
                        <p><strong>Winner:</strong> {winner_name}</p>
                        <p><strong>Email:</strong> {winner_email}</p>
                        <p style="font-size: 24px; color: #059669;"><strong>Amount to Pay:</strong> £{amount:.2f}</p>
                    </div>
                    
                    <p style="font-size: 16px; color: #374151; line-height: 1.6;">
                        Please arrange bank transfer payment to the winner at your earliest convenience.
                    </p>
                    
                    <p style="font-size: 14px; color: #6b7280;">
                        This is the net amount after 10% admin fee has been deducted.
                    </p>
                </div>
            </body>
        </html>
        """
        
        await send_email(admin_email, subject, html_content)
        logger.info(f"✉️ Admin payment notification sent to {admin_email}")
        
    except Exception as e:
        logger.error(f"Failed to send admin notification: {str(e)}")


async def send_admin_tie_notification(admin_email, team_name, winner_names, rollover_amount):
    """Notify admin about tie and rollover"""
    try:
        subject = f"🤝 Tie This Week - Pot Rolls Over - {team_name}"
        
        winners_list = "<br>".join([f"• {name}" for name in winner_names])
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #1f2937; padding: 30px;">
                    <h1 style="color: white; margin: 0;">🤝 Weekly Tie - No Payment</h1>
                </div>
                
                <div style="padding: 30px; background: #f9fafb;">
                    <h2 style="color: #1f2937;">Team: {team_name}</h2>
                    
                    <p style="font-size: 16px; color: #374151;">
                        This week ended in a tie. No payment required - pot rolls over to next week.
                    </p>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="color: #d97706;">Tied Winners:</h3>
                        <p>{winners_list}</p>
                        <p style="font-size: 20px; color: #b45309; margin-top: 15px;">
                            <strong>Rollover Amount:</strong> £{rollover_amount:.2f}
                        </p>
                    </div>
                    
                    <p style="font-size: 14px; color: #6b7280;">
                        This amount will be added to next week's pot for a bigger prize!
                    </p>
                </div>
            </body>
        </html>
        """
        
        await send_email(admin_email, subject, html_content)
        logger.info(f"✉️ Admin tie notification sent to {admin_email}")
        
    except Exception as e:
        logger.error(f"Failed to send admin tie notification: {str(e)}")


async def send_rollover_notification(admin_email, team_name, rollover_amount):
    """Notify admin when no one got any correct predictions"""
    try:
        subject = f"📊 No Winners This Week - Pot Rolls Over - {team_name}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #1f2937; padding: 30px;">
                    <h1 style="color: white; margin: 0;">📊 Weekly Update</h1>
                </div>
                
                <div style="padding: 30px; background: #f9fafb;">
                    <h2 style="color: #1f2937;">Team: {team_name}</h2>
                    
                    <p style="font-size: 16px; color: #374151;">
                        No players got any correct predictions this week.
                    </p>
                    
                    <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
                        <p style="font-size: 20px; color: #b45309;">
                            <strong>Rollover Amount:</strong> £{rollover_amount:.2f}
                        </p>
                        <p style="font-size: 14px; color: #78716c;">
                            Added to next week's pot
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        await send_email(admin_email, subject, html_content)
        
    except Exception as e:
        logger.error(f"Failed to send rollover notification: {str(e)}")


@api_router.post("/admin/trigger-scoring")
async def manual_trigger_scoring():
    """
    Manually trigger the scoring system
    Useful for testing or immediate updates
    """
    try:
        logger.info("🔧 Manual scoring trigger called...")
        
        # Call the automated result update function
        await automated_result_update()
        
        return {
            "success": True,
            "message": "Scoring system triggered successfully",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Error in manual trigger: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/admin/sync-predictions")
async def sync_predictions_with_fixtures():
    """
    Sync all predictions with current fixture data
    Updates predictions to include team names, scores, leagues directly
    """
    try:
        # Get all predictions
        all_predictions = await db.predictions.find({}).to_list(length=10000)
        
        updated_count = 0
        missing_fixtures = 0
        
        for pred in all_predictions:
            fixture_id = pred.get('fixture_id')
            
            # Find matching fixture
            fixture = await db.fixtures.find_one({"fixture_id": fixture_id})
            
            if fixture:
                # Update prediction with fixture details
                await db.predictions.update_one(
                    {"id": pred.get('id')},
                    {"$set": {
                        "home_team": fixture.get('home_team'),
                        "away_team": fixture.get('away_team'),
                        "league": fixture.get('league_name'),
                        "home_score": fixture.get('home_score'),
                        "away_score": fixture.get('away_score'),
                        "actual_result": pred.get('actual_result'),  # Keep if already scored
                        "match_date": fixture.get('utc_date') or fixture.get('match_date')
                    }}
                )
                updated_count += 1
            else:
                missing_fixtures += 1
        
        logger.info(f"✅ Synced {updated_count} predictions, {missing_fixtures} fixtures not found")
        
        return {
            "message": "Predictions synced successfully",
            "updated": updated_count,
            "missing_fixtures": missing_fixtures
        }
        
    except Exception as e:
        logger.error(f"Error syncing predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_scheduler():
    """Start the automated result checker and weekly winners calculation on app startup"""
    try:
        # Run one-time migration for Dec 2-3 scores (safe to run multiple times)
        logger.info("🔧 Running one-time Dec 2-3 score migration...")
        try:
            import subprocess
            result = subprocess.run(['python3', '/app/migrate_dec23_scores.py'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Dec 2-3 scores migrated successfully")
            else:
                logger.warning(f"⚠️  Migration script issue: {result.stderr}")
        except Exception as e:
            logger.warning(f"⚠️  Could not run migration script: {e}")
        
        # Run result updates every 15 minutes to score predictions
        scheduler.add_job(
            automated_result_update,
            CronTrigger(minute='*/15'),  # Every 15 minutes: :00, :15, :30, :45
            id='result_checker',
            replace_existing=True
        )
        
        # Run weekly winners calculation every Wednesday at 2 PM GMT
        # This awards points (3 for solo winner, 1 for ties) after weekend matches
        scheduler.add_job(
            calculate_weekly_winners,
            CronTrigger(day_of_week='wed', hour=14, minute=0),  # Wednesday 2:00 PM
            id='weekly_winners',
            replace_existing=True
        )
        
        # ALSO run weekly winners every day at 6 PM to catch any completed matchdays
        # (Some leagues play Mon/Tue, so we check daily)
        scheduler.add_job(
            calculate_weekly_winners,
            CronTrigger(hour=18, minute=0),  # Daily at 6:00 PM
            id='daily_winners_check',
            replace_existing=True
        )
        
        # LIVE MATCH UPDATES: Check every 2 minutes for in-play matches
        # Updates scores in real-time without scoring predictions
        scheduler.add_job(
            live_match_update,
            CronTrigger(minute='*/2'),  # Every 2 minutes
            id='live_match_checker',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("🚀 Automated scheduler started:")
        logger.info("   - Live match updates: every 2 minutes 🔴")
        logger.info("   - Result checker: every 15 minutes")
        logger.info("   - Weekly winners: Wednesdays 2 PM + Daily 6 PM")
        
        # Log all scheduled jobs for debugging
        jobs = scheduler.get_jobs()
        logger.info(f"📋 Total scheduled jobs: {len(jobs)}")
        for job in jobs:
            logger.info(f"   - {job.id}: {job.next_run_time}")
        
        # Run once immediately on startup to catch any pending updates
        logger.info("🔧 Running initial result update...")
        await automated_result_update()
        logger.info("✅ Initial result update complete")
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")

@app.on_event("shutdown")
async def shutdown_scheduler():
    """Shutdown scheduler gracefully"""
    scheduler.shutdown()
    logger.info("Scheduler shut down")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()


# Emergency data restoration endpoint
@api_router.post("/emergency/restore-cheshunt-crew")
async def emergency_restore_data():
    """
    Emergency endpoint to restore Cheshunt Crew team and predictions
    """
    import random
    from uuid import uuid4
    import bcrypt
    
    try:
        # Define all user data
        users_data = [
            {'username': 'aysin', 'email': 'info@hadfun.co.uk', 'predictions': 38},
            {'username': 'pistachios', 'email': 'pistachios@hadfun.co.uk', 'predictions': 29},
            {'username': 'aysindjemil', 'email': 'aysindjemil@yahoo.com', 'predictions': 29},
            {'username': 'Josh', 'email': 'admin@', 'predictions': 29},
            {'username': 'Remster', 'email': 'Remie.djemil@gmail.com', 'predictions': 10},
            {'username': 'Ayhan', 'email': 'ayhanozgegiet@gmail.com', 'predictions': 9},
            {'username': 'Leeanne', 'email': 'leeanne@example.com', 'predictions': 0},
        ]
        
        user_ids = {}
        
        # Ensure all users exist
        for user_data in users_data:
            username = user_data['username']
            user = await db.users.find_one({'username': username}, {'_id': 0})
            
            if user:
                user_ids[username] = user['id']
            else:
                user_id = str(uuid4())
                password_hash = bcrypt.hashpw(b'temppass123', bcrypt.gensalt()).decode('utf-8')
                
                new_user = {
                    'id': user_id,
                    'username': username,
                    'email': user_data['email'],
                    'password_hash': password_hash,
                    'profile_completed': True,
                    'season_points': 0,
                    'weekly_points': 0,
                    'weekly_wins': 0,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
                
                await db.users.insert_one(new_user)
                user_ids[username] = user_id
        
        # Create/verify team
        team = await db.teams.find_one({'join_code': '256BFA9A'}, {'_id': 0})
        
        if not team:
            team_id = str(uuid4())
            team_data = {
                'id': team_id,
                'name': 'Cheshunt Crew',
                'join_code': '256BFA9A',
                'motto': 'Playing for fun',
                'created_at': datetime.now(timezone.utc).isoformat(),
                'created_by': user_ids.get('aysin', 'unknown')
            }
            await db.teams.insert_one(team_data)
        else:
            team_id = team['id']
        
        # Add members
        for username, uid in user_ids.items():
            existing = await db.team_members.find_one({'team_id': team_id, 'user_id': uid}, {'_id': 0})
            
            if not existing:
                member_data = {
                    'id': str(uuid4()),
                    'team_id': team_id,
                    'user_id': uid,
                    'username': username,
                    'joined_at': datetime.now(timezone.utc).isoformat(),
                    'role': 'admin' if username == 'aysin' else 'member'
                }
                await db.team_members.insert_one(member_data)
        
        # Get fixtures
        fixtures = await db.fixtures.find({}, {'_id': 0}).to_list(500)
        premier_fixtures = [f for f in fixtures if 'premier' in f.get('league_name', '').lower()]
        
        # Create predictions
        total_created = 0
        for user_data in users_data:
            username = user_data['username']
            user_id = user_ids[username]
            target_count = user_data['predictions']
            
            if target_count == 0:
                continue
            
            available = premier_fixtures if len(premier_fixtures) > 0 else fixtures
            count = min(target_count, len(available))
            selected = random.sample(available, count)
            
            for fixture in selected:
                existing = await db.predictions.find_one({'user_id': user_id, 'fixture_id': fixture['fixture_id']}, {'_id': 0})
                
                if not existing:
                    prediction_data = {
                        'id': str(uuid4()),
                        'user_id': user_id,
                        'username': username,
                        'fixture_id': fixture['fixture_id'],
                        'league_name': fixture.get('league_name', 'Unknown'),
                        'home_team': fixture['home_team'],
                        'away_team': fixture['away_team'],
                        'prediction': random.choice(['home', 'draw', 'away']),
                        'result': 'pending',
                        'points': 0,
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'fixture_date': fixture.get('fixture_date', datetime.now(timezone.utc).isoformat())
                    }
                    await db.predictions.insert_one(prediction_data)
                    total_created += 1
        
        return {
            'success': True,
            'message': 'Cheshunt Crew restored successfully',
            'team_members': len(user_ids),
            'predictions_created': total_created
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

