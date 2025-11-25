import httpx
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Import the Sportmonks backup service
try:
    from .sportmonks_service import SportmonksService
    SPORTMONKS_AVAILABLE = True
    logger.info("Sportmonks backup service available")
except ImportError:
    try:
        from sportmonks_service import SportmonksService
        SPORTMONKS_AVAILABLE = True
        logger.info("Sportmonks backup service available (fallback import)")
    except ImportError:
        SPORTMONKS_AVAILABLE = False
        SportmonksService = None
        logger.warning("Sportmonks backup service not available")


class APIFootballService:
    """Service for interacting with API-Football API with Sportmonks backup"""
    
    def __init__(self):
        self.api_key = os.environ.get('API_FOOTBALL_KEY', 'YOUR_API_KEY_HERE')
        self.api_host = os.environ.get('API_FOOTBALL_HOST', 'v3.football.api-sports.io')
        self.base_url = f"https://{self.api_host}"
        self.headers = {
            'x-apisports-key': self.api_key
        }
        self.timeout = 10.0
        
        # Initialize Sportmonks backup service
        self.sportmonks_service = SportmonksService() if SPORTMONKS_AVAILABLE else None
        
    async def get_fixtures_by_date(self, date: str, league_id: Optional[int] = None, season: int = 2025) -> List[Dict[str, Any]]:
        """
        Fetch fixtures for a specific date with Sportmonks backup
        Args:
            date: Date in YYYY-MM-DD format
            league_id: Optional league ID to filter fixtures
            season: Season year (default: 2025)
        """
        try:
            params = {'date': date, 'season': season, 'timezone': 'Europe/London'}
            if league_id:
                params['league'] = league_id
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/fixtures",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('errors') and len(data['errors']) > 0:
                    logger.error(f"API-Football errors: {data['errors']}")
                    # Try Sportmonks backup for 2025 season data
                    if season == 2025 and self.sportmonks_service:
                        logger.info(f"API-Football failed for 2025 season, trying Sportmonks backup for {date}")
                        return await self.sportmonks_service.get_fixtures_by_date(date, league_id)
                    return []
                
                fixtures = data.get('response', [])
                
                # If no fixtures found for 2025 season, try Sportmonks backup
                if not fixtures and season == 2025 and self.sportmonks_service:
                    logger.info(f"No fixtures from API-Football for 2025 season on {date}, trying Sportmonks backup")
                    sportmonks_fixtures = await self.sportmonks_service.get_fixtures_by_date(date, league_id)
                    if sportmonks_fixtures:
                        logger.info(f"Retrieved {len(sportmonks_fixtures)} fixtures from Sportmonks backup")
                        return sportmonks_fixtures
                
                return fixtures
                
        except Exception as e:
            logger.error(f"Error fetching fixtures from API-Football: {str(e)}")
            # Try Sportmonks backup if primary API fails for 2025 season
            if season == 2025 and self.sportmonks_service:
                logger.info(f"API-Football failed with error, trying Sportmonks backup for {date}")
                try:
                    return await self.sportmonks_service.get_fixtures_by_date(date, league_id)
                except Exception as backup_error:
                    logger.error(f"Sportmonks backup also failed: {str(backup_error)}")
            return []
    
    async def get_fixtures_by_league_and_season(
        self, 
        league_id: int, 
        season: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch fixtures for a specific league and season
        Args:
            league_id: League ID
            season: Season year (e.g., 2024 for 2024-2025 season)
            from_date: Optional start date in YYYY-MM-DD format
            to_date: Optional end date in YYYY-MM-DD format
        """
        try:
            params = {
                'league': league_id,
                'season': season
            }
            if from_date:
                params['from'] = from_date
            if to_date:
                params['to'] = to_date
                
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/fixtures",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('errors') and len(data['errors']) > 0:
                    logger.error(f"API-Football errors: {data['errors']}")
                    return []
                    
                return data.get('response', [])
        except Exception as e:
            logger.error(f"Error fetching fixtures for league {league_id}: {str(e)}")
            return []
    
    async def get_upcoming_fixtures(
        self, 
        league_ids: List[int], 
        days_ahead: int = 7  # Paid plan allows more days
    ) -> List[Dict[str, Any]]:
        """
        Fetch upcoming fixtures for multiple leagues
        Args:
            league_ids: List of league IDs
            days_ahead: Number of days to look ahead (increased for paid plan)
        """
        # Paid plan: fetch last 3 days and next days for comprehensive coverage
        today = datetime.now().date()
        start_date = today - timedelta(days=3)  # Last 3 days to catch finished matches
        end_date = today + timedelta(days=days_ahead)
        
        all_fixtures = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Fetch fixtures for all leagues on this date
            for league_id in league_ids:
                # Use 2025 for the 2025 season
                fixtures = await self.get_fixtures_by_date(date_str, league_id, season=2025)
                all_fixtures.extend(fixtures)
            
            current_date += timedelta(days=1)
        
        # Filter only upcoming and live fixtures (NS - Not Started, LIVE statuses)
        upcoming = [f for f in all_fixtures if f.get('fixture', {}).get('status', {}).get('short') in ['NS', '1H', '2H', 'HT', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE']]
        
        # Sort by date
        upcoming.sort(key=lambda x: x.get('fixture', {}).get('date', ''))
        
        return upcoming
    
    def transform_to_standard_format(self, fixtures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform API-Football format to our standard format
        """
        # Friendly name mappings for leagues with country labels
        league_name_map = {
            'Primera Division': 'La Liga (Spain)',
            'Primeira Liga': 'Primeira Liga (Portugal)',
            'Bundesliga': 'Bundesliga (Germany)',
            'Premier League': 'Premier League (England)',
            'Serie A': 'Serie A (Italy)',  # Italian Serie A
            'Ligue 1': 'Ligue 1 (France)',
            'Championship': 'Championship (England)',
            'Eredivisie': 'Eredivisie (Holland)',
            'Premiership': 'Scottish Premiership (Scotland)',
            'Super Lig': 'Süper Lig (Turkey)',
            'MLS': 'MLS (USA)',
            'Brasileirao': 'Brasileirão (Brazil)',  # Brazilian league
            'Primera A': 'Liga BetPlay (Colombia)'
        }
        
        result = []
        
        for f in fixtures:
            fixture = f.get('fixture', {})
            teams = f.get('teams', {})
            league = f.get('league', {})
            goals = f.get('goals', {})
            
            home_team = teams.get('home', {})
            away_team = teams.get('away', {})
            
            # Map API-Football status to our standard status
            api_status = fixture.get('status', {}).get('short', 'NS')
            if api_status in ['FT', 'AET', 'PEN']:
                status = 'FINISHED'
            elif api_status in ['1H', '2H', 'HT', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE']:
                status = 'IN_PLAY'
            elif api_status == 'NS':
                status = 'SCHEDULED'
            else:
                status = 'SCHEDULED'
            
            # Get friendly league name with league_id fallback for conflicts
            api_league_name = league.get('name', 'Unknown')
            league_id = league.get('id')
            
            # Handle naming conflicts by checking league_id
            if api_league_name == 'Serie A' and league_id == 71:
                # Brazilian Serie A
                friendly_league_name = 'Brasileirão (Brazil)'
            elif api_league_name == 'Serie A' and league_id == 135:
                # Italian Serie A
                friendly_league_name = 'Serie A (Italy)'
            else:
                # Use name mapping for other leagues
                friendly_league_name = league_name_map.get(api_league_name, api_league_name)
            
            result.append({
                'fixture_id': fixture.get('id'),
                'league_id': league.get('id'),
                'league_name': friendly_league_name,
                'home_team': home_team.get('name', 'Unknown'),
                'away_team': away_team.get('name', 'Unknown'),
                'home_logo': home_team.get('logo'),
                'away_logo': away_team.get('logo'),
                'match_date': fixture.get('date'),
                'status': status,
                'home_score': goals.get('home'),
                'away_score': goals.get('away'),
                'matchday': league.get('round', '').replace('Regular Season - ', ''),
            })
        
        return result
    
    async def get_league_standings(self, league_id: int, season: int = 2025) -> Dict[str, Any]:
        """
        Fetch current league standings/table
        Args:
            league_id: ID of the league
            season: Season year (default: 2025)
        Returns:
            Dictionary with league standings data
        """
        try:
            params = {'league': league_id, 'season': season}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/standings",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get('errors') and len(data['errors']) > 0:
                    logger.error(f"API-Football standings errors: {data['errors']}")
                    return {}
                
                return data.get('response', [])
        except Exception as e:
            logger.error(f"Error fetching league standings for league {league_id}: {str(e)}")
            return {}
