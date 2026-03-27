# core/recommendations.py

import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from ..scheduler.user_calendar import get_user_calendar

logger = logging.getLogger('EventMind.Recommender')


class Recommender:
    
    def __init__(self):
        """Initialize the recommender"""
        self.user_profiles = {}
        self.event_vectors = {}
        self.interaction_history = defaultdict(list)
        
        logger.info("Recommender initialized")
    
    def get_recommendations(self, 
                           user_id: int, 
                           events: List[Dict], 
                           limit: int = 10,
                           include_explanation: bool = False) -> List[Dict]:
        if not events:
            logger.warning(f"No events to recommend for user {user_id}")
            return []
    
        user_interests = self._get_user_interests(user_id)
        
        if not user_interests:
            logger.info(f"User {user_id} has no interests, returning popular events")
            return self._get_popular_events(events, limit)
        
        scored_events = []
        for event in events:
            score = self._calculate_relevance(event, user_interests)
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
        
        scored_events.sort(key=lambda x: -x['score'])
        logger.info(f"Generated {len(scored_events[:limit])} recommendations for user {user_id}")
        return scored_events[:limit]
    
    def get_recommendations_with_schedule(self, 
                                          user_id: int, 
                                          events: List[Dict], 
                                          limit: int = 10,
                                          include_explanation: bool = False) -> List[Dict]:
        """
        Возвращает рекомендации с учётом занятости пользователя.
        Оценка комбинирует релевантность интересам (60%) и доступность времени (40%).
        """
        if not events:
            logger.warning(f"No events to recommend for user {user_id}")
            return []

        user_interests = self._get_user_interests(user_id)
        calendar = get_user_calendar(user_id)

        scored_events = []
        for event in events:
            # Базовая релевантность
            relevance_score = self._calculate_relevance(event, user_interests)
            if relevance_score <= 0:
                continue

            # Проверка доступности времени
            available = False
            if event.get('date_begin'):
                try:
                    event_date = datetime.fromisoformat(event['date_begin'].replace('Z', '+00:00'))
                    available = calendar.is_available(event_date, duration_hours=2)
                except Exception as e:
                    logger.error(f"Error parsing event date: {e}")
                    available = True

            # Итоговая оценка: 60% релевантность, 40% доступность
            final_score = relevance_score * 0.6 + (1.0 if available else 0.0) * 0.4
            final_score = self._apply_interaction_boost(user_id, event, final_score)

            if final_score > 0:
                result = {
                    'event': event,
                    'score': final_score,
                    'relevance_score': relevance_score,
                    'available': available,
                    'id': event.get('id')
                }
                if include_explanation:
                    result['explanation'] = self._generate_explanation(event, user_interests)
                scored_events.append(result)

        scored_events.sort(key=lambda x: -x['score'])
        logger.info(f"Generated {len(scored_events[:limit])} schedule-aware recommendations for user {user_id}")
        return scored_events[:limit]
    
    def _get_user_interests(self, user_id: int) -> List[str]:
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        return ['Python', 'AI', 'Tech', 'Startup']
    
    def _calculate_relevance(self, event: Dict, user_interests: List[str]) -> float:
        event_tags = self._extract_event_tags(event)
        if not event_tags:
            return 0.0
        
        user_set = set(user_interests)
        event_set = set(event_tags)
        intersection = user_set & event_set
        if not intersection:
            return 0.0
        
        score = len(intersection) / len(user_set)
        boost = 0.1 if any(tag in event.get('name', '').lower() for tag in user_set) else 0.0
        return min(score + boost, 1.0)
    
    def _extract_event_tags(self, event: Dict) -> List[str]:
        tags = event.get('tags', [])
        if not tags and event.get('description'):
            description = event['description'].lower()
            keywords = ['python', 'ai', 'design', 'startup', 'marketing', 'data']
            for kw in keywords:
                if kw in description:
                    tags.append(kw.capitalize())
        return tags
    
    def _apply_interaction_boost(self, user_id: int, event: Dict, base_score: float) -> float:
        interactions = self.interaction_history.get(user_id, [])
        event_tags = set(self._extract_event_tags(event))
        boost = 0.0
        for interaction in interactions:
            if interaction.get('type') == 'view':
                if event_tags & set(interaction.get('tags', [])):
                    boost += 0.05
            elif interaction.get('type') == 'register':
                if event_tags & set(interaction.get('tags', [])):
                    boost += 0.15
        return min(base_score + boost, 1.0)
    
    def _get_popular_events(self, events: List[Dict], limit: int) -> List[Dict]:
        upcoming = sorted(
            events,
            key=lambda e: e.get('date_begin', ''),
            reverse=False
        )[:limit]
        return [{'event': e, 'score': 0.5, 'id': e.get('id')} for e in upcoming]
    
    def _generate_explanation(self, event: Dict, user_interests: List[str]) -> str:
        event_tags = self._extract_event_tags(event)
        matching = set(user_interests) & set(event_tags)
        if matching:
            return f"Matches your interests: {', '.join(matching)}"
        else:
            return "Popular event in your area"
    
    def record_interaction(self, user_id: int, event_id: int, interaction_type: str, tags: List[str] = None):
        self.interaction_history[user_id].append({
            'event_id': event_id,
            'type': interaction_type,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat()
        })
        if len(self.interaction_history[user_id]) > 100:
            self.interaction_history[user_id] = self.interaction_history[user_id][-100:]
        logger.info(f"Recorded {interaction_type} for user {user_id} on event {event_id}")
    
    def update_user_profile(self, user_id: int, interests: List[str]):
        self.user_profiles[user_id] = interests
        logger.info(f"Updated profile for user {user_id}: {interests}")
    
    def get_similar_events(self, event_id: int, events: List[Dict], limit: int = 5) -> List[Dict]:
        source = next((e for e in events if e.get('id') == event_id), None)
        if not source:
            return []
        source_tags = set(self._extract_event_tags(source))
        if not source_tags:
            return []
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
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = Recommender()
    return _recommender_instance
