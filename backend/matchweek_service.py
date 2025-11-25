from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MatchweekService:
    """Service for managing matchweek-based cycles"""
    
    def __init__(self):
        pass
    
    def get_matchweek_from_fixtures(self, fixtures: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group fixtures by matchweek based on the round information
        Returns dict with matchweek as key and fixtures as value
        """
        matchweeks = {}
        
        for fixture in fixtures:
            # Football-Data.org provides 'matchday' or 'season.currentMatchday'
            matchday = fixture.get('matchday') or fixture.get('season', {}).get('currentMatchday', 'Unknown')
            matchweek_key = f"Matchweek {matchday}"
            
            if matchweek_key not in matchweeks:
                matchweeks[matchweek_key] = []
            
            matchweeks[matchweek_key].append(fixture)
        
        return matchweeks
    
    def get_current_matchweek(self, fixtures: List[Dict]) -> Optional[str]:
        """
        Determine the current active matchweek based on fixture dates
        Returns the matchweek that contains today's date or upcoming fixtures
        """
        if not fixtures:
            return None
        
        today = datetime.now(timezone.utc)
        
        # Group by matchweek
        matchweeks = self.get_matchweek_from_fixtures(fixtures)
        
        # Find matchweek that contains today or is upcoming
        for matchweek, week_fixtures in sorted(matchweeks.items()):
            # Get date range for this matchweek
            dates = [datetime.fromisoformat(f.get('utcDate', '').replace('Z', '+00:00')) 
                    for f in week_fixtures if f.get('utcDate')]
            
            if not dates:
                continue
            
            week_start = min(dates)
            week_end = max(dates) + timedelta(hours=3)  # Add 3 hours after last match
            
            # If today is within this matchweek or matchweek is in future
            if week_start <= today <= week_end or week_start > today:
                return matchweek
        
        # Default to first matchweek if none found
        return list(matchweeks.keys())[0] if matchweeks else None
    
    def get_matchweek_info(self, fixtures: List[Dict], matchweek: str) -> Dict:
        """
        Get detailed info about a specific matchweek
        Returns start date, end date, and all fixtures
        """
        matchweeks = self.get_matchweek_from_fixtures(fixtures)
        week_fixtures = matchweeks.get(matchweek, [])
        
        if not week_fixtures:
            return {
                'matchweek': matchweek,
                'start_date': None,
                'end_date': None,
                'fixtures': [],
                'total_matches': 0
            }
        
        # Get date range
        dates = [datetime.fromisoformat(f.get('utcDate', '').replace('Z', '+00:00')) 
                for f in week_fixtures if f.get('utcDate')]
        
        if not dates:
            return {
                'matchweek': matchweek,
                'start_date': None,
                'end_date': None,
                'fixtures': week_fixtures,
                'total_matches': len(week_fixtures)
            }
        
        return {
            'matchweek': matchweek,
            'start_date': min(dates),
            'end_date': max(dates) + timedelta(hours=3),
            'fixtures': week_fixtures,
            'total_matches': len(week_fixtures),
            'first_kickoff': min(dates),
            'last_kickoff': max(dates)
        }
    
    def can_predict(self, match_date_str: str) -> bool:
        """
        Check if predictions are still allowed for this match
        Returns True if match hasn't started yet
        """
        try:
            match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            # Allow predictions up until kickoff
            return now < match_date
        except Exception as e:
            logger.error(f"Error checking prediction time: {str(e)}")
            return False
    
    def get_matchweek_status(self, matchweek_info: Dict) -> str:
        """
        Get status of matchweek: 'upcoming', 'active', or 'completed'
        """
        if not matchweek_info.get('start_date'):
            return 'unknown'
        
        now = datetime.now(timezone.utc)
        start = matchweek_info['start_date']
        end = matchweek_info['end_date']
        
        if now < start:
            return 'upcoming'
        elif start <= now <= end:
            return 'active'
        else:
            return 'completed'
    
    def format_matchweek_dates(self, matchweek_info: Dict) -> str:
        """
        Format matchweek date range for display
        e.g., "Fri 24 Oct - Sun 26 Oct"
        """
        if not matchweek_info.get('start_date'):
            return "Dates TBD"
        
        start = matchweek_info['start_date']
        end = matchweek_info['last_kickoff']
        
        if start.date() == end.date():
            # Same day
            return start.strftime("%a %d %b")
        elif start.month == end.month:
            # Same month
            return f"{start.strftime('%a %d')} - {end.strftime('%a %d %b')}"
        else:
            # Different months
            return f"{start.strftime('%a %d %b')} - {end.strftime('%a %d %b')}"
