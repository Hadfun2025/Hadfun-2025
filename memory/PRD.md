# HADfun Predictor - Football Prediction App

## Original Problem Statement
A full-stack football prediction application where users can predict match results from various leagues around the world. The app includes a new leaderboard system (3 points for sole winner, 1 point for ties), support for FA Cup and World Cup 2026, and an admin analytics dashboard.

## Current Tech Stack
- **Frontend:** React + Tailwind CSS + Shadcn/UI + Recharts
- **Backend:** FastAPI (Python)
- **Database:** MongoDB

## What's Been Implemented

### Core Features
- User authentication (username/email login)
- Multi-league support (Premier League, FA Cup, World Cup, etc.)
- Match predictions (Home/Away/Draw)
- Real-time fixture updates via API-Football
- Team management and leaderboards
- Weekly pot competitions

### Recent Additions (January 2026)
- **POSTPONED Match Status:** UI now correctly displays "📅 MATCH POSTPONED" for postponed games instead of showing "Predictions locked"
- **3/1 Leaderboard System:** 3 points for matchday's sole winner, 1 point for tied users
- **FA Cup Integration:** Third Round fixtures with manual seeding
- **World Cup 2026 Groups:** Seeded at startup
- **Admin Analytics Dashboard:** DAU, WAU, retention, feature usage metrics
- **Penalty Shootout Handling:** Knockout matches correctly scored

## Key Files
- `/app/backend/server.py` - Monolith backend (6000+ lines, needs refactoring)
- `/app/frontend/src/App.js` - Main frontend component
- `/app/frontend/src/components/AdminDashboard.jsx` - Analytics dashboard
- `/app/frontend/src/components/TeamManagement.jsx` - Team/leaderboard views

## Completed Tasks This Session
- ✅ Added `isPostponed` status check in frontend
- ✅ Added POSTPONED UI component with gray styling
- ✅ Updated Salford City vs Swindon Town fixture to POSTPONED status
- ✅ Disabled prediction buttons for postponed matches
- ✅ Updated conditional display logic to exclude postponed from "Predictions locked" message

## Pending Issues
1. **FA Cup Score Automation (P1):** API-Football integration unreliable for manually-seeded fixtures
2. **Admin Dashboard Button Visibility (P2):** May be hidden behind other elements

## Upcoming Tasks
1. **Refactor server.py (P1):** Break 6000+ line monolith into modules:
   - `/app/backend/routes/` - API endpoints
   - `/app/backend/services/` - Business logic
   - `/app/backend/data/` - Seeding data
2. **Investigate Score Update Interval (P2):** Check why scores update instantly vs. every 2 minutes

## Future/Backlog
- Admin Score Update UI for manual score management
- Improved FA Cup API integration

## API Endpoints
- `GET /api/fixtures?league_ids=45` - Get fixtures by league
- `GET /api/teams/{team_id}/leaderboard_v2` - New leaderboard
- `GET /api/admin/seed-fa-cup` - Manual FA Cup seeding
- `GET /api/admin/analytics/*` - Analytics endpoints

## Database Collections
- `fixtures` - Match data (includes `status`, `penalty_winner`)
- `predictions` - User predictions
- `users` - User accounts
- `teams` - Team groups
- `user_league_points` - Leaderboard points
- `world_cup_groups` - World Cup group data

## Known Constraints
- Separate databases for preview/production environments
- User self-deploys via "Re-Deploy" button
- Post-deployment may require visiting admin seeding URLs
