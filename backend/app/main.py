from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.exceptions import HTTPException as StarletteHTTPException

from .agent.core.api import get_api

app = FastAPI(title="EventMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем обращаться к нам с любых хостов (плохой вариант, но в нашем случае самый удобный.)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SPAStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        try:
            response = await super().get_response(path, scope)
            if response.status_code == 404:
                return await super().get_response("index.html", scope)
            return response
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise

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


@app.get("/api/events")
async def get_events(request: AuthRequest):
    api = get_api()
    return api.handle_request(request.dict())

frontend_build_dir = Path(__file__).resolve().parents[2] / "frontend" / "build"

app.mount("/", SPAStaticFiles(directory=str(frontend_build_dir), html=True), name="spa")
