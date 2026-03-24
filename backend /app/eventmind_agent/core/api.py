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

    # -------------------- Существующие методы --------------------

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
            # events = []  # здесь нужно получать реальные события из Odoo
            events = []  # заглушка
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
            # Синхронизируем с календарём
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
            events = []  # заглушка
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
                    'groups_id': [(6, 0, [1])]  # группа Internal User
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
        # В реальном приложении нужно проверять токен
        return {'success': False, 'error': 'Not implemented'}

    def update_user_profile(self, user_id: int, name: str = None, interests: List[str] = None) -> Dict:
        try:
            if interests is not None:
                self.recommender.update_user_profile(user_id, interests)
                calendar = get_user_calendar(user_id)
                calendar.set_interests(interests)
            return {'success': True, 'message': 'Profile updated'}
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            return {'success': False, 'error': str(e)}

    # -------------------- Новые методы для расписания --------------------

    def add_busy_slot(self, user_id: int, start: str, end: str, title: str) -> Dict:
        """Добавить занятое время в календарь"""
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
        """Получить расписание пользователя на неделю"""
        try:
            calendar = get_user_calendar(user_id)
            start = datetime.fromisoformat(start_date)
            schedule = calendar.get_week_schedule(start)
            return {'success': True, 'data': schedule}
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return {'success': False, 'error': str(e)}

    def get_recommendations_with_schedule(self, user_id: int, limit: int = 10) -> Dict:
        """
        Рекомендации с учётом свободного времени
        """
        try:
            # Здесь нужно получить реальные события из Odoo
            events = []  # заглушка
            if not events:
                return {'success': True, 'data': [], 'message': 'No events available'}

            calendar = get_user_calendar(user_id)
            scored = []
            for event in events:
                event_date = datetime.fromisoformat(event.get('date_begin', '').replace('Z', '+00:00'))
                # Проверка доступности
                available = calendar.is_available(event_date, duration_hours=2)
                # Базовая релевантность (можно использовать рекомендации)
                relevance = 0.5  # заглушка
                score = relevance * 0.6 + (1.0 if available else 0.0) * 0.4
                if score > 0:
                    scored.append({
                        'event': event,
                        'score': score,
                        'available': available
                    })
            scored.sort(key=lambda x: -x['score'])
            return {
                'success': True,
                'data': scored[:limit],
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
        # Новые действия для расписания
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
            return self.get_recommendations_with_schedule(
                user_id=request_data.get('user_id'),
                limit=request_data.get('limit', 10)
            )
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}


_api_instance = None

def get_api() -> AgentAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = AgentAPI()
    return _api_instance
