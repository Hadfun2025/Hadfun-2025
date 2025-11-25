from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime, timezone
from models import Post, PostCreate, PostUpdate, Comment, CommentCreate, Like, User
import os

router = APIRouter(prefix="/posts", tags=["posts"])

# MongoDB connection will be injected
db = None

def set_db(database):
    global db
    db = database


# Helper function to check if user profile is completed
async def require_profile_completed(user_id: str):
    """Check if user has completed their profile"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.get("profile_completed", False):
        raise HTTPException(
            status_code=403, 
            detail="Please complete your profile before posting"
        )
    return user


# ========== POST ENDPOINTS ==========

@router.get("", response_model=List[Post])
async def get_posts(skip: int = 0, limit: int = 20, author_id: Optional[str] = None):
    """
    Get all posts (PUBLIC - no auth required)
    Supports pagination and filtering by author
    """
    query = {}
    if author_id:
        query["author_id"] = author_id
    
    posts = await db.posts.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return posts


@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str):
    """Get single post by ID (PUBLIC - no auth required)"""
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("", response_model=Post)
async def create_post(post_data: PostCreate, user_id: str = Query(...)):
    """
    Create a new post (REQUIRES AUTH + COMPLETED PROFILE)
    Content limit: 5000 characters
    Images: Up to 5 image URLs
    """
    # Validate profile completion
    user = await require_profile_completed(user_id)
    
    # Validate content length
    if len(post_data.content) > 5000:
        raise HTTPException(status_code=400, detail="Content exceeds 5000 character limit")
    
    if len(post_data.content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Content cannot be empty")
    
    # Validate images count
    if post_data.images and len(post_data.images) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images allowed per post")
    
    # Validate videos count
    if post_data.videos and len(post_data.videos) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 videos allowed per post")
    
    # Validate charity description if charity name provided
    if post_data.charity_name and post_data.charity_description:
        if len(post_data.charity_description) > 500:
            raise HTTPException(status_code=400, detail="Charity description exceeds 500 character limit")
    
    # Create post
    post = Post(
        author_id=user["id"],
        author_username=user["username"],
        author_avatar=user.get("avatar_url"),
        content=post_data.content,
        images=post_data.images or [],
        videos=post_data.videos or [],
        charity_name=post_data.charity_name,
        charity_description=post_data.charity_description
    )
    
    post_dict = post.model_dump()
    post_dict["created_at"] = post_dict["created_at"].isoformat()
    post_dict["updated_at"] = post_dict["updated_at"].isoformat()
    
    await db.posts.insert_one(post_dict)
    return post


@router.put("/{post_id}", response_model=Post)
async def update_post(post_id: str, post_data: PostUpdate, user_id: str = Query(...)):
    """Update a post (REQUIRES AUTH + OWNERSHIP)"""
    # Check if post exists and user is the author
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post["author_id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")
    
    # Validate content if provided
    update_data = {}
    if post_data.content is not None:
        if len(post_data.content) > 5000:
            raise HTTPException(status_code=400, detail="Content exceeds 5000 character limit")
        if len(post_data.content.strip()) == 0:
            raise HTTPException(status_code=400, detail="Content cannot be empty")
        update_data["content"] = post_data.content
    
    if post_data.images is not None:
        if len(post_data.images) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 images allowed per post")
        update_data["images"] = post_data.images
    
    if post_data.videos is not None:
        if len(post_data.videos) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 videos allowed per post")
        update_data["videos"] = post_data.videos
    
    if post_data.charity_name is not None:
        update_data["charity_name"] = post_data.charity_name
    
    if post_data.charity_description is not None:
        if len(post_data.charity_description) > 500:
            raise HTTPException(status_code=400, detail="Charity description exceeds 500 character limit")
        update_data["charity_description"] = post_data.charity_description
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.posts.update_one({"id": post_id}, {"$set": update_data})
    
    updated_post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    return updated_post


@router.delete("/{post_id}")
async def delete_post(post_id: str, user_id: str = Query(...)):
    """Delete a post (REQUIRES AUTH + OWNERSHIP)"""
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post["author_id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    # Delete post and all associated comments and likes
    await db.posts.delete_one({"id": post_id})
    await db.comments.delete_many({"post_id": post_id})
    await db.likes.delete_many({"post_id": post_id})
    
    return {"message": "Post deleted successfully"}


# ========== COMMENT ENDPOINTS ==========

@router.get("/{post_id}/comments", response_model=List[Comment])
async def get_comments(post_id: str, skip: int = 0, limit: int = 50):
    """Get comments for a post (PUBLIC - no auth required)"""
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = await db.comments.find({"post_id": post_id}, {"_id": 0}).sort("created_at", 1).skip(skip).limit(limit).to_list(limit)
    return comments


@router.post("/{post_id}/comments", response_model=Comment)
async def create_comment(post_id: str, comment_data: CommentCreate, user_id: str = Query(...)):
    """Create a comment (REQUIRES AUTH + COMPLETED PROFILE)"""
    # Validate profile completion
    user = await require_profile_completed(user_id)
    
    # Check if post exists
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Validate content length
    if len(comment_data.content) > 1000:
        raise HTTPException(status_code=400, detail="Comment exceeds 1000 character limit")
    
    if len(comment_data.content.strip()) == 0:
        raise HTTPException(status_code=400, detail="Comment cannot be empty")
    
    # Create comment
    comment = Comment(
        post_id=post_id,
        author_id=user["id"],
        author_username=user["username"],
        author_avatar=user.get("avatar_url"),
        content=comment_data.content
    )
    
    comment_dict = comment.model_dump()
    comment_dict["created_at"] = comment_dict["created_at"].isoformat()
    
    await db.comments.insert_one(comment_dict)
    
    # Update comment count on post
    await db.posts.update_one(
        {"id": post_id},
        {"$inc": {"comments_count": 1}}
    )
    
    return comment


@router.delete("/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: str, comment_id: str, user_id: str = Query(...)):
    """Delete a comment (REQUIRES AUTH + OWNERSHIP)"""
    comment = await db.comments.find_one({"id": comment_id, "post_id": post_id}, {"_id": 0})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment["author_id"] != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    
    await db.comments.delete_one({"id": comment_id})
    
    # Update comment count on post
    await db.posts.update_one(
        {"id": post_id},
        {"$inc": {"comments_count": -1}}
    )
    
    return {"message": "Comment deleted successfully"}


# ========== LIKE ENDPOINTS ==========

@router.post("/{post_id}/like")
async def like_post(post_id: str, user_id: str = Query(...)):
    """Like a post (REQUIRES AUTH)"""
    # Check if post exists
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already liked
    existing_like = await db.likes.find_one({"post_id": post_id, "user_id": user_id}, {"_id": 0})
    if existing_like:
        raise HTTPException(status_code=400, detail="You already liked this post")
    
    # Get user info
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create like
    like = Like(
        post_id=post_id,
        user_id=user_id,
        username=user["username"]
    )
    
    like_dict = like.model_dump()
    like_dict["created_at"] = like_dict["created_at"].isoformat()
    
    await db.likes.insert_one(like_dict)
    
    # Update like count on post
    await db.posts.update_one(
        {"id": post_id},
        {"$inc": {"likes_count": 1}}
    )
    
    return {"message": "Post liked successfully"}


@router.delete("/{post_id}/like")
async def unlike_post(post_id: str, user_id: str = Query(...)):
    """Unlike a post (REQUIRES AUTH)"""
    like = await db.likes.find_one({"post_id": post_id, "user_id": user_id}, {"_id": 0})
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    await db.likes.delete_one({"post_id": post_id, "user_id": user_id})
    
    # Update like count on post
    await db.posts.update_one(
        {"id": post_id},
        {"$inc": {"likes_count": -1}}
    )
    
    return {"message": "Post unliked successfully"}


@router.get("/{post_id}/likes")
async def get_post_likes(post_id: str):
    """Get users who liked a post (PUBLIC)"""
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    likes = await db.likes.find({"post_id": post_id}, {"_id": 0}).to_list(1000)
    return likes
