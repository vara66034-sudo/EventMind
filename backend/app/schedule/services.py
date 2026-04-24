import logging
import os
import smtplib
import ssl

from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Callable, Dict, List, Optional
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .models import (
    SchedulePersonalCreate,
    SchedulePlatformCreate,
    ScheduleResponse,
    ScheduleUpdate,
    UserFavorite,
    UserSchedule,
)

logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "EventMind")

APP_TIMEZONE = os.getenv("APP_TIMEZONE", "Asia/Yekaterinburg")
NOTIFICATION_CHECK_MINUTES = int(os.getenv("NOTIFICATION_CHECK_MINUTES", "30"))
NOTIFICATION_LEAD_HOURS = float(os.getenv("NOTIFICATION_LEAD_HOURS", "24"))

scheduler = BackgroundScheduler()


def _now_local_naive() -> datetime:
    try:
        return datetime.now(ZoneInfo(APP_TIMEZONE)).replace(tzinfo=None)
    except Exception:
        return datetime.now()


def _normalize_datetime(value: Optional[datetime]) -> Optional[datetime]:
    if not value:
        return None

    if value.tzinfo is not None:
        return value.replace(tzinfo=None)

    return value


def escape_ics(text: str) -> str:
    if not text:
        return ""

    return (
        text.replace("\\", "\\\\")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def generate_ics(events: List[dict]) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//EventMind//RU",
        "CALSCALE:GREGORIAN",
    ]

    for ev in events:
        if not ev.get("start"):
            continue

        start = _normalize_datetime(ev["start"])
        end = _normalize_datetime(ev.get("end")) or start + timedelta(hours=2)

        dt_start = start.strftime("%Y%m%dT%H%M%S")
        dt_end = end.strftime("%Y%m%dT%H%M%S")

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{ev['id']}-eventmind",
                f"DTSTART:{dt_start}",
                f"DTEND:{dt_end}",
                f"SUMMARY:{escape_ics(ev.get('name', ''))}",
                f"DESCRIPTION:{escape_ics(ev.get('description', ''))}",
                f"LOCATION:{escape_ics(ev.get('location', ''))}",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")

    return "\r\n".join(lines)


def send_email(to: str, subject: str, body: str) -> None:
    if not to:
        raise ValueError("Email recipient is empty")

    email_provider = os.getenv("EMAIL_PROVIDER", "smtp").lower()

    if email_provider == "resend":
        import resend

        resend_api_key = os.getenv("RESEND_API_KEY", "")
        resend_from = os.getenv("RESEND_FROM", "EventMind <onboarding@resend.dev>")

        if not resend_api_key:
            raise RuntimeError("RESEND_API_KEY is empty. Check backend/.env")

        resend.api_key = resend_api_key

        result = resend.Emails.send({
            "from": resend_from,
            "to": [to],
            "subject": subject,
            "html": body,
        })

        logger.info(f"Resend email result: {result}")
        return

    if not SMTP_USER:
        raise RuntimeError("SMTP_USER is empty. Check backend/.env")

    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is empty. Check backend/.env")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
    msg["To"] = to

    msg.attach(MIMEText(body, "html", "utf-8"))

    if SMTP_PORT == 465:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            SMTP_HOST,
            SMTP_PORT,
            context=context,
            timeout=60,
        ) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, [to], msg.as_string())

        return

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        if SMTP_USE_TLS:
            server.starttls(context=ssl.create_default_context())

        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to], msg.as_string())


