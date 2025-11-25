import httpx
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FootballDataService:
    """Service for interacting with Football-Data.org API"""
    
    def __init__(self):
        self.api_key = os.environ.get('FOOTBALL_DATA_KEY', 'YOUR_FOOTBALL_DATA_KEY')
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            'X-Auth-Token': self.api_key
        }
        self.timeout = 10.0
        
        # Competition codes for Football-Data.org
        self.competition_codes = {
            39: 'PL',      # Premier League
            140: 'PD',     # La Liga (Primera Division)
            78: 'BL1',     # Bundesliga
            135: 'SA',     # Serie A
            61: 'FL1',     # Ligue 1
            40: 'ELC',     # Championship (English League Championship)
            94: 'PPL',     # Primeira Liga
            88: 'DED',     # Eredivisie
        }
    
    def get_competition_code(self, league_id: int) -> Optional[str]:
        """Get Football-Data.org competition code from our league ID"""
        return self.competition_codes.get(league_id)
    
    async def get_fixtures_by_competition(
        self, 
        competition_code: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch fixtures for a specific competition
        Args:
            competition_code: Competition code (e.g., 'PL' for Premier League)
            date_from: Optional start date in YYYY-MM-DD format
            date_to: Optional end date in YYYY-MM-DD format
        """
        try:
            params = {}
            if date_from:
                params['dateFrom'] = date_from
            if date_to:
                params['dateTo'] = date_to
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/competitions/{competition_code}/matches",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                return data.get('matches', [])
        except Exception as e:
            logger.error(f"Error fetching fixtures for {competition_code}: {str(e)}")
            return []
    
    async def get_upcoming_fixtures(
        self, 
        league_ids: List[int], 
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Fetch upcoming fixtures for multiple leagues
        Args:
            league_ids: List of our league IDs
            days_ahead: Number of days to look ahead (default: 7)
        """
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)
        
        date_from = today.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
        
        all_fixtures = []
        
        for league_id in league_ids:
            comp_code = self.get_competition_code(league_id)
            if not comp_code:
                logger.warning(f"No competition code for league ID {league_id}")
                continue
            
            fixtures = await self.get_fixtures_by_competition(
                comp_code, 
                date_from=date_from, 
                date_to=date_to
            )
            
            # Add league_id to each fixture for our internal tracking
            for fixture in fixtures:
                fixture['league_id'] = league_id
                fixture['league_code'] = comp_code
            
            all_fixtures.extend(fixtures)
        
        # Filter only scheduled/upcoming fixtures
        upcoming = [
            f for f in all_fixtures 
            if f.get('status') in ['SCHEDULED', 'TIMED', 'IN_PLAY', 'PAUSED']
        ]
        
        # Sort by date
        upcoming.sort(key=lambda x: x.get('utcDate', ''))
        
        return upcoming
    
    def transform_to_standard_format(self, fixtures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform Football-Data.org format to our standard format
        """
        # Friendly name mappings for leagues with country labels
        league_name_map = {
            'Primera Division': 'La Liga (Spain)',
            'Primeira Liga': 'Primeira Liga (Portugal)',
            'Bundesliga': 'Bundesliga (Germany)',
            'Premier League': 'Premier League (England)',
            'Serie A': 'Serie A (Italy)',
            'Ligue 1': 'Ligue 1 (France)',
            'Championship': 'Championship (England)',
            'Eredivisie': 'Eredivisie (Holland)'
        }
        
        result = []
        
        for f in fixtures:
            home_team = f.get('homeTeam', {})
            away_team = f.get('awayTeam', {})
            competition = f.get('competition', {})
            score = f.get('score', {}).get('fullTime', {})
            season = f.get('season', {})
            
            # Extract matchday/round information
            matchday = f.get('matchday') or season.get('currentMatchday', None)
            
            # Get friendly league name
            api_league_name = competition.get('name', 'Unknown')
            friendly_league_name = league_name_map.get(api_league_name, api_league_name)
            
            result.append({
                'fixture_id': f.get('id'),
                'league_id': f.get('league_id'),
                'league_name': friendly_league_name,
                'home_team': home_team.get('name', 'Unknown'),
                'away_team': away_team.get('name', 'Unknown'),
                'home_logo': home_team.get('crest'),
                'away_logo': away_team.get('crest'),
                'match_date': f.get('utcDate'),
                'status': f.get('status'),
                'home_score': score.get('home'),
                'away_score': score.get('away'),
                'matchday': matchday,  # Add matchday information
            })
        
        return result
