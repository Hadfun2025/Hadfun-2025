# API-Football Integration Guide

## Status: ✅ READY FOR ACTIVATION

The API-Football service has been fully integrated and is ready to use. Currently using Football-Data.org due to free plan limitations.

## Quick Switch Instructions

To activate API-Football for faster, real-time updates:

### 1. Get API-Football Paid Plan
- Visit: https://www.api-football.com/pricing
- Subscribe to Basic plan or higher (supports current season)

### 2. Update Environment Variables
```bash
# Add to .env file
API_FOOTBALL_KEY=your_paid_api_key_here
API_FOOTBALL_HOST=v3.football.api-sports.io
```

### 3. Switch Active Service
In `/app/backend/server.py`, update the `get_active_football_service()` function:

```python
def get_active_football_service():
    """
    Returns the active football service for fetching fixtures and results.
    Switch to api_football when paid plan is available for faster updates.
    """
    # Switch this line when API-Football paid plan is ready:
    return api_football  # <-- Change from football_data to api_football
```

### 4. Restart Backend
```bash
sudo supervisorctl restart backend
```

## Benefits of API-Football vs Football-Data.org

| Feature | Football-Data.org | API-Football |
|---------|------------------|--------------|
| Update Speed | ~30 min delay | Real-time |
| Match Results | Delayed | Immediate |
| Free Plan | ✅ Current season | ❌ Only 2021-2023 |
| Paid Plan | Limited features | Full real-time |
| Rate Limits | 10 calls/min | 100+ calls/min |

## Current Implementation

- ✅ **APIFootballService** class implemented
- ✅ **transform_to_standard_format()** method added
- ✅ **get_upcoming_fixtures()** method ready
- ✅ **Helper function** for easy switching
- ✅ **Error handling** for API limitations
- ✅ **Automated result checker** ready to use either service

## Testing

Run the integration test:
```bash
cd /app/backend
python test_integration.py
```

## Troubleshooting

### Free Plan Limitations
If you see errors like "Free plans do not have access to this season":
- This is expected with free API-Football plan
- System automatically falls back to Football-Data.org
- Upgrade to paid plan to access current season

### Switching Back
To revert to Football-Data.org:
```python
return football_data  # In get_active_football_service()
```

## Impact on Aysin's Predictions

Once switched to API-Football:
- ✅ **Weekend match results will be scored IMMEDIATELY**
- ✅ **Automated checker (every 15 mins) will catch results in real-time**
- ✅ **Leaderboard will update within 15 minutes of match finish**
- ✅ **No more waiting for delayed Football-Data.org updates**

The 12 pending predictions from this weekend will be scored as soon as API-Football is activated and the next automated check runs.