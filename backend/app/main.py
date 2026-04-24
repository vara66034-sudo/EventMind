from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.routes.agent import get_api
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="EventMind API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    model_config = {"extra": "allow"}

from fastapi import Response

@app.post("/api/auth")
async def auth_handler(request: Dict[str, Any]):
    api = get_api()
    result = api.handle_request(request)
    
    # Если результат содержит контент для файла (например, ICS)
    if isinstance(result, dict) and result.get('success') and isinstance(result.get('data'), dict) and 'content' in result['data']:
        data = result['data']
        return Response(
            content=data['content'],
            media_type=data.get('content_type', 'text/calendar'),
            headers={
                'Content-Disposition': f'attachment; filename="{data.get("filename", "calendar.ics")}"'
            }
        )
    
    return result

def get_user_email(user_id: int) -> Optional[str]:
    # Placeholder for email fetching
    return None

@app.on_event("startup")
async def startup_event():
    from .schedule.services import start_scheduler
    from .schedule.models import SessionLocal
    start_scheduler(SessionLocal, get_user_email)
    import logging
    logging.info("Scheduler started successfully")

frontend_build_dir = Path(__file__).resolve().parents[2] / "frontend" / "build"

if frontend_build_dir.exists():
    app.mount("/", SPAStaticFiles(directory=str(frontend_build_dir), html=True), name="spa")
else:
    import logging
    logging.warning(f"Frontend build directory not found at {frontend_build_dir}. API will run without serving static files.")
