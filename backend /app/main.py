from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional, List
import logging

from eventmind_agent.core.api import get_api
from eventmind_agent.notifications.ics_generator import get_ics_generator

app = FastAPI(title="EventMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # для разработки, в продакшене ограничить
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- МОДЕЛИ ДАННЫХ ----------
class AuthRequest(BaseModel):
    action: str
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    token: Optional[str] = None
    user_id: Optional[int] = None
    interests: Optional[List[str]] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    interests: Optional[List[str]] = None

class RegisterEventRequest(BaseModel):
    user_id: int

# ---------- ЕДИНЫЙ ЭНДПОИНТ (для расписания, рекомендаций и т.д.) ----------
@app.post("/api/auth")
async def auth_handler(request: AuthRequest):
    api = get_api()
    return api.handle_request(request.dict())

# ---------- АВТОРИЗАЦИЯ ----------
@app.post("/api/auth/login")
async def login(request: LoginRequest):
    api = get_api()
    return api.login_user(request.email, request.password)

@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    api = get_api()
    return api.register_user(request.email, request.password, request.name)

@app.post("/api/auth/logout")
async def logout(token: str = Query(...)):
    api = get_api()
    return api.logout_user(token)

@app.get("/api/auth/me")
async def get_current_user(token: str = Query(...)):
    api = get_api()
    return api.get_current_user(token)   # пока заглушка, можно доработать

# ---------- СОБЫТИЯ ----------
@app.get("/api/events")
async def get_events(limit: int = 100):
    api = get_api()
    events = api._fetch_events_from_odoo()
    return {"success": True, "data": events[:limit]}

@app.get("/api/events/{event_id}")
async def get_event(event_id: int):
    api = get_api()
    events = api._fetch_events_from_odoo()
    event = next((e for e in events if e.get('id') == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True, "data": event}

@app.post("/api/events/{event_id}/register")
async def register_event(event_id: int, request: RegisterEventRequest):
    api = get_api()
    # Записываем взаимодействие (регистрация) для истории
    api.recommender.record_interaction(
        user_id=request.user_id,
        event_id=event_id,
        interaction_type='register',
        tags=None
    )
    # В реальной системе здесь нужно создавать запись в Odoo event.registration
    return {"success": True, "message": "Registered successfully"}

# ---------- ЭКСПОРТ В КАЛЕНДАРЬ (.ics) ----------
@app.get("/event/{event_id}/ics")
async def download_ics(event_id: int):
    api = get_api()
    events = api._fetch_events_from_odoo()
    event = next((e for e in events if e.get('id') == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    ics_gen = get_ics_generator()
    ics_content = ics_gen.generate_ics(event)
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=event_{event_id}.ics"}
    )

# ---------- ПОЛЬЗОВАТЕЛЬ ----------
@app.get("/api/user/profile")
async def get_profile(user_id: int = Query(...)):
    # Заглушка – можно будет реализовать получение из Odoo
    return {"success": True, "data": {"name": "User", "email": "user@example.com", "phone": ""}}

@app.put("/api/user/profile")
async def update_profile(request: UpdateProfileRequest, user_id: int = Query(...)):
    api = get_api()
    return api.update_user_profile(user_id, request.name, request.interests)

@app.get("/api/user/registrations")
async def get_registrations(user_id: int = Query(...)):
    # Заглушка – нужно будет получать регистрации из Odoo
    return {"success": True, "data": []}

# ---------- ГОРОДА ----------
CITIES = [
    "Москва", "Санкт-Петербург", "Екатеринбург", "Казань", "Новосибирск",
    "Нижний Новгород", "Краснодар", "Сочи", "Владивосток", "Онлайн"
]

@app.get("/api/cities")
async def get_cities():
    return {"success": True, "data": CITIES}

# ---------- УВЕДОМЛЕНИЯ (ЗАГЛУШКИ) ----------
@app.post("/api/notifications/test")
async def test_notification(registration_id: int):
    return {"success": True, "message": "Test notification sent"}

@app.get("/api/notifications/stats")
async def get_notification_stats():
    return {"success": True, "data": {"total_sent": 0, "successful": 0, "failed": 0}}

@app.post("/api/notifications/subscribe")
async def subscribe(email: str, event_id: int):
    return {"success": True, "message": "Subscribed"}
