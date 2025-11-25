# API-Football Setup Guide

## 🎯 Quick Start

Your Football Predictions Platform is ready to go! Currently, it's running with **mock data** so you can test the features immediately.

To get **real fixtures** from Premier League, La Liga, Championship, and more:

## 📋 How to Get Your Free API Key (2 minutes)

### Option 1: API-Football Dashboard (Recommended - No Credit Card Required)

1. **Visit**: https://dashboard.api-football.com/register
2. **Sign up** with your email
3. **Copy your API key** from the dashboard
4. **Add it to your app**:
   - Go to `/app/backend/.env`
   - Replace `YOUR_API_KEY_HERE` with your actual API key
5. **Restart backend**: Run `sudo supervisorctl restart backend`

### Option 2: RapidAPI (Alternative)

1. **Visit**: https://rapidapi.com/api-sports/api/api-football
2. **Sign up** and subscribe to the free tier
3. **Copy your API key**
4. **Add it to** `/app/backend/.env` (replace `YOUR_API_KEY_HERE`)
5. **Restart backend**: `sudo supervisorctl restart backend`

## 💰 Cost Structure

### Free Tier (Perfect for Getting Started)
- **100 requests/day** 
- **10 requests/minute**
- Covers **870+ leagues** worldwide
- No credit card required

### What This Means for Your App
- With smart caching, you can support many users on the free tier
- Fixtures are cached for 1 hour (reduces API calls)
- Perfect for testing and small-scale deployment

### Paid Plans (If You Need More)
- **Pro**: 7,500 requests/day - $15/month
- **Ultra**: 75,000 requests/day - $59/month
- **Mega**: 150,000 requests/day - $99/month

## 🏆 Features Included

### Multiple Leagues Support
✅ Premier League (England)
✅ La Liga (Spain)
✅ Bundesliga (Germany)
✅ Serie A (Italy)
✅ Ligue 1 (France)
✅ Championship (England)
✅ Primeira Liga (Portugal)
✅ Eredivisie (Netherlands)

### Platform Features
✅ User authentication (username-based)
✅ Home/Draw/Away predictions
✅ Real-time fixtures (7 days ahead)
✅ Leaderboard system
✅ Points tracking
✅ User dashboard
✅ Multi-league selection

## 🔧 Current Status

**Backend**: ✅ Running (Port 8001)
**Frontend**: ✅ Running (Port 3000)
**Database**: ✅ MongoDB Connected
**API Mode**: ⚠️ Mock Data (Add API key for real fixtures)

## 📝 Environment Variables

Located at `/app/backend/.env`:

```env
# MongoDB (DO NOT CHANGE)
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"

# CORS (DO NOT CHANGE)
CORS_ORIGINS="*"

# API-Football (UPDATE THIS)
API_FOOTBALL_KEY="YOUR_API_KEY_HERE"  # <-- Add your key here
API_FOOTBALL_HOST="v3.football.api-sports.io"
```

## 🚀 How the App Works

1. **Login/Signup**: Enter username (and email for new accounts)
2. **Select Leagues**: Choose which leagues to follow
3. **View Fixtures**: See upcoming matches for the next 7 days
4. **Make Predictions**: Click Home, Draw, or Away for each match
5. **Track Points**: Earn points for correct predictions
6. **Compete**: Check your rank on the leaderboard

## 📊 API Endpoints

All endpoints use the `/api` prefix:

- `GET /api/leagues` - Get supported leagues
- `GET /api/fixtures` - Get upcoming fixtures
- `POST /api/users` - Create new user
- `GET /api/users/{username}` - Get user details
- `POST /api/predictions` - Submit prediction
- `GET /api/predictions/user/{user_id}` - Get user predictions
- `GET /api/leaderboard` - Get leaderboard

## 🔍 Testing Without API Key

The app includes **mock fixtures** for testing:
- Mock matches from Premier League, La Liga, Bundesliga, Championship
- Realistic team names and matchups
- Proper date formatting
- All features work identically

## 💡 Tips

1. **Start with mock data** to test the app
2. **Get the free API key** when ready for real fixtures
3. **Monitor your API usage** in the dashboard
4. **Cache optimization** is already built-in
5. **Scale up** to paid plans as your user base grows

## 🆘 Need Help?

If you have questions about:
- **API-Football**: Visit their documentation at https://www.api-football.com/documentation-v3
- **This Platform**: Check the Emergent Discord or support
- **Deployment**: Contact Emergent support for deployment help

---

**Next Steps:**
1. Test the app with mock data ✅
2. Get your free API-Football key 🔑
3. Add the key to `.env` file 📝
4. Restart backend 🔄
5. Enjoy real fixtures! 🎉
