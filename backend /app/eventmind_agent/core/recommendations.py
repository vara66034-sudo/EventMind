

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger('EventMind.Recommender')


class Recommender:
    
    def __init__(self):
        """Initialize the recommender"""
        self.user_profiles = {}  # Cache user profiles
        self.event_vectors = {}   # Cache event vectors
        self.interaction_history = defaultdict(list)
        
        logger.info(" Recommender initialized")
    
    def get_recommendations(self, 
                           user_id: int, 
                           events: List[Dict], 
                           limit: int = 10,
                           include_explanation: bool = False) -> List[Dict]:

        if not events:
            logger.warning(f"No events to recommend for user {user_id}")
            return []
        
        # Get user interests
        user_interests = self._get_user_interests(user_id)
        
        if not user_interests:
            # No interests, return popular/upcoming events
            logger.info(f"User {user_id} has no interests, returning popular events")
            return self._get_popular_events(events, limit)
        
        # Score each event
        scored_events = []
        for event in events:
            score = self._calculate_relevance(event, user_interests)
            
            # Boost score based on user's past interactions
            score = self._apply_interaction_boost(user_id, event, score)
            
            if score > 0:
                result = {
                    'event': event,
                    'score': float(score),
                    'id': event.get('id')
                }
                
                if include_explanation:
                    result['explanation'] = self._generate_explanation(event, user_interests)
                
                scored_events.append(result)
        
        # Sort by score descending
        scored_events.sort(key=lambda x: -x['score'])
        
        logger.info(f"Generated {len(scored_events[:limit])} recommendations for user {user_id}")
        
        return scored_events[:limit]
    
    def _get_user_interests(self, user_id: int) -> List[str]:
        """
        Get user interests from storage
        
        This would typically call Odoo API or database
        """
        # Placeholder - in production, fetch from Odoo
        # For demo purposes, return some default interests
        return ['Python', 'AI', 'Tech', 'Startup']
    
    def _calculate_relevance(self, event: Dict, user_interests: List[str]) -> float:
        """
        Calculate relevance score between event and user interests
        
        Uses tag overlap as primary signal
        
        Args:
            event: Event dictionary
            user_interests: List of interest tags
            
        Returns:
            Relevance score (0-1)
        """
        # Extract tags from event
        event_tags = self._extract_event_tags(event)
        
        if not event_tags:
            return 0.0
        
        # Convert to sets for faster computation
        user_set = set(user_interests)
        event_set = set(event_tags)
        
        # Calculate Jaccard similarity
        intersection = user_set & event_set
        if not intersection:
            return 0.0
        
        # Weighted score: more important interests get higher weight
        # For now, simple Jaccard
        score = len(intersection) / len(user_set)
        
        # Boost for exact matches
        boost = 0.1 if any(tag in event['name'].lower() for tag in user_set) else 0.0
        
        return min(score + boost, 1.0)
    
    def _extract_event_tags(self, event: Dict) -> List[str]:
        """
        Extract tags from event
        
        In production, this would use tags from Polina's module
        """
        # Try to get tags from event
        tags = event.get('tags', [])
        
        # If no tags, try to extract from description (simple version)
        if not tags and event.get('description'):
            description = event['description'].lower()
            # Simple keyword matching
            keywords = ['python', 'ai', 'design', 'startup', 'marketing', 'data']
            for kw in keywords:
                if kw in description:
                    tags.append(kw.capitalize())
        
        return tags
    
    def _apply_interaction_boost(self, user_id: int, event: Dict, base_score: float) -> float:
        """
        Boost score based on user's past interactions
        
        Args:
            user_id: User ID
            event: Event dictionary
            base_score: Base relevance score
            
        Returns:
            Boosted score
        """
        interactions = self.interaction_history.get(user_id, [])
        
        # Check if user interacted with similar events
        event_tags = set(self._extract_event_tags(event))
        
        boost = 0.0
        for interaction in interactions:
            if interaction.get('type') == 'view':
                # User viewed similar event - small boost
                if event_tags & set(interaction.get('tags', [])):
                    boost += 0.05
            elif interaction.get('type') == 'register':
                # User registered for similar event - bigger boost
                if event_tags & set(interaction.get('tags', [])):
                    boost += 0.15
        
        return min(base_score + boost, 1.0)
    
    def _get_popular_events(self, events: List[Dict], limit: int) -> List[Dict]:
        """
        Get popular events when user has no interests
        
        Args:
            events: List of events
            limit: Maximum number to return
            
        Returns:
            List of popular events
        """
        # Sort by popularity (registrations count, views, etc.)
        # For now, just return upcoming events
        upcoming = sorted(
            events,
            key=lambda e: e.get('date_begin', ''),
            reverse=False
        )[:limit]
        
        return [{'event': e, 'score': 0.5, 'id': e.get('id')} for e in upcoming]
    
    def _generate_explanation(self, event: Dict, user_interests: List[str]) -> str:
        """
        Generate human-readable explanation for recommendation
        
        Args:
            event: Event dictionary
            user_interests: List of interest tags
            
        Returns:
            Explanation string
        """
        event_tags = self._extract_event_tags(event)
        matching = set(user_interests) & set(event_tags)
        
        if matching:
            return f"Matches your interests: {', '.join(matching)}"
        else:
            return "Popular event in your area"
    
    def record_interaction(self, user_id: int, event_id: int, interaction_type: str, tags: List[str] = None):
        """
        Record user interaction for learning
        
        Args:
            user_id: User ID
            event_id: Event ID
            interaction_type: 'view', 'click', 'register', 'ics_download'
            tags: Event tags (optional)
        """
        self.interaction_history[user_id].append({
            'event_id': event_id,
            'type': interaction_type,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 interactions per user
        if len(self.interaction_history[user_id]) > 100:
            self.interaction_history[user_id] = self.interaction_history[user_id][-100:]
        
        logger.info(f"Recorded {interaction_type} for user {user_id} on event {event_id}")
    
    def update_user_profile(self, user_id: int, interests: List[str]):
        """
        Update user profile with new interests
        
        Args:
            user_id: User ID
            interests: New list of interests
        """
        self.user_profiles[user_id] = interests
        logger.info(f"Updated profile for user {user_id}: {interests}")
    
    def get_similar_events(self, event_id: int, events: List[Dict], limit: int = 5) -> List[Dict]:
        """
        Find events similar to a given event
        
        Args:
            event_id: Source event ID
            events: List of all events
            limit: Maximum number to return
            
        Returns:
            List of similar events
        """
        # Find source event
        source = next((e for e in events if e.get('id') == event_id), None)
        if not source:
            return []
        
        source_tags = set(self._extract_event_tags(source))
        if not source_tags:
            return []
        
        # Score other events
        scored = []
        for event in events:
            if event.get('id') == event_id:
                continue
            
            event_tags = set(self._extract_event_tags(event))
            if not event_tags:
                continue
            
            similarity = len(source_tags & event_tags) / len(source_tags | event_tags)
            if similarity > 0:
                scored.append((event, similarity))
        
        scored.sort(key=lambda x: -x[1])
        return [{'event': e, 'score': s} for e, s in scored[:limit]]


# Global instance
_recommender_instance = None

def get_recommender() -> Recommender:
    """
    Get or create the global recommender instance
    
    Returns:
        Recommender instance
    """
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = Recommender()
    return _recommender_instance
