# core/api.py

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib
import secrets
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
load_dotenv()

from ...services.agent.orchestrator import get_agent
from ...services.recommendations.service import get_recommender
from ...services.calendar.user_calendar import get_user_calendar, TimeSlot
from ...schedule.models import SessionLocal, UserSchedule, UserInterest, User
from ...schedule.services import add_favorite, remove_favorite, get_favorites, add_personal_event
from ...integrations.llm.gigachat_service import get_llm_service
from ...integrations.calendar.ics_generator import get_ics_generator

logger = logging.getLogger('EventMind.API')


class AgentAPI:

    def __init__(self):
        self.agent = get_agent()
        self.recommender = get_recommender()
        self._events_cache = {'timestamp': None, 'data': []}
        logger.info("AgentAPI initialized (PostgreSQL mode)")

    def _sync_calendar(self, user_id: int):
        from datetime import timedelta
        calendar = get_user_calendar(user_id)
        calendar._busy_slots = []
        with SessionLocal() as db:
            schedules = db.query(UserSchedule).filter(UserSchedule.user_id == user_id, UserSchedule.is_personal == True).all()
            for s in schedules:
                if s.personal_start:
                    calendar.add_busy_slot(TimeSlot(
                        start=s.personal_start,
                        end=s.personal_end or s.personal_start + timedelta(hours=2),
                        title=s.personal_title or 'Занято'
                    ))
        return calendar

    # -------------------- Вспомогательные методы --------------------

    def _fetch_events(self, date_from: datetime = None, date_to: datetime = None, force_refresh: bool = False) -> List[Dict]:
        """Загружает события из PostgreSQL (с кэшированием)"""
        now = datetime.now()
        if not force_refresh and not date_from and not date_to:
            if self._events_cache['timestamp'] and (now - self._events_cache['timestamp']).total_seconds() < 300:
                return self._events_cache['data']
        
        database_url = os.getenv("DATABASE_URL")
        logger.info(f"Fetching events from DB. URL present: {bool(database_url)}")
        if not database_url:
            logger.error("DATABASE_URL not found in environment")
            return []

        try:
            conn = psycopg2.connect(database_url)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if date_from:
                query += " AND event_date >= %s"
                params.append(date_from)
            elif not date_to and not force_refresh:
                # По умолчанию: только будущие события
                query += " AND event_date >= %s"
                params.append(now)
            
            if date_to:
                query += " AND event_date <= %s"
                params.append(date_to)
                
            cur.execute(query, params)
            rows = cur.fetchall()
            
            events = []
            for row in rows:
                events.append({
                    'id': row['id'],
                    'name': row['title'],
                    'date_begin': row['event_date'].isoformat() if row['event_date'] else None,
                    'date_end': None,
                    'location': row['location'],
                    'description': row['description'],
                    'tags': row['tags'] or [],
                    'image': row['image_url'],
                    'source': row['source'],
                    'source_url': row['source_url']
                })
                
            cur.close()
            conn.close()
            
            if not date_from and not date_to:
                self._events_cache['timestamp'] = now
                self._events_cache['data'] = events
                
            return events
        except Exception as e:
            logger.error(f"Failed to fetch events from DB: {e}")
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
            events = self._fetch_events()
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
            # Сохраняем в БД
            with SessionLocal() as db:
                # Удаляем старые интересы
                db.query(UserInterest).filter(UserInterest.user_id == user_id).delete()
                # Добавляем новые
                if interests:
                    for interest in interests:
                        db.add(UserInterest(user_id=user_id, interest=interest))
                db.commit()

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
            events = self._fetch_events()
            similar = self.recommender.get_similar_events(
                event_id=event_id,
                events=events,
                limit=limit
            )
            return {
                'success': True,
                'data': {
                    'items': similar,
                    'count': len(similar)
                }
            }
        except Exception as e:
            logger.error(f"Error getting similar events: {e}")
            return {'success': False, 'error': str(e)}

    def get_schedule(self, user_id: int, status: str = 'planned') -> Dict:
        try:
            if user_id is not None:
                user_id = int(user_id)
            
            with SessionLocal() as db:
                schedule_items = db.query(UserSchedule).filter(
                    UserSchedule.user_id == user_id,
                    UserSchedule.status == status
                ).all()
            
            # Нам нужно обогатить данные мероприятий, если это не персональные события
            events = self._fetch_events()
            events_map = {e['id']: e for e in events}
            
            results = []
            for item in schedule_items:
                if not item.is_personal and item.event_id in events_map:
                    event = events_map[item.event_id]
                    results.append({
                        'id': item.id,
                        'event_id': item.event_id,
                        'type': 'platform',
                        'name': event['name'],
                        'start': event['date_begin'],
                        'location': event['location'],
                        'description': event['description'],
                        'status': item.status
                    })
                elif item.is_personal:
                    results.append({
                        'id': item.id,
                        'type': 'personal',
                        'name': item.personal_title,
                        'start': item.personal_start.isoformat() if item.personal_start else None,
                        'end': item.personal_end.isoformat() if item.personal_end else None,
                        'location': item.personal_location,
                        'description': item.personal_description,
                        'status': item.status
                    })
            
            return {'success': True, 'data': results}
        except Exception as e:
            logger.error(f"Error fetching schedule for user {user_id}: {e}")
            return {'success': False, 'error': str(e)}

    def add_platform_event(self, user_id: int, event_id: int) -> Dict:
        try:
            if user_id is not None:
                user_id = int(user_id)
            if event_id is not None:
                event_id = int(event_id)
                
            with SessionLocal() as db:
                # Проверяем, нет ли уже такого события
                existing = db.query(UserSchedule).filter(
                    UserSchedule.user_id == user_id,
                    UserSchedule.event_id == event_id
                ).first()
                
                if existing:
                    return {'success': True, 'message': 'Event already in schedule'}
                
                new_item = UserSchedule(
                    user_id=user_id,
                    event_id=event_id,
                    is_personal=False,
                    status='planned'
                )
                db.add(new_item)
                db.commit()
            return {'success': True}
        except Exception as e:
            logger.error(f"Error adding platform event: {e}")
            return {'success': False, 'error': str(e)}

    def add_personal_event(self, user_id: int, title: str, start: str, end: str = None, description: str = '', location: str = '') -> Dict:
        try:
            if user_id is not None:
                user_id = int(user_id)
            
            # Парсим даты из ISO формата
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00')) if end else None
            
            with SessionLocal() as db:
                new_item = UserSchedule(
                    user_id=user_id,
                    is_personal=True,
                    personal_title=title,
                    personal_start=start_dt,
                    personal_end=end_dt,
                    personal_description=description,
                    personal_location=location,
                    status='planned'
                )
                db.add(new_item)
                db.commit()
            return {'success': True}
        except Exception as e:
            logger.error(f"Error adding personal event: {e}")
            return {'success': False, 'error': str(e)}

    def register_user(self, email: str, password: str, name: str = None, interests: List[str] = None) -> Dict:
        try:
            logger.info(f"--- Direct SQL Registration Start for {email} ---")
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            user_name = name or email.split('@')[0]
            
            # Используем прямое соединение psycopg2 для гарантии записи в Неон
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            cur = conn.cursor()
            
            # 1. Проверяем существование
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                conn.close()
                return {'success': False, 'error': 'Пользователь с таким email уже существует'}
            
            # 2. Создаем пользователя
            cur.execute(
                "INSERT INTO users (email, password_hash, name) VALUES (%s, %s, %s) RETURNING id",
                (email, password_hash, user_name)
            )
            user_id = cur.fetchone()[0]
            logger.info(f"User created via SQL. ID: {user_id}")
            
            # 3. Сохраняем интересы
            if interests:
                for interest in interests:
                    cur.execute(
                        "INSERT INTO user_interests (user_id, interest) VALUES (%s, %s)",
                        (user_id, interest)
                    )
                logger.info(f"Interests saved via SQL for user {user_id}")
            
            conn.commit()
            conn.close()
            
            token = hashlib.sha256(f"{email}:{password}:{secrets.token_hex(16)}".encode()).hexdigest()
            return {
                'success': True,
                'data': {
                    'user_id': user_id,
                    'token': token,
                    'email': email,
                    'name': user_name
                },
                'message': 'Registration successful'
            }
        except Exception as e:
            logger.error(f"CRITICAL SQL ERROR in register_user: {e}")
            return {'success': False, 'error': f"Ошибка базы данных: {str(e)}"}

    def login_user(self, email: str, password: str) -> Dict:
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cur.execute(
                "SELECT id, email, name FROM users WHERE email = %s AND password_hash = %s",
                (email, password_hash)
            )
            user = cur.fetchone()
            conn.close()
            
            if not user:
                return {'success': False, 'error': 'Неверный email или пароль'}
            
            token = secrets.token_hex(16)
            return {
                'success': True,
                'data': {
                    'user_id': user['id'],
                    'token': token,
                    'email': user['email'],
                    'name': user['name']
                }
            }
        except Exception as e:
            logger.error(f"Error logging in via SQL: {e}")
            return {'success': False, 'error': str(e)}

    def get_profile(self, user_id: int) -> Dict:
        try:
            if user_id is not None:
                user_id = int(user_id)
            
            with SessionLocal() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return {'success': False, 'error': 'Пользователь не найден'}
                    
                interests = db.query(UserInterest).filter(UserInterest.user_id == user_id).all()
                interest_list = [i.interest for i in interests]
                
                return {
                    'success': True,
                    'data': {
                        'id': user_id,
                        'user_id': user_id,
                        'name': user.name or 'Пользователь',
                        'email': user.email or '',
                        'interests': interest_list,
                        'friends_count': 0,
                        'avatar': None,
                    }
                }
        except Exception as e:
            logger.error(f"Get profile error: {e}")
            return {'success': False, 'error': str(e)}

    def get_event(self, event_id: int) -> Dict:
        try:
            # Преобразуем event_id к int, если он пришел строкой
            if event_id is not None:
                event_id = int(event_id)
            
            logger.info(f"API Request: get_event for ID {event_id}")
            events = self._fetch_events(force_refresh=True)
            event = next((e for e in events if str(e['id']) == str(event_id)), None)
            
            if event:
                logger.info(f"Event found: {event.get('name')}")
                return {'success': True, 'data': event}
            
            logger.warning(f"Event {event_id} not found among {len(events)} events")
            return {'success': False, 'error': f'Событие с ID {event_id} не найдено'}
        except Exception as e:
            logger.error(f"Error fetching event {event_id}: {e}")
            return {'success': False, 'error': str(e)}

    def get_event_ics(self, event_id: int) -> Dict:
        try:
            event_res = self.get_event(event_id)
            if not event_res['success']:
                return event_res
            
            event = event_res['data']
            ics_gen = get_ics_generator()
            ics_content = ics_gen.generate_ics(event)
            
            return {
                'success': True, 
                'data': {
                    'content': ics_content,
                    'filename': f"event_{event_id}.ics",
                    'content_type': 'text/calendar'
                }
            }
        except Exception as e:
            logger.error(f"Error generating ICS for event {event_id}: {e}")
            return {'success': False, 'error': str(e)}

    def export_ics(self, user_id: int) -> Dict:
        try:
            with SessionLocal() as db:
                fav_ids = get_favorites(db, user_id=user_id)
            events = self._fetch_events()
            fav_events = [e for e in events if e.get('id') in fav_ids]
            
            ics_gen = get_ics_generator()
            ics_content = ics_gen.generate_multi_ics(fav_events)
            
            return {
                'success': True,
                'data': {
                    'content': ics_content,
                    'filename': 'my_schedule.ics',
                    'content_type': 'text/calendar'
                }
            }
        except Exception as e:
            logger.error(f"Error exporting ICS for user {user_id}: {e}")
            return {'success': False, 'error': str(e)}

    def get_events(self, page=1, limit=20, city=None, event_type=None, q=None):
        try:
            events = self._fetch_events(force_refresh=True)

            return {
                "success": True,
                "data": {
                    "items": events,
                    "total": len(events),
                    "page": int(page or 1),
                    "limit": int(limit or 20),
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка загрузки событий: {str(e)}",
            }


    def logout_user(self, token: str) -> Dict:
        logger.info(f"User logged out (token: {token[:10]}...)")
        return {'success': True, 'message': 'Logged out successfully'}

    def ask_ai(self, question: str) -> Dict:
        try:
            # Получаем актуальные события для контекста
            events = self._fetch_events(force_refresh=True)
            llm_service = get_llm_service()
            
            # Передаем вопрос и события в LLM сервис
            answer = llm_service.ask_ai_question(question, events)
            
            return {
                'success': True,
                'data': {
                    'answer': answer
                }
            }
        except Exception as e:
            logger.error(f"Error in ask_ai: {e}")
            return {
                'success': False,
                'error': f"Ошибка AI ассистента: {str(e)}"
            }

    def handle_request(self, request_data: Dict) -> Dict:
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
        elif action == 'get_events':
            return self.get_events(
                page=request_data.get("page", 1),
                limit=request_data.get("limit", 20)
            )
        elif action == 'get_event':
            return self.get_event(request_data.get('event_id'))
        elif action == 'get_event_ics':
            return self.get_event_ics(request_data.get('event_id'))
        elif action == 'export_ics':
            return self.export_ics(request_data.get('user_id'))
        elif action == 'get_profile':
            return self.get_profile(user_id=request_data.get('user_id'))
        elif action == 'login':
            return self.login_user(request_data.get('email'), request_data.get('password'))
        elif action == 'register':
            return self.register_user(
                email=request_data.get('email'),
                password=request_data.get('password'),
                name=request_data.get('name'),
                interests=request_data.get('interests')
            )
        elif action == 'get_favorites':
            user_id = request_data.get('user_id')
            with SessionLocal() as db:
                fav_ids = get_favorites(db, user_id=user_id)
            events = self._fetch_events()
            fav_events = [e for e in events if e.get('id') in fav_ids]
            return {'success': True, 'data': fav_events}
        elif action == 'add_favorite':
            user_id = request_data.get('user_id')
            event_id = request_data.get('event_id')
            with SessionLocal() as db:
                add_favorite(db, user_id=user_id, event_id=event_id)
            return {'success': True}
        elif action == 'remove_favorite':
            user_id = request_data.get('user_id')
            event_id = request_data.get('event_id')
            with SessionLocal() as db:
                remove_favorite(db, user_id=user_id, event_id=event_id)
            return {'success': True}
        elif action == 'get_schedule':
            u_id = request_data.get('user_id')
            # Защита от кривых данных с фронтенда
            if u_id == 'planned' or u_id is None:
                return {'success': False, 'error': 'Invalid user_id'}
            return self.get_schedule(
                user_id=u_id,
                status=request_data.get('status', 'planned')
            )
        elif action == 'add_platform_event':
            return self.add_platform_event(
                user_id=request_data.get('user_id'),
                event_id=request_data.get('event_id')
            )
        elif action == 'add_personal_event':
            return self.add_personal_event(
                user_id=request_data.get('user_id'),
                title=request_data.get('title'),
                start=request_data.get('start'),
                end=request_data.get('end'),
                description=request_data.get('description'),
                location=request_data.get('location')
            )
        elif action == 'ask_ai':
            return self.ask_ai(request_data.get('question'))
        elif action == 'recommendations_with_schedule':
            u_id = request_data.get('user_id')
            if u_id == 'planned' or u_id is None:
                return {'success': False, 'error': 'Invalid user_id'}
            return self.get_recommendations_with_schedule(
                user_id=u_id,
                limit=request_data.get('limit', 10)
            )
        elif action == 'update_interests':
            return self.update_user_interests(
                user_id=request_data.get('user_id'),
                interests=request_data.get('interests')
            )
        
        return {'success': False, 'error': f'Unknown action: {action}'}

        # -------------------- Добавление LLM --------------------

    def get_recommendations_with_schedule(self, user_id: int, limit: int = 10, use_llm: bool = True) -> Dict:
        try:
            if user_id is None:
                return {'success': False, 'error': 'Invalid user_id'}

            user_id = int(user_id)
            limit = int(limit or 10)

            events = self._fetch_events(force_refresh=True)

            if not events:
                return {
                    'success': True,
                    'data': [],
                    'ai_advice': None,
                    'message': 'No events available'
                }

            # Важно: сначала синхронизируем календарь из БД,
            # чтобы recommender видел реальные занятые слоты пользователя.
            self._sync_calendar(user_id)

            recs = self.recommender.get_recommendations_with_schedule(
                user_id=user_id,
                events=events,
                limit=limit,
                include_explanation=True
            )

            llm_message = None

            if use_llm and recs:
                try:
                    llm_service = get_llm_service()
                    user_interests = self.recommender._get_user_interests(user_id)
                    clean_events = [item['event'] for item in recs[:3]]

                    llm_message = llm_service.generate_personal_advice(
                        user_interests,
                        clean_events
                    )
                except Exception as llm_error:
                    logger.error(f"LLM advice error: {llm_error}")
                    llm_message = None

            return {
                'success': True,
                'data': recs,
                'ai_advice': llm_message,
                'user_id': user_id,
                'count': len(recs),
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error in recommendations_with_schedule: {e}")
            return {'success': False, 'error': str(e)}


_api_instance = None

def get_api() -> AgentAPI:
    global _api_instance
    if _api_instance is None:
        _api_instance = AgentAPI()
    return _api_instance
