from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from .agent.core.api import get_api

app = FastAPI(title="EventMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем обращаться к нам с любых хостов (плохой вариант, но в нашем случае самый удобный.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthRequest(BaseModel):
    action: str
    email: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    token: Optional[str] = None
    user_id: Optional[int] = None
    interests: Optional[List[str]] = None

@app.post("/api/auth")
async def auth_handler(request: AuthRequest):
    api = get_api()
    return api.handle_request(request.dict())

