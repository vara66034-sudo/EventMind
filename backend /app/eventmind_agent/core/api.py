

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .agent_core import get_agent
from .recommendations import get_recommender

logger = logging.getLogger('EventMind.API')


class AgentAPI:

    
    def __init__(self):
        """Initialize API with agent and recommender"""
        self.agent = get_agent()
        self.recommender = get_recommender()
        logger.info("AgentAPI initialized")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status
        
        Returns:
            Dict with agent status and statistics
        """
        return {
            'success': True,
            'data': self.agent.get_status(),
            'timestamp': datetime.now().isoformat()
        }
    
    def run_cycle(self, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Manually trigger agent cycle
        
        Args:
            auth_token: Authentication token (for security)
            
        Returns:
            Dict with cycle results
        """
        # In production, validate auth_token
        logger.info("Manual cycle trigger requested")
        
        result = self.agent.run_cycle()
        
        return {
            'success': result.get('success', False),
            'data': result,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_recommendations(self, 
                           user_id: int, 
                           limit: int = 10,
                           include_explanation: bool = False) -> Dict:
        """
        Get recommendations for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations
            include_explanation: Whether to include explanations
            
        Returns:
            Dict with recommendations
        """
        try:
            # This would typically get events from database
            # For now, return placeholder
            events = []  # Would fetch from Odoo
            
            recommendations = self.recommender.get_recommendations(
                user_id=user_id,
                events=events,
                limit=limit,
                include_explanation=include_explanation
            )
            
            return {
                'success': True,
                'data': {
                    'user_id': user_id,
                    'recommendations': recommendations,
                    'count': len(recommendations),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def record_interaction(self, 
                          user_id: int, 
                          event_id: int, 
                          interaction_type: str,
                          tags: Optional[List[str]] = None) -> Dict:
        """
        Record user interaction for learning
        
        Args:
            user_id: User ID
            event_id: Event ID
            interaction_type: 'view', 'click', 'register', 'ics_download'
            tags: Event tags (optional)
            
        Returns:
            Dict with status
        """
        try:
            self.recommender.record_interaction(
                user_id=user_id,
                event_id=event_id,
                interaction_type=interaction_type,
                tags=tags
            )
            
            return {
                'success': True,
                'data': {
                    'recorded': True,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_user_interests(self, user_id: int, interests: List[str]) -> Dict:
        """
        Update user interests
        
        Args:
            user_id: User ID
            interests: List of interest tags
            
        Returns:
            Dict with status
        """
        try:
            self.recommender.update_user_profile(user_id, interests)
            
            return {
                'success': True,
                'data': {
                    'updated': True,
                    'user_id': user_id,
                    'interests': interests,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating interests: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_similar_events(self, event_id: int, limit: int = 5) -> Dict:
        """
        Get events similar to a given event
        
        Args:
            event_id: Source event ID
            limit: Maximum number of similar events
            
        Returns:
            Dict with similar events
        """
        try:
            # This would fetch events from database
            events = []  # Would fetch from Odoo
            
            similar = self.recommender.get_similar_events(
                event_id=event_id,
                events=events,
                limit=limit
            )
            
            return {
                'success': True,
                'data': {
                    'source_event_id': event_id,
                    'similar_events': similar,
                    'count': len(similar)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting similar events: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_request(self, request_data: Dict) -> Dict:
        """
        Handle incoming API request (unified endpoint)
        
        Args:
            request_data: Request with 'action' and parameters
            
        Returns:
            Response data
        """
        action = request_data.get('action')
        
        if not action:
            return {'success': False, 'error': 'No action specified'}
        
        logger.info(f"API request: {action}")
        
        if action == 'status':
            return self.get_status()
        
        elif action == 'run_cycle':
            return self.run_cycle(request_data.get('auth_token'))
        
        elif action == 'recommendations':
            return self.get_recommendations(
                user_id=request_data.get('user_id'),
                limit=request_data.get('limit', 10),
                include_explanation=request_data.get('include_explanation', False)
            )
        
        elif action == 'interaction':
            return self.record_interaction(
                user_id=request_data.get('user_id'),
                event_id=request_data.get('event_id'),
                interaction_type=request_data.get('type'),
                tags=request_data.get('tags')
            )
        
        elif action == 'update_interests':
            return self.update_user_interests(
                user_id=request_data.get('user_id'),
                interests=request_data.get('interests', [])
            )
        
        elif action == 'similar':
            return self.get_similar_events(
                event_id=request_data.get('event_id'),
                limit=request_data.get('limit', 5)
            )
        
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}


# Global instance
_api_instance = None

def get_api() -> AgentAPI:
    """
    Get or create the global API instance
    
    Returns:
        AgentAPI instance
    """
    global _api_instance
    if _api_instance is None:
        _api_instance = AgentAPI()
    return _api_instance
