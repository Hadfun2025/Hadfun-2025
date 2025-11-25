# Team System - How It Works

## 🎯 Overview

Your app has a **team-based prediction system** where users can join teams, make predictions together, and compete for weekly pots.

---

## 👥 How Team Joining Works

### Method 1: Join Code (Recommended)

**For Team Members:**
1. Login to the app
2. Go to "Team" tab
3. Click "Join a Team"
4. Enter the team's join code
5. Click "Join"
6. You're immediately added to the team

**Join Code Location:**
- Team admin can see the join code in Team Settings
- Can share it via text, WhatsApp, etc.
- No email required

### Method 2: Email Invitation (Currently Not Working)

**Why Email Invitations Don't Work:**
- The email service (Resend API) is configured
- BUT: Emails require the app to be **deployed** to send
- Preview/local environment can't send emails
- The invitation gets recorded but email doesn't send

**What Shows in Database:**
- Invitations are saved but email is `None`
- Status shows "sent" but recipient never receives it

**Solution:**
- ✅ **Use Join Code method instead** (works immediately)
- OR wait until after deployment for emails to work

---

## 📊 Current State: CHESHUNT CREW

**Team Fixed:**
- ✅ Team name: CHESHUNT CREW
- ✅ Current members: 2
  - aysin (info@hadfun.co.uk)
  - pistachios (pistachios@hadfun.co.uk)
- ✅ Member count synced correctly

**What Happened:**
- Previously showed 3 members
- When leaderboard was cleaned, deleted users were removed
- Their IDs remained in team's member list (orphaned)
- Now fixed: Only actual users counted

---

## 🔑 How to Add aysindjemil@yahoo.com to Team

Since you want to add aysindjemil@yahoo.com to CHESHUNT CREW:

### Option A: Share Join Code (Works Now)
1. Go to Team tab in your app
2. Find CHESHUNT CREW's join code
3. Send the join code to aysindjemil@yahoo.com via:
   - Text message
   - WhatsApp
   - Email (manually)
4. They login to hadfun.co.uk
5. They go to Team tab → Join Team → Enter code
6. They're in!

### Option B: After Deployment (Email Will Work)
1. Deploy the app to production (hadfun.co.uk)
2. Send email invitation from Team Settings
3. Recipient gets email with join link
4. They click link and join automatically

---

## 💡 Why Email Didn't Work This Time

**Email Service Requirements:**
- ✅ Resend API key configured
- ✅ Sender email set: noreply@hadfun.co.uk
- ❌ App needs to be deployed (not preview)
- ❌ Preview environment blocks outbound emails

**After Deployment:**
- Emails will work automatically
- No configuration changes needed
- Invitations will be delivered

---

## 🔧 Team Member Count Sync

**Fixed Issues:**
1. ❌ **Before:** Team showed 3 members but only 2 existed
   - Old deleted users still in member list
   
2. ✅ **After:** Team shows 2 members correctly
   - Orphaned member IDs removed
   - Member count field synced with actual members

**How It Works:**
- Each team has a `members` array (user IDs)
- Each team has a `member_count` field
- When users are deleted, their IDs must be removed from all teams
- Both fields must stay in sync

---

## 📋 Team Features

**What Teams Can Do:**
- Make predictions together
- Compete in weekly pots
- Track team leaderboard
- Chat with team members (if implemented)
- Pool entry fees

**Team Roles:**
- **Admin:** Creates team, manages settings, sees join code
- **Members:** Make predictions, see team stats

**Team Limits:**
- Max members: Configurable (default 30)
- Entry fee: Set by admin
- Weekly pot: Pooled from all members

---

## 🎯 Next Steps

**To Add New Members:**
1. **NOW (Before Deployment):** Share join code manually
2. **AFTER Deployment:** Email invitations will work

**To Test Email Invitations:**
1. Deploy the app
2. Go to Team Settings
3. Send invitation to aysindjemil@yahoo.com
4. Check if email arrives

**Current Team Status:**
- CHESHUNT CREW: 2 members (clean & synced)
- Ready for more members via join code
- Ready for deployment

---

## ⚠️ Important Notes

1. **Don't Delete Users Without Cleaning Teams**
   - When deleting users, also remove from teams
   - Otherwise orphaned IDs remain

2. **Email Invitations Only Work After Deployment**
   - Preview = No emails
   - Production = Emails work

3. **Join Code Always Works**
   - No deployment needed
   - Instant joining
   - Recommended method

4. **Database Persists Across Deployments**
   - Teams survive deployments
   - Members stay in teams
   - No need to recreate
