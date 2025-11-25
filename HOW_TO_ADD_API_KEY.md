# How to Add API-Football Key for Live Deployment

## Step 1: Get Your Free API Key (2 minutes)

1. Visit: https://dashboard.api-football.com/register
2. Sign up with your email
3. Verify your email
4. Login to dashboard
5. Copy your API key (looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`)

## Step 2: Add Key to Your App

### Option A: Direct File Edit (Easiest)
```bash
# Edit the .env file
nano /app/backend/.env

# Find this line:
API_FOOTBALL_KEY="YOUR_API_KEY_HERE"

# Replace with your actual key:
API_FOOTBALL_KEY="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"

# Save file (Ctrl+X, then Y, then Enter)
```

### Option B: Using Command Line
```bash
# Replace YOUR_ACTUAL_KEY with your key
cd /app/backend
sed -i 's/YOUR_API_KEY_HERE/YOUR_ACTUAL_KEY/g' .env
```

## Step 3: Restart Backend

```bash
sudo supervisorctl restart backend
```

## Step 4: Verify It's Working

```bash
# This should now show REAL fixtures instead of mock data
curl "http://localhost:8001/api/fixtures?league_ids=39&days_ahead=7"
```

You'll know it's working when you see real team logos and actual upcoming fixtures!

## That's It! 🎉

Your app will now fetch real fixtures from:
- ✅ Premier League
- ✅ La Liga  
- ✅ Bundesliga
- ✅ Championship
- ✅ And all other supported leagues

## Free Tier Limits
- 100 requests/day
- 10 requests/minute
- Perfect for small-medium teams
- Built-in caching reduces API usage

## Need More?
Upgrade to Pro plan ($15/month) for 7,500 requests/day directly on API-Football dashboard.
