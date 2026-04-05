"""
EventMind ICS Calendar Generator
Author: Ksusha
Description: Generate .ics files for calendar export
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import uuid

logger = logging.getLogger('EventMind.ICS')


class ICSGenerator:
    """
    Generate iCalendar (.ics) files for events

    Supports:
    - Single event export
    - Multiple events export
    - Recurring events
    - Reminders/alarms
    - Timezone handling
    - RFC 5545 compliant text escaping
    """

    def __init__(self):
        """Initialize ICS generator"""
        self.stats = {
            'total_generated': 0,
            'single_events': 0,
            'multi_events': 0
        }
        logger.info("ICSGenerator initialized")

    def _escape_ics_text(self, text: str) -> str:
        """
        Escape special characters for iCalendar (RFC 5545)
        Required escapes: \\ ; , \n
        """
        if not text:
            return ''
        return (str(text)
            .replace('\\', '\\\\')
            .replace(';', '\\;')
            .replace(',', '\\,')
            .replace('\n', '\\n')
            .replace('\r', '')
        )

    def _format_datetime(self, dt_value) -> str:
        """Format datetime for .ics (YYYYMMDDTHHMMSSZ)"""
        if isinstance(dt_value, str):
            try:
                dt = datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
            except:
                dt = datetime.now()
        else:
            dt = dt_value

        return dt.strftime('%Y%m%dT%H%M%SZ')

    def _add_hours(self, dt_value, hours: int) -> datetime:
        """Add hours to a datetime"""
        if isinstance(dt_value, str):
            try:
                dt = datetime.fromisoformat(dt_value.replace('Z', '+00:00'))
            except:
                dt = datetime.now()
        else:
            dt = dt_value

        return dt + timedelta(hours=hours)

    def generate_ics(self, event: Dict, include_alarm: bool = True) -> str:
        """
        Generate .ics content for a single event

        Args:
            event: Event dictionary with:
                - id: Event ID
                - name: Event title
                - date_begin: Start date (ISO format)
                - date_end: End date (optional)
                - location: Location (optional)
                - description: Description (optional)
                - url: Event URL (optional)
            include_alarm: Whether to include alarm/reminder

        Returns:
            .ics file content as string
        """
        dtstart = self._format_datetime(event.get('date_begin', datetime.now()))
        dtend = self._format_datetime(
            event.get('date_end') or
            self._add_hours(event.get('date_begin'), 2)
        )

        event_id = event.get('id', str(uuid.uuid4()))
        uid = f"{event_id}@{datetime.now().strftime('%Y%m%d')}.eventmind.ai"

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//EventMind//EventMind AI Calendar//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{self._escape_ics_text(event.get('name', 'Event'))}",
        ]

        if event.get('location'):
            lines.append(f"LOCATION:{self._escape_ics_text(event['location'])}")

        if event.get('description'):
            desc = event['description'][:1000]
            lines.append(f"DESCRIPTION:{self._escape_ics_text(desc)}")

        if event.get('url'):
            lines.append(f"URL:{event['url']}")

        created = datetime.now().strftime('%Y%m%dT%H%M%S')
        lines.append(f"DTSTAMP:{created}")
        lines.append(f"CREATED:{created}")
        lines.append(f"LAST-MODIFIED:{created}")

        if include_alarm:
            lines.extend([
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                "DESCRIPTION:Reminder",
                "TRIGGER:-PT1H",
                "END:VALARM"
            ])

        lines.extend([
            "END:VEVENT",
            "END:VCALENDAR"
        ])

        self.stats['total_generated'] += 1
        self.stats['single_events'] += 1

        return "\r\n".join(lines)

    def generate_multi_ics(self, events: List[Dict], calendar_name: str = "EventMind Events") -> str:
        """Generate .ics with multiple events"""
        if not events:
            return self._generate_empty_calendar(calendar_name)

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"X-WR-CALNAME:{calendar_name}",
            "PRODID:-//EventMind//EventMind AI Calendar//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]

        for event in events:
            event_ics = self.generate_ics(event, include_alarm=False)
            vevent_lines = []
            in_vevent = False

            for line in event_ics.split('\n'):
                if line == "BEGIN:VEVENT":
                    in_vevent = True
                if in_vevent:
                    vevent_lines.append(line)
                if line == "END:VEVENT":
                    in_vevent = False
                    break

            lines.extend(vevent_lines)

        lines.append("END:VCALENDAR")

        self.stats['total_generated'] += 1
        self.stats['multi_events'] += 1

        return "\r\n".join(lines)

    def _generate_empty_calendar(self, calendar_name: str) -> str:
        """Generate empty calendar"""
        return "\r\n".join([
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"X-WR-CALNAME:{calendar_name}",
            "PRODID:-//EventMind//EventMind AI Calendar//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "END:VCALENDAR"
        ])

    def generate_ics_file(self, event: Dict, filepath: str) -> bool:
        """Generate and save .ics file"""
        try:
            content = self.generate_ics(event)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"ICS file saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save ICS file: {e}")
            return False

    def generate_recurring_ics(self,
                              event: Dict,
                              frequency: str = 'weekly',
                              count: int = 4) -> str:
        """Generate .ics for recurring event"""
        freq_map = {
            'daily': 'DAILY',
            'weekly': 'WEEKLY',
            'monthly': 'MONTHLY'
        }

        rr_freq = freq_map.get(frequency, 'WEEKLY')
        base_ics = self.generate_ics(event, include_alarm=False)

        lines = []
        in_vevent = False

        for line in base_ics.split('\n'):
            if line == "BEGIN:VEVENT":
                in_vevent = True
                lines.append(line)
            elif in_vevent and line.startswith("END:VEVENT"):
                lines.append(f"RRULE:FREQ={rr_freq};COUNT={count}")
                lines.append(line)
                in_vevent = False
            else:
                lines.append(line)

        return "\r\n".join(lines)

    def validate_ics(self, content: str) -> bool:
        """Basic validation of .ics content"""
        required = ['BEGIN:VCALENDAR', 'END:VCALENDAR', 'BEGIN:VEVENT', 'END:VEVENT']
        for req in required:
            if req not in content:
                logger.warning(f"ICS validation failed: missing {req}")
                return False
        return True

    def get_stats(self) -> Dict:
        """Get generator statistics"""
        return self.stats


    # для оды

    def generate_ics_from_odoo(self, event_record, base_url: Optional[str] = None, include_alarm: bool = True) -> str:
        """
        Generate .ics content from Odoo event.event record

        Args:
            event_record: Odoo recordset (event.event model)
            base_url: Base URL for generating absolute links in ICS
            include_alarm: Whether to include VALARM reminder

        Returns:
            str: .ics file content
        """
        # Convert Odoo record to dict compatible with generate_ics()
        event_dict = {
            'id': event_record.id,
            'name': event_record.name or '',
            'date_begin': event_record.date_begin.isoformat() if event_record.date_begin else '',
            'date_end': event_record.date_end.isoformat() if event_record.date_end else None,
            'location': event_record.location or '',
            'description': event_record.note or '',
            'url': f"{base_url}/event/event/{event_record.id}" if base_url else None
        }
        
        return self.generate_ics(event_dict, include_alarm=include_alarm)

    def generate_ics_file_from_odoo(self, event_record, filepath: str, base_url: Optional[str] = None) -> bool:
        """
        Generate and save .ics file from Odoo event.event record

        Args:
            event_record: Odoo recordset (event.event model)
            filepath: Path to save the .ics file
            base_url: Base URL for absolute links

        Returns:
            bool: True if saved successfully
        """
        try:
            content = self.generate_ics_from_odoo(event_record, base_url)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"ICS file saved from Odoo record: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save ICS file from Odoo: {e}")
            return False


    # для фронта

    def api_generate_ics(self, event: Dict, include_alarm: bool = True) -> Dict:
        """
        API endpoint handler for generating ICS content

        Expected input:
        {
            "id": 123,
            "name": "Event Name",
            "date_begin": "2024-04-01T18:00:00+03:00",
            "date_end": "2024-04-01T20:00:00+03:00",  // optional
            "location": "Moscow",  // optional
            "description": "Event description"  // optional
        }

        Returns:
        {
            "success": true,
            "data": {
                "content": "BEGIN:VCALENDAR...",
                "filename": "event_123.ics",
                "content_type": "text/calendar; charset=utf-8"
            },
            "code": 200
        }
        """
        try:
            # Validate required fields
            if 'id' not in event or 'name' not in event or 'date_begin' not in event:
                return {
                    'success': False,
                    'error': 'Event missing required fields: id, name, date_begin',
                    'code': 400
                }

            content = self.generate_ics(event, include_alarm=include_alarm)
            
            return {
                'success': True,
                'data': {
                    'content': content,
                    'filename': f"event_{event['id']}.ics",
                    'content_type': 'text/calendar; charset=utf-8'
                },
                'code': 200
            }
            
        except Exception as e:
            logger.error(f"API error in api_generate_ics: {type(e).__name__}: {e}")
            return {
                'success': False,
                'error': f'Failed to generate ICS: {str(e)}',
                'code': 500
            }

    def api_validate_ics(self, content: str) -> Dict:
        """
        API endpoint for validating ICS content

        Returns:
        {
            "success": true,
            "data": {"valid": true, "errors": []},
            "code": 200
        }
        """
        is_valid = self.validate_ics(content)
        
        if is_valid:
            return {
                'success': True,
                'data': {'valid': True, 'errors': []},
                'code': 200
            }
        else:
            return {
                'success': True,
                'data': {'valid': False, 'errors': ['Missing required iCalendar tags']},
                'code': 200
            }

    def api_get_stats(self) -> Dict:
        """
        API endpoint for generator statistics

        Returns:
        {
            "success": true,
            "data": {"total_generated": 100, ...},
            "code": 200
        }
        """
        return {
            'success': True,
            'data': self.get_stats(),
            'code': 200
        }


# Global instance
_ics_gen_instance = None

def get_ics_generator() -> ICSGenerator:
    """Get or create the global ICS generator instance"""
    global _ics_gen_instance
    if _ics_gen_instance is None:
        _ics_gen_instance = ICSGenerator()
    return _ics_gen_instance


def reset_ics_generator():
    """Reset the global instance (useful for testing)"""
    global _ics_gen_instance
    _ics_gen_instance = None