def _email_template(title: str, text: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;background:#FBE4D8;padding:28px;border-radius:20px;">
        <h2 style="color:#180018;margin-top:0;">{title}</h2>
        <p style="color:#512A59;font-size:16px;line-height:1.5;">{text}</p>
        <p style="color:#854E6B;font-size:13px;margin-top:28px;">
            Это автоматическое уведомление EventMind.
        </p>
    </div>
    """


def format_schedule_response(rec: UserSchedule) -> ScheduleResponse:
    if rec.is_personal:
        return ScheduleResponse(
            id=rec.id,
            type="personal",
            event_id=None,
            name=rec.personal_title or "Личное событие",
            start=rec.personal_start,
            end=rec.personal_end,
            location=rec.personal_location or "",
            description=rec.personal_description or "",
            status=rec.status,
            added_at=rec.added_at,
        )

    return ScheduleResponse(
        id=rec.id,
        type="platform",
        event_id=rec.event_id,
        name=f"Событие #{rec.event_id}",
        start=rec.event_start_date,
        end=None,
        location="",
        description="",
        status=rec.status,
        added_at=rec.added_at,
    )


def get_user_schedule(
    db: Session,
    user_id: int,
    status: str = "planned",
) -> List[ScheduleResponse]:
    records = (
        db.query(UserSchedule)
        .filter(
            UserSchedule.user_id == int(user_id),
            UserSchedule.status == status,
        )
        .all()
    )

    return [format_schedule_response(rec) for rec in records]


def add_platform_event(
    db: Session,
    user_id: int,
    data: SchedulePlatformCreate,
    user_email: Optional[str] = None,
    event_start_date: Optional[datetime] = None,
) -> ScheduleResponse:
    event_start_date = _normalize_datetime(event_start_date)

    existing = (
        db.query(UserSchedule)
        .filter(
            UserSchedule.user_id == int(user_id),
            UserSchedule.event_id == int(data.event_id),
        )
        .first()
    )

    if existing:
        if event_start_date and not existing.event_start_date:
            existing.event_start_date = event_start_date
            existing.reminder_sent = False
            existing.reminder_sent_at = None
            db.commit()
            db.refresh(existing)

        return format_schedule_response(existing)

    new_rec = UserSchedule(
        user_id=int(user_id),
        event_id=int(data.event_id),
        event_start_date=event_start_date,
        is_personal=False,
        status="planned",
        reminder_sent=False,
        reminder_sent_at=None,
    )

    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)

    if user_email:
        try:
            send_email(
                to=user_email,
                subject="✅ Мероприятие добавлено в календарь",
                body=_email_template(
                    "Мероприятие добавлено",
                    f"Событие #{new_rec.event_id} добавлено в ваш календарь EventMind.",
                ),
            )
        except Exception as e:
            logger.error(f"Failed to send add-platform-event email: {e}")

    return format_schedule_response(new_rec)


def add_personal_event(
    db: Session,
    user_id: int,
    data: SchedulePersonalCreate,
    user_email: Optional[str] = None,
) -> ScheduleResponse:
    new_rec = UserSchedule(
        user_id=int(user_id),
        is_personal=True,
        personal_title=data.title,
        personal_start=_normalize_datetime(data.start),
        personal_end=_normalize_datetime(data.end),
        personal_description=data.description or "",
        personal_location=data.location or "",
        status="planned",
        reminder_sent=False,
        reminder_sent_at=None,
    )

    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)

    if user_email:
        try:
            send_email(
                to=user_email,
                subject=f"✅ Личное событие добавлено: {data.title}",
                body=_email_template(
                    "Личное событие добавлено",
                    f"Событие «{data.title}» создано в вашем календаре.",
                ),
            )
        except Exception as e:
            logger.error(f"Failed to send add-personal-event email: {e}")

    return format_schedule_response(new_rec)


def update_personal_event(
    db: Session,
    user_id: int,
    schedule_id: int,
    data: ScheduleUpdate,
) -> ScheduleResponse:
    rec = (
        db.query(UserSchedule)
        .filter(
            UserSchedule.id == int(schedule_id),
            UserSchedule.user_id == int(user_id),
            UserSchedule.is_personal == True,
        )
        .first()
    )

    if not rec:
        raise ValueError("Record not found or access denied")

    if data.title is not None:
        rec.personal_title = data.title

    if data.start is not None:
        rec.personal_start = _normalize_datetime(data.start)
        rec.reminder_sent = False
        rec.reminder_sent_at = None

    if data.end is not None:
        rec.personal_end = _normalize_datetime(data.end)

    if data.description is not None:
        rec.personal_description = data.description

    if data.location is not None:
        rec.personal_location = data.location

    db.commit()
    db.refresh(rec)

    return format_schedule_response(rec)


def remove_schedule(db: Session, user_id: int, schedule_id: int) -> bool:
    rec = (
        db.query(UserSchedule)
        .filter(
            UserSchedule.id == int(schedule_id),
            UserSchedule.user_id == int(user_id),
        )
        .first()
    )

    if not rec:
        return False

    db.delete(rec)
    db.commit()

    return True


def add_favorite(
    db: Session,
    user_id: int,
    event_id: int,
    event_start_date: Optional[datetime] = None,
) -> bool:
    event_start_date = _normalize_datetime(event_start_date)

    existing = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.user_id == int(user_id),
            UserFavorite.event_id == int(event_id),
        )
        .first()
    )

    if existing:
        if event_start_date and not existing.event_start_date:
            existing.event_start_date = event_start_date
            existing.reminder_sent = False
            existing.reminder_sent_at = None
            db.commit()

        return True

    new_fav = UserFavorite(
        user_id=int(user_id),
        event_id=int(event_id),
        event_start_date=event_start_date,
        reminder_sent=False,
        reminder_sent_at=None,
    )

    db.add(new_fav)
    db.commit()

    return True


def remove_favorite(db: Session, user_id: int, event_id: int) -> bool:
    rec = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.user_id == int(user_id),
            UserFavorite.event_id == int(event_id),
        )
        .first()
    )

    if not rec:
        return False

    db.delete(rec)
    db.commit()

    return True


def get_favorites(db: Session, user_id: int) -> List[int]:
    records = (
        db.query(UserFavorite)
        .filter(UserFavorite.user_id == int(user_id))
        .all()
    )

    return [int(rec.event_id) for rec in records]


def export_user_schedule_ics(db: Session, user_id: int) -> str:
    records = (
        db.query(UserSchedule)
        .filter(
            UserSchedule.user_id == int(user_id),
            UserSchedule.status == "planned",
        )
        .all()
    )

    events = [format_schedule_response(rec).model_dump() for rec in records]

    return generate_ics(events)


def run_reminder_job(
    db_session_factory,
    get_email_func: Callable[[int], Optional[str]],
) -> Dict[str, int]:
    sent_favorites = 0
    sent_schedule = 0
    failed = 0

    now = _now_local_naive()
    remind_until = now + timedelta(hours=NOTIFICATION_LEAD_HOURS)

    with db_session_factory() as db:
        fav_to_remind = (
            db.query(UserFavorite)
            .filter(
                UserFavorite.reminder_sent == False,
                UserFavorite.event_start_date.isnot(None),
                UserFavorite.event_start_date >= now,
                UserFavorite.event_start_date <= remind_until,
            )
            .all()
        )

        for fav in fav_to_remind:
            email = get_email_func(int(fav.user_id))

            if not email:
                logger.warning(f"No email for user {fav.user_id}")
                continue

            try:
                send_email(
                    to=email,
                    subject="⏰ Напоминание об избранном событии",
                    body=_email_template(
                        "Скоро избранное событие",
                        (
                            f"Событие #{fav.event_id} начнётся "
                            f"{fav.event_start_date.strftime('%d.%m.%Y в %H:%M')}."
                        ),
                    ),
                )

                fav.reminder_sent = True
                fav.reminder_sent_at = now
                db.commit()
                sent_favorites += 1

            except Exception as e:
                db.rollback()
                failed += 1
                logger.error(f"Failed to send favorite reminder: {e}")

        schedule_to_remind = (
            db.query(UserSchedule)
            .filter(
                UserSchedule.status == "planned",
                UserSchedule.reminder_sent == False,
                or_(
                    UserSchedule.personal_start.between(now, remind_until),
                    UserSchedule.event_start_date.between(now, remind_until),
                ),
            )
            .all()
        )

        for rec in schedule_to_remind:
            email = get_email_func(int(rec.user_id))

            if not email:
                logger.warning(f"No email for user {rec.user_id}")
                continue

            event_time = rec.personal_start if rec.is_personal else rec.event_start_date
            event_title = rec.personal_title if rec.is_personal else f"Событие #{rec.event_id}"

            if not event_time:
                continue

            try:
                send_email(
                    to=email,
                    subject=f"⏰ Напоминание: {event_title}",
                    body=_email_template(
                        "Событие скоро начнётся",
                        (
                            f"«{event_title}» начнётся "
                            f"{event_time.strftime('%d.%m.%Y в %H:%M')}."
                        ),
                    ),
                )

                rec.reminder_sent = True
                rec.reminder_sent_at = now
                db.commit()
                sent_schedule += 1

            except Exception as e:
                db.rollback()
                failed += 1
                logger.error(f"Failed to send schedule reminder: {e}")

    result = {
        "sent_favorites": sent_favorites,
        "sent_schedule": sent_schedule,
        "failed": failed,
    }

    logger.info(f"Reminder job finished: {result}")

    return result


def start_scheduler(db_session_factory, get_email_func) -> None:
    if scheduler.running:
        return

    scheduler.add_job(
        func=run_reminder_job,
        trigger="interval",
        minutes=NOTIFICATION_CHECK_MINUTES,
        args=[db_session_factory, get_email_func],
        id="eventmind_reminders",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()

    logger.info(
        f"EventMind notification scheduler started. "
        f"Check every {NOTIFICATION_CHECK_MINUTES} minutes, "
        f"lead time {NOTIFICATION_LEAD_HOURS} hours."
    )


def get_pending_notification_stats(db: Session) -> Dict[str, int]:
    now = _now_local_naive()
    remind_until = now + timedelta(hours=NOTIFICATION_LEAD_HOURS)

    favorites_pending = (
        db.query(UserFavorite)
        .filter(
            UserFavorite.reminder_sent == False,
            UserFavorite.event_start_date.isnot(None),
            UserFavorite.event_start_date >= now,
            UserFavorite.event_start_date <= remind_until,
        )
        .count()
    )

    schedule_pending = (
        db.query(UserSchedule)
        .filter(
            UserSchedule.status == "planned",
            UserSchedule.reminder_sent == False,
            or_(
                UserSchedule.personal_start.between(now, remind_until),
                UserSchedule.event_start_date.between(now, remind_until),
            ),
        )
        .count()
    )

    return {
        "favorites_pending": favorites_pending,
        "schedule_pending": schedule_pending,
        "check_every_minutes": NOTIFICATION_CHECK_MINUTES,
        "lead_hours": NOTIFICATION_LEAD_HOURS,
    }