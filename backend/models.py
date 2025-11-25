from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import uuid


class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_points: int = 0
    season_points: int = 0
    weekly_wins: int = 0
    
    # Profile fields for social feature
    full_name: Optional[str] = None
    bio: Optional[str] = None
    birthdate: Optional[str] = None  # YYYY-MM-DD format
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    favorite_team: Optional[str] = None
    favorite_leagues: List[int] = []  # List of league IDs
    interests: Optional[str] = None  # Comma-separated interests
    profile_completed: bool = False


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
    user_email: Optional[str] = None
    username: str
    fixture_id: int
    prediction: str  # "home", "draw", "away"
    league_id: int
    match_date: str
    week_id: str  # Week identifier (e.g., "2024-W42")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    points: Optional[int] = None
    result: Optional[str] = None  # "correct", "incorrect", "pending"
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    league: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class PredictionCreate(BaseModel):
    user_id: str
    username: str
    fixture_id: int
    prediction: str
    league_id: int
    match_date: str


class WeeklyCycle(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    week_id: str  # e.g., "2024-W42"
    week_start: datetime
    week_end: datetime
    cutoff_date: datetime  # Wednesday or day before fixtures
    stake_amount: float  # £2, £3, or £5
    total_pot: float
    admin_fee: float  # 10%
    distributable_pot: float
    status: str  # "active", "closed", "distributed", "rollover"
    winner_id: Optional[str] = None
    winner_username: Optional[str] = None
    is_tie: bool = False
    tied_users: List[str] = []
    rollover_amount: float = 0
    charity_mode: bool = False
    charity_name: Optional[str] = None


class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    week_id: str
    amount: float
    paypal_order_id: Optional[str] = None
    status: str  # "pending", "completed", "failed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class PaymentCreate(BaseModel):
    user_id: str
    username: str
    week_id: str
    amount: float


class TeamSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_name: str = "My Predictions Team"
    play_mode: str = "fun"  # "fun" or "pot" (with money)
    stake_amount: float = 5.0  # £2, £3, or £5
    admin_fee_percentage: float = 10.0
    charity_mode: bool = False
    charity_name: Optional[str] = None
    season_prize_pool: float = 0
    min_members: int = 2
    max_members: int = 30
    season_start: datetime = Field(default_factory=datetime.utcnow)
    season_end: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=270))


class LeaderboardEntry(BaseModel):
    username: str
    total_points: int
    season_points: int
    correct_predictions: int
    total_predictions: int
    weekly_wins: int
    rank: int
    team_name: str


class WeeklyResult(BaseModel):
    week_id: str
    week_start: str
    week_end: str
    winner_username: Optional[str]
    pot_amount: float
    admin_fee: float
    winner_payout: float
    is_tie: bool
    tied_users: List[str]
    top_predictors: List[dict]



class PromoCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # e.g., "HADFUN10"
    description: str
    discount_type: str  # "fixed" or "percentage"
    discount_value: float  # e.g., 3.0 for £3 off, or 50 for 50% off
    stake_amount: float  # Fixed stake amount for this promo (e.g., £3)
    max_uses: Optional[int] = None  # Total uses allowed (e.g., 100 for 10 teams x 10 members)
    current_uses: int = 0
    max_uses_per_user: Optional[int] = 1  # Uses per user
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    is_active: bool = True
    requires_review: bool = False  # Require review after promo period
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # Admin email


class PromoCodeCreate(BaseModel):
    code: str
    description: str
    discount_type: str = "fixed"
    discount_value: float
    stake_amount: float = 3.0
    max_uses: Optional[int] = None
    max_uses_per_user: int = 1
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    requires_review: bool = False


class PromoCodeUsage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    promo_code_id: str
    promo_code: str
    user_id: str
    user_email: str
    team_id: Optional[str] = None


# ========== SOCIAL FEATURE MODELS ==========

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    birthdate: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    favorite_team: Optional[str] = None
    favorite_leagues: Optional[List[int]] = None
    interests: Optional[str] = None


class Post(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str
    author_username: str
    author_avatar: Optional[str] = None
    content: str  # Max 5000 characters
    images: List[str] = []  # List of image URLs
    videos: List[str] = []  # List of video URLs (YouTube, direct URLs, etc.)
    charity_name: Optional[str] = None  # Free-text charity/cause name
    charity_description: Optional[str] = None  # Short description of the cause
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PostCreate(BaseModel):
    content: str
    images: Optional[List[str]] = []
    videos: Optional[List[str]] = []
    charity_name: Optional[str] = None
    charity_description: Optional[str] = None


class PostUpdate(BaseModel):
    content: Optional[str] = None
    images: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    charity_name: Optional[str] = None
    charity_description: Optional[str] = None


class Comment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    author_id: str
    author_username: str
    author_avatar: Optional[str] = None
    content: str  # Max 1000 characters
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CommentCreate(BaseModel):
    content: str


class Like(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    username: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromoCodeValidation(BaseModel):
    code: str
    user_email: str
    team_id: Optional[str] = None
