# core/recommendations.py

import logging
from typing import List, Dict, Optional
from datetime import datetime
from collections import defaultdict

from ..calendar.user_calendar import get_user_calendar
from ...schedule.models import SessionLocal, UserInterest, UserInteraction

logger = logging.getLogger('EventMind.Recommender')


class Recommender:
    
    def __init__(self):
        """Initialize the recommender"""
        self.event_vectors = {}
        
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
        
        interactions = self._get_user_interactions(user_id)
        
        scored_events = []
        for event in events:
            score = self._calculate_relevance(event, user_interests)
            score = self._apply_interaction_boost(interactions, event, score)
            
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
    
    def get_recommendations_with_schedule(
        self,
        user_id: int,
        events: List[Dict],
        limit: int = 10,
        include_explanation: bool = False
    ) -> List[Dict]:
        """
        Рекомендации с учётом интересов и занятости пользователя.
        Если точных совпадений по тегам нет, возвращаем популярные будущие события,
        чтобы пользователь не видел пустой блок.
        """
        if not events:
            logger.warning(f"No events to recommend for user {user_id}")
            return []

        user_id = int(user_id)
        limit = int(limit or 10)

        user_interests = self._get_user_interests(user_id)
        calendar = get_user_calendar(user_id)
        interactions = self._get_user_interactions(user_id)

        scored_events = []

        for event in events:
            relevance_score = self._calculate_relevance(event, user_interests)

            if relevance_score <= 0:
                continue

            available = True

            if event.get('date_begin'):
                try:
                    event_date = datetime.fromisoformat(
                        str(event['date_begin']).replace('Z', '+00:00')
                    )

                    if event_date.tzinfo is not None:
                        event_date = event_date.replace(tzinfo=None)

                    available = calendar.is_available(event_date, duration_hours=2)
                except Exception as e:
                    logger.error(f"Error parsing event date: {e}")
                    available = True

            # Не выкидываем полностью занятые события, а просто понижаем их.
            # Так рекомендации не будут пустыми.
            availability_score = 1.0 if available else 0.15
            final_score = relevance_score * 0.75 + availability_score * 0.25
            final_score = self._apply_interaction_boost(interactions, event, final_score)

            result = {
                'event': event,
                'score': float(min(final_score, 1.0)),
                'relevance_score': float(relevance_score),
                'available': available,
                'id': event.get('id'),
            }

            if include_explanation:
                result['explanation'] = self._generate_explanation(event, user_interests)

            scored_events.append(result)

        scored_events.sort(
            key=lambda item: (
                item.get('available', False),
                item.get('score', 0)
            ),
            reverse=True
        )

        if scored_events:
            logger.info(
                f"Generated {len(scored_events[:limit])} schedule-aware recommendations for user {user_id}"
            )
            return scored_events[:limit]

        # Fallback: если интересы есть, но совпадений по тегам нет.
        popular = self._get_popular_events(events, limit)

        for item in popular:
            item['available'] = True
            item['relevance_score'] = 0.0
            if include_explanation:
                item['explanation'] = 'Пока нет точных совпадений по интересам, поэтому показываем ближайшие события.'

        return popular

    def _normalize_tag(self, tag: str) -> str:
        if tag is None:
            return ''

        value = str(tag).strip().lower()

        aliases = {
            'искусственный интеллект': 'ai',
            'ии': 'ai',
            'ai': 'ai',
            'ml': 'ml',
            'machine learning': 'ml',
            'машинное обучение': 'ml',
            'data science': 'data science',
            'данные': 'data science',
            'backend': 'backend',
            'бекенд': 'backend',
            'бэкенд': 'backend',
            'frontend': 'frontend',
            'фронтенд': 'frontend',
            'devops': 'devops',
            'mobile': 'mobile',
            'мобильная разработка': 'mobile',
            'cybersecurity': 'cybersecurity',
            'кибербезопасность': 'cybersecurity',
            'конференция': 'конференция',
            'митап': 'митап',
            'хакатон': 'хакатон',
            'воркшоп': 'воркшоп',
            'it': 'it',
            'tech': 'it',
        }

        return aliases.get(value, value)

    def _get_user_interests(self, user_id: int) -> List[str]:
        with SessionLocal() as db:
            interests = db.query(UserInterest.interest).filter(UserInterest.user_id == user_id).all()
        if interests:
            return [i[0] for i in interests]
        return ['Python', 'AI', 'Tech', 'Startup']
    
    def _calculate_relevance(self, event: Dict, user_interests: List[str]) -> float:
        event_tags = self._extract_event_tags(event)

        if not event_tags:
            return 0.0

        user_set = {
            self._normalize_tag(tag)
            for tag in user_interests
            if self._normalize_tag(tag)
        }

        event_set = {
            self._normalize_tag(tag)
            for tag in event_tags
            if self._normalize_tag(tag)
        }

        if not user_set or not event_set:
            return 0.0

        intersection = user_set & event_set

        text = f"{event.get('name', '')} {event.get('description', '')}".lower()

        text_boost = 0.0
        for tag in user_set:
            if tag and tag in text:
                text_boost += 0.1

        if not intersection and text_boost <= 0:
            return 0.0

        tag_score = len(intersection) / max(len(user_set), 1)

        return min(tag_score + text_boost, 1.0)
    
    def _extract_event_tags(self, event: Dict) -> List[str]:
        raw_tags = event.get('tags') or []

        if isinstance(raw_tags, str):
            raw_tags = [tag.strip() for tag in raw_tags.split(',') if tag.strip()]

        tags = list(raw_tags)

        text = f"{event.get('name', '')} {event.get('description', '')}".lower()

        keyword_map = {
            'python': 'Backend',
            'backend': 'Backend',
            'django': 'Backend',
            'fastapi': 'Backend',
            'frontend': 'Frontend',
            'react': 'Frontend',
            'javascript': 'Frontend',
            'ml': 'ML',
            'machine learning': 'ML',
            'машинное обучение': 'ML',
            'ai': 'AI',
            'gpt': 'AI',
            'нейросет': 'AI',
            'искусственный интеллект': 'AI',
            'data': 'Data Science',
            'данн': 'Data Science',
            'devops': 'DevOps',
            'docker': 'DevOps',
            'kubernetes': 'DevOps',
            'mobile': 'Mobile',
            'android': 'Mobile',
            'ios': 'Mobile',
            'security': 'CyberSecurity',
            'cyber': 'CyberSecurity',
            'кибер': 'CyberSecurity',
            'конференц': 'Конференция',
            'митап': 'Митап',
            'meetup': 'Митап',
            'хакатон': 'Хакатон',
            'hackathon': 'Хакатон',
            'воркшоп': 'Воркшоп',
            'workshop': 'Воркшоп',
            'it': 'IT',
        }

        for keyword, tag in keyword_map.items():
            if keyword in text and tag not in tags:
                tags.append(tag)

        return tags
    
    def _apply_interaction_boost(self, interactions: List[Dict], event: Dict, base_score: float) -> float:
        event_tags = set(self._extract_event_tags(event))
        boost = 0.0
        for interaction in interactions:
            int_tags = set(interaction.get('tags', []))
            if event_tags & int_tags:
                if interaction.get('type') == 'view':
                    boost += 0.05
                elif interaction.get('type') == 'favorite':
                    boost += 0.10
                elif interaction.get('type') == 'register':
                    boost += 0.15
        return min(base_score + boost, 1.0)
    
    def _get_popular_events(self, events: List[Dict], limit: int) -> List[Dict]:
        now = datetime.now()

        future_events = []

        for event in events:
            date_value = event.get('date_begin')

            if not date_value:
                future_events.append(event)
                continue

            try:
                event_date = datetime.fromisoformat(str(date_value).replace('Z', '+00:00'))

                if event_date.tzinfo is not None:
                    event_date = event_date.replace(tzinfo=None)

                if event_date >= now:
                    future_events.append(event)
            except Exception:
                future_events.append(event)

        upcoming = sorted(
            future_events,
            key=lambda e: e.get('date_begin') or ''
        )[:limit]

        return [
            {
                'event': event,
                'score': 0.35,
                'relevance_score': 0.0,
                'available': True,
                'id': event.get('id'),
            }
            for event in upcoming
        ]
    
    def _generate_explanation(self, event: Dict, user_interests: List[str]) -> str:
        event_tags = self._extract_event_tags(event)

        user_set = {
            self._normalize_tag(tag)
            for tag in user_interests
            if self._normalize_tag(tag)
        }

        event_set = {
            self._normalize_tag(tag)
            for tag in event_tags
            if self._normalize_tag(tag)
        }

        matching = user_set & event_set

        if matching:
            return f"Совпадает с вашими интересами: {', '.join(sorted(matching))}"

        return "Рекомендовано как ближайшее актуальное событие."
    
    def _get_user_interactions(self, user_id: int) -> List[Dict]:
        # Взаимодействия временно отключены для упрощения
        return []
    
    def record_interaction(self, user_id: int, event_id: int, interaction_type: str, tags: List[str] = None):
        # Взаимодействия временно отключены для упрощения
        pass
    
    def update_user_profile(self, user_id: int, interests: List[str]):
        with SessionLocal() as db:
            db.query(UserInterest).filter(UserInterest.user_id == user_id).delete()
            for interest in interests:
                db.add(UserInterest(user_id=user_id, interest=interest))
            db.commit()
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
