from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from .models import get_db, SchedulePlatformCreate, SchedulePersonalCreate, ScheduleUpdate, ScheduleResponse
from .services import get_user_schedule, add_platform_event, add_personal_event, update_personal_event, remove_schedule, export_user_schedule_ics

router = APIRouter(prefix="/api/v1/schedule", tags=["schedule"])

def get_current_user_id(): return 1
def get_current_user_email(): return "user@example.com"

@router.get("/", response_model=List[ScheduleResponse])
def read_schedule(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return get_user_schedule(db, user_id)

@router.post("/platform", response_model=ScheduleResponse)
def create_platform_event( SchedulePlatformCreate, user_id: int = Depends(get_current_user_id), user_email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    return add_platform_event(db, user_id, data, user_email)

@router.post("/personal", response_model=ScheduleResponse)
def create_personal_event( SchedulePersonalCreate, user_id: int = Depends(get_current_user_id), user_email: str = Depends(get_current_user_email), db: Session = Depends(get_db)):
    return add_personal_event(db, user_id, data, user_email)

@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_event(schedule_id: int,  ScheduleUpdate, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    try:
        return update_personal_event(db, user_id, schedule_id, data)
    except ValueError:
        raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/{schedule_id}")
def delete_event(schedule_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    success = remove_schedule(db, user_id, schedule_id)
    if not success: raise HTTPException(status_code=404, detail="Event not found")
    return {"status": "deleted"}

@router.get("/export/ics")
def export_ics(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    ics_content = export_user_schedule_ics(db, user_id)
    return Response(content=ics_content, media_type="text/calendar", headers={"Content-Disposition": "attachment; filename=\"eventmind_schedule.ics\""})