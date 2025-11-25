from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from models import User, UserCreate, UserProfileUpdate
from typing import Optional

router = APIRouter(prefix="/users", tags=["auth"])

# MongoDB connection will be injected
db = None

def set_db(database):
    global db
    db = database


@router.post("", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    existing = await db.users.find_one({"username": user.username}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check email uniqueness
    existing_email = await db.users.find_one({"email": user.email}, {"_id": 0})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Check team capacity
    settings = await db.team_settings.find_one({}, {"_id": 0})
    if settings:
        member_count = await db.users.count_documents({})
        max_members = settings.get('max_members', 30)
        
        if member_count >= max_members:
            raise HTTPException(
                status_code=400,
                detail=f"Team is full. Maximum {max_members} members allowed."
            )
    
    user_obj = User(username=user.username, email=user.email)
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.users.insert_one(doc)
    return user_obj


@router.get("/{username}", response_model=User)
async def get_user(username: str):
    """Get user by username"""
    user = await db.users.find_one({"username": username}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/id/{user_id}", response_model=User)
async def get_user_by_id(user_id: str):
    """Get user by ID"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}/profile", response_model=User)
async def update_user_profile(user_id: str, profile_data: UserProfileUpdate):
    """
    Update user profile (REQUIRES AUTH + OWNERSHIP)
    This endpoint allows users to complete or update their profile
    """
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {}
    
    # Validate and update fields
    if profile_data.full_name is not None:
        if len(profile_data.full_name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Full name cannot be empty")
        if len(profile_data.full_name) > 100:
            raise HTTPException(status_code=400, detail="Full name too long (max 100 characters)")
        update_data["full_name"] = profile_data.full_name.strip()
    
    if profile_data.bio is not None:
        if len(profile_data.bio) > 500:
            raise HTTPException(status_code=400, detail="Bio exceeds 500 character limit")
        update_data["bio"] = profile_data.bio.strip()
    
    if profile_data.birthdate is not None:
        # Validate date format YYYY-MM-DD
        try:
            datetime.strptime(profile_data.birthdate, "%Y-%m-%d")
            update_data["birthdate"] = profile_data.birthdate
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid birthdate format. Use YYYY-MM-DD")
    
    if profile_data.avatar_url is not None:
        update_data["avatar_url"] = profile_data.avatar_url
    
    if profile_data.location is not None:
        if len(profile_data.location) > 100:
            raise HTTPException(status_code=400, detail="Location too long (max 100 characters)")
        update_data["location"] = profile_data.location.strip()
    
    if profile_data.favorite_team is not None:
        if len(profile_data.favorite_team) > 100:
            raise HTTPException(status_code=400, detail="Favorite team name too long (max 100 characters)")
        update_data["favorite_team"] = profile_data.favorite_team.strip()
    
    if profile_data.favorite_leagues is not None:
        if len(profile_data.favorite_leagues) > 20:
            raise HTTPException(status_code=400, detail="Too many favorite leagues (max 20)")
        update_data["favorite_leagues"] = profile_data.favorite_leagues
    
    if profile_data.interests is not None:
        if len(profile_data.interests) > 200:
            raise HTTPException(status_code=400, detail="Interests too long (max 200 characters)")
        update_data["interests"] = profile_data.interests.strip()
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": user_id}, {"_id": 0})
    return updated_user


@router.post("/{user_id}/complete-profile", response_model=User)
async def complete_profile(user_id: str, profile_data: UserProfileUpdate):
    """
    Complete user profile for the first time
    Requires: full_name, birthdate (minimum fields)
    """
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("profile_completed", False):
        raise HTTPException(status_code=400, detail="Profile already completed. Use PUT /users/{user_id}/profile to update")
    
    # Validate required fields
    if not profile_data.full_name or len(profile_data.full_name.strip()) == 0:
        raise HTTPException(status_code=400, detail="Full name is required")
    
    if not profile_data.birthdate:
        raise HTTPException(status_code=400, detail="Birthdate is required")
    
    # Validate birthdate format and age (must be at least 13 years old)
    try:
        birth_date = datetime.strptime(profile_data.birthdate, "%Y-%m-%d")
        today = datetime.now(timezone.utc)
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 13:
            raise HTTPException(status_code=400, detail="You must be at least 13 years old to use this platform")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid birthdate format. Use YYYY-MM-DD")
    
    # Build update data
    update_data = {
        "full_name": profile_data.full_name.strip(),
        "birthdate": profile_data.birthdate,
        "profile_completed": True,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Optional fields
    if profile_data.bio:
        if len(profile_data.bio) > 500:
            raise HTTPException(status_code=400, detail="Bio exceeds 500 character limit")
        update_data["bio"] = profile_data.bio.strip()
    
    if profile_data.avatar_url:
        update_data["avatar_url"] = profile_data.avatar_url
    
    if profile_data.location:
        if len(profile_data.location) > 100:
            raise HTTPException(status_code=400, detail="Location too long")
        update_data["location"] = profile_data.location.strip()
    
    if profile_data.favorite_team:
        if len(profile_data.favorite_team) > 100:
            raise HTTPException(status_code=400, detail="Favorite team name too long")
        update_data["favorite_team"] = profile_data.favorite_team.strip()
    
    if profile_data.favorite_leagues:
        if len(profile_data.favorite_leagues) > 20:
            raise HTTPException(status_code=400, detail="Too many favorite leagues")
        update_data["favorite_leagues"] = profile_data.favorite_leagues
    
    if profile_data.interests:
        if len(profile_data.interests) > 200:
            raise HTTPException(status_code=400, detail="Interests too long")
        update_data["interests"] = profile_data.interests.strip()
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": user_id}, {"_id": 0})
    return updated_user


@router.get("/{user_id}/profile-status")
async def check_profile_status(user_id: str):
    """Check if user has completed their profile"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "profile_completed": 1, "username": 1})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "profile_completed": user.get("profile_completed", False),
        "username": user.get("username")
    }
