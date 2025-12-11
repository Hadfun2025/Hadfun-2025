from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid


class Team(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    admin_user_id: str
    admin_username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    member_count: int = 0
    stake_amount: float = 5.0
    play_mode: str = "fun"  # "fun" or "pot"
    is_private: bool = True
    join_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())


class TeamCreate(BaseModel):
    name: str
    admin_user_id: str
    admin_username: str
    stake_amount: float = 5.0
    play_mode: str = "fun"
    is_private: bool = True


class TeamMember(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    user_id: str
    username: str
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    role: str = "member"  # "admin" or "member"


class TeamJoin(BaseModel):
    user_id: str
    username: str
    join_code: str


class TeamMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    user_id: str
    username: str
    message: str
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    likes: int = 0


class MessageCreate(BaseModel):
    team_id: str
    user_id: str
    username: str
    message: str
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)


class TeamStats(BaseModel):
    team_id: str
    team_name: str
    total_members: int
    total_predictions: int
    correct_predictions: int
    accuracy_percentage: float
    top_predictor: Optional[str] = None


class TeamNomination(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    nominee_user_id: str
    nominee_username: str
    nominated_by_user_id: str
    nominated_by_username: str
    reason: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # "active", "fulfilled", "cancelled"
    is_anonymous: bool = False


class NominationCreate(BaseModel):
    team_id: str
    nominee_user_id: str
    nominee_username: str
    nominated_by_user_id: str
    nominated_by_username: str
    reason: str
    is_anonymous: bool = False


class WinnerDonation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    winner_user_id: str
    winner_username: str
    recipient_user_id: str
    recipient_username: str
    amount: float
    week_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None



class TeamInvitation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    team_name: str
    inviter_user_id: str
    inviter_username: str
    invited_user_id: str
    invited_username: str
    status: str = "pending"  # "pending", "accepted", "declined"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None


class InvitationCreate(BaseModel):
    team_id: str
    inviter_user_id: str
    invited_user_id: str
