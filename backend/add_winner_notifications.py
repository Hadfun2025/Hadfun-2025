"""
Script to add winner notification endpoints to server.py
This adds:
1. Notification creation when winners are calculated
2. API endpoints to fetch notifications
3. Mark notifications as read
"""

# This will be integrated into server.py
NOTIFICATION_ENDPOINTS = '''

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
'''

# Updated winner calculation with notifications
UPDATED_WINNER_CALCULATION = '''
@api_router.post("/pot/calculate-winner")
async def calculate_weekly_winner():
    """Calculate winner for current week and send notifications"""
    cycle = await get_or_create_weekly_cycle()
    week_id = cycle['week_id']
    
    # Get all predictions for this week
    pipeline = [
        {"$match": {"week_id": week_id}},
        {
            "$group": {
                "_id": "$user_id",
                "username": {"$first": "$username"},
                "correct_count": {"$sum": {"$cond": [{"$eq": ["$result", "correct"]}, 1, 0]}},
                "total_predictions": {"$sum": 1},
                "correct_predictions_details": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$result", "correct"]},
                            {
                                "fixture_id": "$fixture_id",
                                "home_team": "$home_team",
                                "away_team": "$away_team",
                                "prediction": "$prediction"
                            },
                            "$$REMOVE"
                        ]
                    }
                }
            }
        },
        {"$sort": {"correct_count": -1}}
    ]
    
    results = await db.predictions.aggregate(pipeline).to_list(None)
    
    if not results:
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
        # Tie - notify all winners
        for winner in winners:
            await db.users.update_one(
                {"id": winner['_id']},
                {"$inc": {"season_points": 1}}
            )
            
            # Send tie notification
            await create_notification(
                user_id=winner['_id'],
                notification_type='tie',
                title='🤝 You Tied This Week!',
                message=f"You tied with {len(winners)-1} other player(s) with {top_score} correct predictions! Each of you earned 1 point. The pot of £{distributable:.2f} rolls over to next week. Keep predicting!",
                data={
                    "correct_predictions": top_score,
                    "tied_with": [w['username'] for w in winners if w['_id'] != winner['_id']],
                    "rollover_amount": distributable,
                    "correct_predictions_details": winner.get('correct_predictions_details', [])
                }
            )
        
        # Notify losers
        losers = [r for r in results if r['correct_count'] < top_score]
        for loser in losers:
            await create_notification(
                user_id=loser['_id'],
                notification_type='loser',
                title='😔 Not This Week!',
                message=f"This week had a tie! {', '.join([w['username'] for w in winners])} tied with {top_score} correct predictions. You got {loser['correct_count']} correct. Better luck next time! Keep coming back, keep predicting, and keep interacting with your friends. Football is unpredictable — anyone can win! 🎯⚽",
                data={
                    "winner_usernames": [w['username'] for w in winners],
                    "winner_correct_predictions": top_score,
                    "your_correct_predictions": loser['correct_count'],
                    "your_total_predictions": loser['total_predictions']
                }
            )
        
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
        
        next_week_id = get_week_id(datetime.now() + timedelta(days=7))
        await db.weekly_cycles.update_one(
            {"week_id": next_week_id},
            {"$set": {"rollover_amount": distributable}},
            upsert=True
        )
        
        return {
            "message": "Tie detected. Notifications sent.",
            "tied_users": [w['username'] for w in winners],
            "rollover_amount": distributable
        }
    
    # Single winner
    winner = winners[0]
    
    await db.users.update_one(
        {"id": winner['_id']},
        {
            "$inc": {
                "season_points": 3,
                "weekly_wins": 1
            }
        }
    )
    
    # Send winner notification
    await create_notification(
        user_id=winner['_id'],
        notification_type='winner',
        title='🏆 You Won This Week!',
        message=f"Congratulations! You won with {top_score} correct predictions and earned £{distributable:.2f}! 🎉",
        data={
            "correct_predictions": top_score,
            "payout": distributable,
            "total_predictions": winner['total_predictions'],
            "correct_predictions_details": winner.get('correct_predictions_details', [])
        }
    )
    
    # Send loser notifications
    losers = [r for r in results if r['correct_count'] < top_score]
    for loser in losers:
        await create_notification(
            user_id=loser['_id'],
            notification_type='loser',
            title='😔 Not This Week!',
            message=f"{winner['username']} won this week with {top_score} correct predictions. You got {loser['correct_count']} correct. Better luck next time! Keep coming back, keep predicting, and keep interacting with your friends. Football is unpredictable — anyone can win! 🎯⚽",
            data={
                "winner_username": winner['username'],
                "winner_correct_predictions": top_score,
                "your_correct_predictions": loser['correct_count'],
                "your_total_predictions": loser['total_predictions']
            }
        )
    
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
        "message": "Winner calculated and notifications sent",
        "winner": winner['username'],
        "correct_predictions": top_score,
        "payout": distributable
    }
'''

print("Notification system code ready for integration")
print("\nFeatures:")
print("1. Create notifications when winners/losers are determined")
print("2. Show correct predictions to winners")
print("3. Motivational messages to losers")
print("4. API endpoints to fetch and manage notifications")
