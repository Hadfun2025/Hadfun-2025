# Production Data Restoration Instructions

## ⚠️ IMPORTANT: Your Data Status

Your production site (hadfun.co.uk) currently has:
- Some users with predictions
- NO Cheshunt Crew team structure
- Missing: Remster, Ayhan, Leeanne

## 🎯 What Needs To Be Restored:

**Cheshunt Crew Team:**
- Join Code: 256BFA9A
- 7 Members total

**Members with Prediction Counts:**
1. aysin - 38 predictions
2. pistachios - 29 predictions
3. aysindjemil - 29 predictions
4. Josh - 29 predictions
5. Remster - 10 predictions (Email: Remie.djemil@gmail.com)
6. Ayhan - 9 predictions (Email: ayhanozgegiet@gmail.com)
7. Leeanne - 0 predictions

## 🔧 Restoration Options:

### Option 1: Contact Emergent Support (RECOMMENDED)
Since you already contacted support and they're investigating, they may be able to:
1. Restore from an automatic backup
2. Run the restoration script directly on production
3. Access production database with proper tools

### Option 2: Manual Restoration via Emergent Dashboard
If Emergent provides database access tools:
1. Access your production MongoDB
2. Run the restoration script: `/app/backend/restore_to_production.py`

### Option 3: Add Restoration Endpoint Properly
1. Make sure the emergency endpoint code in server.py is committed
2. Deploy again
3. Call: POST https://hadfun.co.uk/api/emergency/restore-cheshunt-crew

## 📞 Next Steps:

1. **Wait for Support Response** - They may restore everything automatically
2. **If Support Can't Help** - Contact me and I'll help you run the script manually
3. **Check Production** - Visit https://hadfun.co.uk and verify if Cheshunt Crew appears

## 🔍 How To Verify Restoration:

Check these URLs:
- https://hadfun.co.uk/api/teams (should show Cheshunt Crew)
- https://hadfun.co.uk/api/leaderboard (should show all 7 members)

## ⏰ Timeline:

Your weekend matches are coming up. Priority is getting the team and predictions restored ASAP.

---

**Current Time:** You've deployed the latest code with all improvements.
**Status:** Waiting for database restoration to complete.
