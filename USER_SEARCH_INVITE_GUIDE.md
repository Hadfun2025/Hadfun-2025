# 🔍 User Search & Invite Feature - User Guide

## Overview
You can now **search for users by username** and **send them team invitations** directly from the app, without needing their email addresses!

---

## How to Invite Users to Your Team

### **Option 1: Search & Invite (New! ✨)**

1. **Go to "My Team" tab**
2. **Click on "Team Members" sub-tab**
3. **Find the "Search & Invite Users" section** (green box)
4. **Type the username** in the search box (e.g., "Remste", "Davidwhu", or "Ender")
5. **Click "Search"**
6. **Click "Invite" button** next to the user you want to invite
7. **Done!** They'll receive an invitation to join your team

### **Option 2: Share Join Code (Still Works!)**

Share your team's join code: **`256BFA9A`**

Users can:
1. Go to "My Team" tab
2. Click "Join Team"
3. Enter the code
4. Instantly join!

### **Option 3: Email Invitation (If you know their email)**

1. Go to "My Team" → "Team Members"
2. Enter their email address
3. Click "Send Invite"

---

## For Users Receiving Invitations

When someone invites you to join their team:

1. **You'll see a notification** on the "My Team" page
2. **A green "Team Invitations" card** will appear showing:
   - Team name
   - Who invited you
   - When you were invited
3. **Click "Accept"** to join the team
4. **Or click "Decline"** if you're not interested

---

## Privacy & Security 🔒

- **User emails are NOT shown** to other users (even team admins)
- Only **usernames** are visible in search results
- Users can **accept or decline** invitations
- Invitations expire after being responded to

---

## Example: Inviting Remste, Davidwhu, and Ender

Since you mentioned these users have joined the app:

1. Go to **My Team** → **Team Members**
2. In the **"Search & Invite Users"** section:
   - Search for "Remste" → Click **Invite**
   - Search for "Davidwhu" → Click **Invite**
   - Search for "Ender" → Click **Invite**
3. They'll see invitations when they next visit the app
4. They can accept to join **Cheshunt Crew**!

---

## Benefits of This Feature

✅ **No need for email addresses** - Search by username only  
✅ **Quick & easy** - Send invitations with one click  
✅ **In-app notifications** - Users see invitations immediately  
✅ **Privacy-focused** - No personal information exposed  
✅ **User control** - Recipients can accept or decline  

---

## Technical Details

**Backend Endpoints:**
- `GET /api/users/search?q={username}` - Search users
- `POST /api/teams/{team_id}/invite-user` - Send invitation
- `GET /api/users/{user_id}/invitations` - Get pending invitations
- `POST /api/teams/invitations/{invitation_id}/accept` - Accept invitation
- `POST /api/teams/invitations/{invitation_id}/decline` - Decline invitation

**Database Collections:**
- `team_invitations` - Stores all team invitations with status tracking

---

## Need Help?

If you have any questions or issues with the user search and invite feature, please let me know!

**Your Team:** Cheshunt Crew  
**Join Code:** 256BFA9A  
**Current Members:** 3
