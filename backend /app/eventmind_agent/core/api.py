# core/api.py

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import xmlrpc.client
import hashlib
import secrets

from .agent_core import get_agent
from .recommendations import get_recommender
from scheduler.user_calendar import get_user_calendar, TimeSlot
from .llm_service import get_llm_service   # исправлено имя

logger = logging.getLogger('EventMind.API')


class AgentAPI:

    def __init__(self):
        self.agent = get_agent()
        self.recommender = get_recommender()
        odoo_config = self.agent.config.get('odoo', {})
        self.odoo_url = odoo_config.get('url', 'http://localhost:8069')
        self.odoo_db = odoo_config.get('db', 'eventmind')
        self.odoo_admin = odoo_config.get('username', 'admin')
        self.odoo_admin_pw = odoo_config.get('password', 'admin')
        logger.info("AgentAPI initialized")

    # -------------------- Вспомогательные методы --------------------

    def _fetch_events_from_odoo(self, date_from: datetime = None, date_to: datetime = None) -> List[Dict]:
        """Загружает события из Odoo через XML-RPC"""
        try:
            common = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")
            uid = common.authenticate(self.odoo_db, self.odoo_admin, self.odoo_admin_pw, {})
            if not uid:
                logger.error("Cannot authenticate to Odoo")
                return []

            models = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
            domain = []
            if date_from:
                domain.append(('date_begin', '>=', date_from.isoformat()))
            if date_to:
                domain.append(('date_begin', '<=', date_to.isoformat()))
            else:
                domain.append(('date_begin', '>=', datetime.now().isoformat()))

            events = models.execute_kw(
                self.odoo_db, uid, self.odoo_admin_pw,
                'event.event', 'search_read',
                [domain],
                {'fields': ['id', 'name', 'date_begin', 'date_end', 'location', 'description', 'tag_ids']}
            )
            # Преобразуем tag_ids в список названий тегов
            for e in events:
                if e.get('tag_ids'):
                    tags = models.execute_kw(self.odoo_db, uid, self.odoo_admin_pw,
                                             'event.tag', 'read', [e['tag_ids']], {'fields': ['name']})
                    e['tags'] = [t['name'] for t in tags]
                else:
                    e['tags'] = []
            return events
        except Exception as e:
            logger.error(f"Failed to fetch events from Odoo: {e}")
            return []

    # -------------------- Основные методы --------------------

    def get_status(self) -> Dict[str, Any]:
        return {
            'success': True,
            'data': self.agent.get_status(),
            'timestamp': datetime.now().isoformat()
        }

    def run_cycle(self, auth_token: Optional[str] = None) -> Dict[str, Any]:
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
        try:
            events = self._fetch_events_from_odoo()
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
            return {'success': False, 'error': str(e), 'timestamp': datetime.now().isoformat()}

    def record_interaction(self,
                           user_id: int,
                           event_id: int,
                           interaction_type: str,
                           tags: Optional[List[str]] = None) -> Dict:
        try:
            self.recommender.record_interaction(
                user_id=user_id,
                event_id=event_id,
                interaction_type=interaction_type,
                tags=tags
            )
            return {
                'success': True,
                'data': {'recorded': True, 'timestamp': datetime.now().isoformat()}
            }
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")
            return {'success': False, 'error': str(e)}

    def update_user_interests(self, user_id: int, interests: List[str]) -> Dict:
        try:
            self.recommender.update_user_profile(user_id, interests)
            calendar = get_user_calendar(user_id)
            calendar.set_interests(interests)
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
            return {'success': False, 'error': str(e)}

    def get_similar_events(self, event_id: int, limit: int = 5) -> Dict:
        try:
            events = self._fetch_events_from_odoo()
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
            return {'success': False, 'error': str(e)}

    # -------------------- Авторизация через Odoo --------------------

    def _get_odoo_connection(self, username: str, password: str):
        try:
            common = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")
            uid = common.authenticate(self.odoo_db, username, password, {})
            if uid:
                models = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
                return {'uid': uid, 'models': models}
            return None
        except Exception as e:
            logger.error(f"Odoo connection error: {e}")
            return None

    def register_user(self, email: str, password: str, name: str = None) -> Dict:
        try:
            admin_conn = self._get_odoo_connection(self.odoo_admin, self.odoo_admin_pw)
            if not admin_conn:
                return {'success': False, 'error': 'Cannot connect to Odoo server'}

            existing = admin_conn['models'].execute_kw(
                self.odoo_db, admin_conn['uid'], self.odoo_admin_pw,
                'res.users', 'search',
                [[['login', '=', email]]]
            )
            if existing:
                return {'success': False, 'error': 'User with this email already exists'}

            partner_id = admin_conn['models'].execute_kw(
                self.odoo_db, admin_conn['uid'], self.odoo_admin_pw,
                'res.partner', 'create', [{
                    'name': name or email.split('@')[0],
                    'email': email,
                }]
            )

            user_id = admin_conn['models'].execute_kw(
                self.odoo_db, admin_conn['uid'], self.odoo_admin_pw,
                'res.users', 'create', [{
                    'name': name or email.split('@')[0],
                    'login': email,
                    'password': password,
                    'email': email,
                    'partner_id': partner_id,
                    'groups_id': [(6, 0, [1])]
                }]
            )

            logger.info(f"New user registered: {email} (ID: {user_id})")
            return {
                'success': True,
                'data': {
                    'user_id': user_id,
                    'email': email,
                    'name': name or email.split('@')[0]
                },
                'message': 'Registration successful'
            }
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'success': False, 'error': str(e)}

    def login_user(self, email: str, password: str) -> Dict:
        try:
            common = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")
            uid = common.authenticate(self.odoo_db, email, password, {})
            if not uid:
                return {'success': False, 'error': 'Invalid email or password'}

            models = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
            user_data = models.execute_kw(
                self.odoo_db, uid, password,
                'res.users', 'read',
                [uid],
                {'fields': ['id', 'name', 'login', 'email', 'partner_id']}
            )

            token = hashlib.sha256(f"{email}:{password}:{secrets.token_hex(16)}".encode()).hexdigest()
            logger.info(f"User logged in: {email} (ID: {uid})")
            return {
                'success': True,
                'data': {
                    'user_id': uid,
                    'email': user_data[0]['login'],
                    'name': user_data[0]['name'],
                    'token': token,
                    'partner_id': user_data[0]['partner_id'][0] if user_data[0]['partner_id'] else None
                }
            }
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'success': False, 'error': str(e)}

    def logout_user(self, token: str) -> Dict:
        logger.info(f"User logged out (token: {token[:10]}...)")
        return {'success': True, 'message': 'Logged out successfully'}

    def get_current_user(self, token: str) -> Dict:
        # Временная заглушка – можно реализовать проверку токена
        return {'success': False, 'error': 'Not implemented'}

    def update_user_profile(self, user_id: int, name: str = None, interests: List[str] = None) -> Dict:
        try:
            if interests is not None:
                self.recommender.update_user_profile(user_id, interests)
                calendar = get_user_calendar(user_id)
                calendar.set_interests(interests)
            # Обновление имени в Odoo можно добавить позже
            return {'success': True, 'message': 'Profile updated'}
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            return {'success': False, 'error': str(e)}

    # -------------------- Профиль пользователя (новый метод) --------------------

    def get_user_profile(self, user_id: int) -> Dict:
        """Получить данные пользователя из Odoo (res.users)"""
        try:
            common = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")
            uid = common.authenticate(self.odoo_db, self.odoo_admin, self.odoo_admin_pw, {})
            if not uid:
                return {'success': False, 'error': 'Cannot authenticate to Odoo'}

            models = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")
            user_data = models.execute_kw(
                self.odoo_db, uid, self.odoo_admin_pw,
                'res.users', 'read',
                [user_id],
                {'fields': ['id', 'name', 'login', 'email', 'partner_id']}
            )
            if user_data:
                return {'success': True, 'data': user_data[0]}
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return {'success': False, 'error': str(e)}

    # -------------------- Расписание и рекомендации с учётом времени --------------------

    def add_busy_slot(self, user_id: int, start: str, end: str, title: str) -> Dict:
        try:
            calendar = get_user_calendar(user_id)
            slot = TimeSlot(
                start=datetime.fromisoformat(start),
                end=datetime.fromisoformat(end),
                title=title
            )
            calendar.add_busy_slot(slot)
            logger.info(f"Added busy slot for user {user_id}: {start} - {end} ({title})")
            return {'success': True, 'message': 'Busy slot added'}
        except Exception as e:
            logger.error(f"Error adding busy slot: {e}")
            return {'success': False, 'error': str(e)}

    def get_schedule(self, user_id: int, start_date: str) -> Dict:
        try:
            calendar = get_user_calendar(user_id)
            start = datetime.fromisoformat(start_date)
            schedule = calendar.get_week_schedule(start)
            return {'success': True, 'data': schedule}
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return {'success': False, 'error': str(e)}

    def get_recommendations_with_schedule(self, user_id: int, limit: int = 10, use_llm: bool = True) -> Dict:
        """
        Возвращает рекомендации с учётом занятости пользователя и генерирует сообщение от ИИ.
        """
        try:
            events = self._fetch_events_from_odoo()
            if not events:
                return {'success': True, 'data': [], 'message': 'No events available'}

            # Получаем рекомендации с релевантностью
            recs = self.recommender.get_recommendations(
                user_id=user_id,
                events=events,
                limit=100,
                include_explanation=True
            )

            calendar = get_user_calendar(user_id)
            scored = []

            for rec in recs:
                event = rec['event']
                relevance = rec['score']

                available = False
                if event.get('date_begin'):
                    try:
                        event_date = datetime.fromisoformat(event['date_begin'].replace('Z', '+00:00'))
                        available = calendar.is_available(event_date, duration_hours=2)
                    except Exception as e:
                        logger.error(f"Error parsing event date: {e}")
                        available = True

                final_score = relevance * 0.6 + (1.0 if available else 0.0) * 0.4
                if final_score > 0 and available:  # Берем только те, где есть свободное время
                    result = {
                        'event': event,
                        'score': final_score,
                        'relevance_score': relevance,
                        'available': available,
                        'id': event.get('id')
                    }
                    if rec.get('explanation'):
                        result['explanation'] = rec['explanation']
                    scored.append(result)

            scored.sort(key=lambda x: -x['score'])
            top_events = scored[:limit]

            # >>> ИНТЕГРАЦИЯ GIGACHAT <<<
            llm_message = None
            if use_llm and top_events:
                llm_service = get_llm_service()
                user_interests = self.recommender._get_user_interests(user_id)
                clean_events = [item['event'] for item in top_events[:3]]
                llm_message = llm_service.generate_personal_advice(user_interests, clean_events)

            return {
                'success': True,
                'data': top_events,
                'ai_advice': llm_message,
                'user_id': user_id
            }
        except Exception as e:
            logger.error(f"Error in recommendations_with_schedule: {e}")
            return {'success': False, 'error': str(e)}

    # -------------------- Единый обработчик запросов --------------------

    def handle_request(self, request_data: Dict) -> Dict:
        action = request_data.get('action')
        if not action:
            return {'success': False, 'error': 'No action specified'}

        logger.info(f"API request: {action}")

        # Существующие действия
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
        # Авторизация
        elif action == 'register':
            return self.register_user(
                email=request_data.get('email'),
                password=request_data.get('password'),
                name=request_data.get('name')
            )
        elif action == 'login':
            return self.login_user(
                email=request_data.get('email'),
                password=request_data.get('password')
            )
        elif action == 'logout':
            return self.logout_user(token=request_data.get('token'))
        elif action == 'current_user':
            return self.get_current_user(token=request_data.get('token'))
        elif action == 'update_profile':
            return self.update_user_profile(
                user_id=request_data.get('user_id'),
                name=request_data.get('name'),
                interests=request_data.get('interests')
            )
        # Профиль пользователя (добавлено)
        elif action == 'get_profile':
            return self.get_user_profile(
                user_id=request_data.get('user_id')
            )
        # Расписание
        elif action == 'add_busy_slot':
            return self.add_busy_slot(
                user_id=request_data.get('user_id'),
                start=request_data.get('start'),
                end=request_data.get('end'),
                title=request_data.get('title', 'Занято')
            )
        elif action == 'get_schedule':
            return self.get_schedule(
                user_id=request_data.get('user_id'),
                start_date=request_data.get('start_date', datetime.now().isoformat())
            )
        elif action == 'recommendations_with_schedule':
            # используем метод с параметром use_llm (по умолчанию True)
            return self.get_recommendations_with_schedule(
                user_id=request_data.get('user_id'),
                limit=request_data.get('limit', 10),
                use_llm=request_data.get('use_llm', True)
            )
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}


_api_instance = None

def get_api() -> AgentAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = AgentAPI()
    return _api_instance
