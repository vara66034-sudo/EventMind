from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from .models import UserSchedule, SchedulePlatformCreate, SchedulePersonalCreate, ScheduleUpdate, ScheduleResponse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

def escape_ics(text: str) -> str:
    if not text: return ""
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

def generate_ics(events: List[dict]) -> str:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//EventMind//RU", "CALSCALE:GREGORIAN"]
    for ev in events:
        if not ev.get("start"): continue
        dt_start = ev["start"].strftime("%Y%m%dT%H%M%SZ")
        dt_end = (ev.get("end") or ev["start"] + timedelta(hours=2)).strftime("%Y%m%dT%H%M%SZ")
        lines.extend(["BEGIN:VEVENT", f"UID:{ev['id']}-eventmind", f"DTSTART:{dt_start}", f"DTEND:{dt_end}", f"SUMMARY:{escape_ics(ev.get('name', ''))}", f"DESCRIPTION:{escape_ics(ev.get('description', ''))}", f"LOCATION:{escape_ics(ev.get('location', ''))}", "END:VEVENT"])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

def send_email(to: str, subject: str, body: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        if SMTP_USE_TLS: server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to, msg.as_string())

def format_schedule_response(rec: UserSchedule) -> ScheduleResponse:
    if rec.is_personal:
        return ScheduleResponse(id=rec.id, type="personal", event_id=None, name=rec.personal_title or "Личное событие", start=rec.personal_start, end=rec.personal_end, location=rec.personal_location or "", description=rec.personal_description or "", status=rec.status, added_at=rec.added_at)
    return ScheduleResponse(id=rec.id, type="platform", event_id=rec.event_id, name=f"Событие #{rec.event_id}", start=None, end=None, location="", description="", status=rec.status, added_at=rec.added_at)

def get_user_schedule(db: Session, user_id: int, status: str = "planned") -> List[ScheduleResponse]:
    records = db.query(UserSchedule).filter(UserSchedule.user_id == user_id, UserSchedule.status == status).all()
    return [format_schedule_response(rec) for rec in records]

def add_platform_event(db: Session, user_id: int,  SchedulePlatformCreate, user_email: str) -> ScheduleResponse:
    existing = db.query(UserSchedule).filter(UserSchedule.user_id == user_id, UserSchedule.event_id == data.event_id).first()
    if existing: return format_schedule_response(existing)
    new_rec = UserSchedule(user_id=user_id, event_id=data.event_id, is_personal=False, status="planned")
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    try: send_email(to=user_email, subject="✅ Мероприятие добавлено в расписание", body=f"<p>Событие <b>{new_rec.event_id}</b> добавлено в календарь.</p>")
    except Exception: pass
    return format_schedule_response(new_rec)

def add_personal_event(db: Session, user_id: int,  SchedulePersonalCreate, user_email: str) -> ScheduleResponse:
    new_rec = UserSchedule(user_id=user_id, is_personal=True, personal_title=data.title, personal_start=data.start, personal_end=data.end, personal_description=data.description or "", personal_location=data.location or "", status="planned")
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    try: send_email(to=user_email, subject=f"✅ Личное событие добавлено: {data.title}", body=f"<p>Событие <b>{data.title}</b> создано в календаре.</p>")
    except Exception: pass
    return format_schedule_response(new_rec)

def update_personal_event(db: Session, user_id: int, schedule_id: int,  ScheduleUpdate) -> ScheduleResponse:
    rec = db.query(UserSchedule).filter(UserSchedule.id == schedule_id, UserSchedule.user_id == user_id, UserSchedule.is_personal == True).first()
    if not rec: raise ValueError("Record not found or access denied")
    if data.title is not None: rec.personal_title = data.title
    if data.start is not None: rec.personal_start = data.start
    if data.end is not None: rec.personal_end = data.end
    if data.description is not None: rec.personal_description = data.description
    if data.location is not None: rec.personal_location = data.location
    rec.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(rec)
    return format_schedule_response(rec)

def remove_schedule(db: Session, user_id: int, schedule_id: int) -> bool:
    rec = db.query(UserSchedule).filter(UserSchedule.id == schedule_id, UserSchedule.user_id == user_id).first()
    if not rec: return False
    db.delete(rec)
    db.commit()
    return True

def export_user_schedule_ics(db: Session, user_id: int) -> str:
    records = db.query(UserSchedule).filter(UserSchedule.user_id == user_id, UserSchedule.status == "planned").all()
    events = [format_schedule_response(rec).model_dump() for rec in records]
    return generate_ics(events)

scheduler = BackgroundScheduler()

def start_scheduler(db_session_factory, user_email_map):
    if not scheduler.running:
        scheduler.add_job(func=run_reminder_job, trigger="interval", hours=1, args=[db_session_factory, user_email_map], id="eventmind_reminders", replace_existing=True)
        scheduler.start()

def run_reminder_job(db_session_factory, user_email_map):
    with db_session_factory() as db:
        now = datetime.utcnow()
        tomorrow = now + timedelta(hours=23.5)
        to_remind = db.query(UserSchedule).filter(UserSchedule.status == "planned", UserSchedule.reminder_sent == False, UserSchedule.personal_start >= now, UserSchedule.personal_start <= tomorrow).all()
        for rec in to_remind:
            email = user_email_map.get(rec.user_id)
            if email:
                try:
                    send_email(to=email, subject=f"⏰ Напоминание: {rec.personal_title}", body=f"<p>Мероприятие <b>{rec.personal_title}</b> состоится завтра в {rec.personal_start.strftime('%H:%M')}.</p>")
                    rec.reminder_sent = True
                    db.commit()
                except Exception: pass