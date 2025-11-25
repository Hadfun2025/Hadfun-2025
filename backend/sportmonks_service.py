import httpx
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SportmonksService:
    """Backup service for Sportmonks Football API when API-Football lacks 2025 data"""
    
    def __init__(self):
        self.api_token = os.environ.get('SPORTMONKS_API_TOKEN')
        self.base_url = os.environ.get('SPORTMONKS_BASE_URL', 'https://api.sportmonks.com/v3/football')
        self.timeout = 30.0
        
        if not self.api_token:
            logger.warning("SPORTMONKS_API_TOKEN not found - backup service will be disabled")
        
    async def is_available(self) -> bool:
        """Check if Sportmonks API is available and configured"""
        return bool(self.api_token)
    
    async def get_fixtures_by_date(self, date: str, league_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch fixtures for a specific date from Sportmonks API
        
        Args:
            date: Date in YYYY-MM-DD format
            league_id: Optional league ID to filter fixtures (8 for Premier League)
            
        Returns:
            List of fixture dictionaries in API-Football compatible format
        """
        if not await self.is_available():
            logger.error("Sportmonks API not available - missing token")
            return []
            
        try:
            # Map common league IDs (API-Football -> Sportmonks)
            league_mapping = {
                39: 8,      # Premier League
                140: 207,   # La Liga  
                78: 82,     # Bundesliga
                135: 384,   # Serie A
                61: 301,    # Ligue 1
            }
            
            sportmonks_league_id = league_mapping.get(league_id, league_id) if league_id else None
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                endpoint = f"{self.base_url}/fixtures/date/{date}"
                params = {"api_token": self.api_token}
                
                if sportmonks_league_id:
                    params["filters"] = f"fixtureLeagues:{sportmonks_league_id}"
                
                logger.info(f"Fetching Sportmonks fixtures for {date}, league: {sportmonks_league_id}")
                
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get('data'):
                    logger.info(f"No Sportmonks fixtures found for {date}")
                    return []
                
                # Convert Sportmonks format to API-Football compatible format
                converted_fixtures = []
                for fixture in data['data']:
                    converted_fixture = await self._convert_sportmonks_fixture(fixture)
                    if converted_fixture:
                        converted_fixtures.append(converted_fixture)
                
                logger.info(f"Retrieved {len(converted_fixtures)} fixtures from Sportmonks for {date}")
                return converted_fixtures
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Sportmonks API rate limit exceeded")
            elif e.response.status_code == 401:
                logger.error("Sportmonks API authentication failed - check token")
            else:
                logger.error(f"Sportmonks API error {e.response.status_code}: {e.response.text}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Sportmonks fixtures: {str(e)}")
            return []
    
    async def get_teams_by_league(self, league_id: int) -> List[Dict[str, Any]]:
        """
        Fetch teams for a specific league from Sportmonks API
        
        Args:
            league_id: League ID (API-Football format, will be converted)
            
        Returns:
            List of team dictionaries in API-Football compatible format
        """
        if not await self.is_available():
            return []
            
        try:
            # Map league ID
            league_mapping = {39: 8, 140: 207, 78: 82, 135: 384, 61: 301}
            sportmonks_league_id = league_mapping.get(league_id, league_id)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                endpoint = f"{self.base_url}/teams/seasons/{self._get_current_season_id()}"
                params = {
                    "api_token": self.api_token,
                    "filters": f"teamLeagues:{sportmonks_league_id}"
                }
                
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                teams = []
                
                for team in data.get('data', []):
                    converted_team = {
                        'team': {
                            'id': team.get('id'),
                            'name': team.get('name'),
                            'code': team.get('short_code'),
                            'country': 'England',  # Default for Premier League
                            'founded': team.get('founded'),
                            'national': False,
                            'logo': team.get('image_path')
                        }
                    }
                    teams.append(converted_team)
                
                logger.info(f"Retrieved {len(teams)} teams from Sportmonks for league {league_id}")
                return teams
                
        except Exception as e:
            logger.error(f"Error fetching Sportmonks teams: {str(e)}")
            return []
    
    async def _convert_sportmonks_fixture(self, sportmonks_fixture: Dict) -> Optional[Dict[str, Any]]:
        """
        Convert Sportmonks fixture format to API-Football compatible format
        """
        try:
            # Extract participants (teams)
            participants = sportmonks_fixture.get('participants', [])
            if len(participants) < 2:
                logger.warning(f"Incomplete participants data for fixture {sportmonks_fixture.get('id')}")
                return None
            
            home_team = next((p for p in participants if p.get('meta', {}).get('location') == 'home'), None)
            away_team = next((p for p in participants if p.get('meta', {}).get('location') == 'away'), None)
            
            if not home_team or not away_team:
                home_team = participants[0]
                away_team = participants[1]
            
            # Extract scores
            scores = sportmonks_fixture.get('scores', [])
            home_score = None
            away_score = None
            
            for score in scores:
                if score.get('description') == 'CURRENT' or score.get('type_id') == 1525:  # Full time score
                    participant_id = score.get('participant_id')
                    score_value = score.get('score', {}).get('goals', 0)
                    
                    if participant_id == home_team.get('id'):
                        home_score = score_value
                    elif participant_id == away_team.get('id'):
                        away_score = score_value
            
            # Convert status
            state_id = sportmonks_fixture.get('state_id', 1)
            status = 'FINISHED' if state_id == 5 else ('LIVE' if state_id in [3, 4] else 'SCHEDULED')
            
            # Map league ID back to API-Football format
            league_mapping = {8: 39, 207: 140, 82: 78, 384: 135, 301: 61}
            original_league_id = league_mapping.get(sportmonks_fixture.get('league_id'), sportmonks_fixture.get('league_id'))
            
            converted = {
                'fixture': {
                    'id': sportmonks_fixture.get('id'),
                    'referee': None,
                    'timezone': 'UTC',
                    'date': sportmonks_fixture.get('starting_at'),
                    'timestamp': sportmonks_fixture.get('starting_at_timestamp'),
                    'periods': {
                        'first': None,
                        'second': None
                    },
                    'venue': {
                        'id': sportmonks_fixture.get('venue_id'),
                        'name': None,
                        'city': None
                    },
                    'status': {
                        'long': status,
                        'short': status[0] if status else 'S',
                        'elapsed': None
                    }
                },
                'league': {
                    'id': original_league_id,
                    'name': 'Premier League' if original_league_id == 39 else 'Unknown',
                    'country': 'England',
                    'logo': None,
                    'flag': None,
                    'season': 2025,
                    'round': f"Regular Season - {sportmonks_fixture.get('round_id', 1)}"
                },
                'teams': {
                    'home': {
                        'id': home_team.get('id'),
                        'name': home_team.get('name'),
                        'logo': home_team.get('image_path'),
                        'winner': None if home_score is None or away_score is None else home_score > away_score
                    },
                    'away': {
                        'id': away_team.get('id'),
                        'name': away_team.get('name'),
                        'logo': away_team.get('image_path'),
                        'winner': None if home_score is None or away_score is None else away_score > home_score
                    }
                },
                'goals': {
                    'home': home_score,
                    'away': away_score
                },
                'score': {
                    'fulltime': {
                        'home': home_score,
                        'away': away_score
                    },
                    'halftime': {
                        'home': None,
                        'away': None
                    },
                    'extratime': {
                        'home': None,
                        'away': None
                    },
                    'penalty': {
                        'home': None,
                        'away': None
                    }
                }
            }
            
            return converted
            
        except Exception as e:
            logger.error(f"Error converting Sportmonks fixture: {str(e)}")
            return None
    
    def _get_current_season_id(self) -> int:
        """Get current season ID for Sportmonks (2025-26 season)"""
        return 21646  # Sportmonks season ID for 2025-26

    async def test_connection(self) -> Dict[str, Any]:
        """Test Sportmonks API connection and return status"""
        if not await self.is_available():
            return {"status": "unavailable", "reason": "No API token configured"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                endpoint = f"{self.base_url}/leagues"
                params = {
                    "api_token": self.api_token,
                    "per_page": 1
                }
                
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                return {
                    "status": "connected",
                    "api_calls_remaining": data.get('meta', {}).get('plan', {}).get('requests_left'),
                    "rate_limit": data.get('meta', {}).get('rate_limit')
                }
                
        except Exception as e:
            return {
                "status": "error",
                "reason": str(e)
            }