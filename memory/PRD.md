# HADFUN Predictor - Product Requirements Document

## Original Problem Statement
Football prediction app (hadfun.co.uk) that allows users to:
- Predict match results from leagues around the world
- Compete with team members on leaderboards
- View World Cup 2026 tournament groups and fixtures
- Participate in community features

## Core Requirements
1. **Stable deployment** - Environment variables correctly loaded with `load_dotenv(override=False)`
2. **Team Leaderboards** - Per-league leaderboards with new scoring system
3. **World Cup 2026** - Display 48-team tournament groups (A-L)
4. **Match predictions** - Users can predict Home/Away/Draw for fixtures
5. **Community features** - Team chat, community feed, image sharing

## Scoring System (Implemented)
- **3 points** - Sole winner of matchday (most correct predictions alone)
- **1 point each** - Multiple users tie for most correct predictions
- **0 points** - Other participants
- Leaderboards are **per league separately**
- Matchdays tracked individually (16, 17, 18 etc.)

## What's Been Implemented

### Session: January 8, 2026
1. **Critical Deployment Fix** - Already applied from previous session
   - `load_dotenv(override=False)` prevents production env vars being overwritten
   - Database name extracted from MongoDB URL correctly

2. **New Leaderboard Design** - COMPLETED
   - Consolidated table per league showing total points
   - Per-matchday breakdown columns (MD 14, MD 15, etc.)
   - Visual indicators: 3★ for sole winner, 1 for tied winner, - for no win
   - Legend explaining scoring system
   - Backend: `/api/teams/{team_id}/leaderboard/by-league`
   - Frontend: `TeamManagement.jsx` leaderboard tab

3. **World Cup 2026 Groups** - VERIFIED
   - All 12 groups (A-L) with 4 teams each
   - Database: `world_cup_groups` collection
   - API: `/api/world-cup/groups`
   - Frontend: World Cup tab with tournament info

## Test Results
- **Backend Tests**: 20/20 passed (100%)
- **Frontend Tests**: All UI elements verified
- Test file: `/app/tests/test_leaderboard_and_worldcup.py`

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/teams/{team_id}/leaderboard/by-league` | GET | Team leaderboard with matchday scores |
| `/api/world-cup/groups` | GET | World Cup 2026 group stage draw |
| `/api/fixtures` | GET | Match fixtures by league |
| `/api/predictions` | POST | Submit prediction |
| `/api/users/{username}` | GET | User profile |

## Database Collections
- `users` - User accounts
- `teams` - Team information
- `team_members` - Team membership
- `predictions` - User predictions
- `fixtures` - Match fixtures
- `world_cup_groups` - World Cup 2026 groups

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **External APIs**: API-Football for live scores

## Backlog / Future Tasks
1. **P1** - Deploy and verify on production (hadfun.co.uk)
2. **P2** - Recreate missing users (Davidwhu, DavidKaye) and team (Cheshunt Crew) on production
3. **P3** - Investigate live score update rate (apscheduler config)
4. **P4** - Add more matchday fixtures for World Cup 2026
