"""
EventMind Notification Module
Author: Ksusha
Description: Email reminders and notifications for events
"""

import logging
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import jinja2

from ics_generator import ICSGenerator

logger = logging.getLogger('EventMind.Notifier')


class Notifier:
    """
    Handle event notifications and reminders

    Features:
    - Email reminders before events (configurable hours)
    - Calendar attachments (.ics)
    - Batch sending
    - Template-based emails
    - Error handling and logging
    - Odoo integration layer
    - Frontend API compatibility
    """

    def __init__(self, config_path: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize notifier

        Args:
            config_path: Path to email configuration JSON file
            base_url: Base URL for generating absolute links (for emails)
        """
        self.config = self._load_config(config_path)
        self.base_url = base_url or os.getenv('BASE_URL', 'http://localhost:8069')
        self.ics_gen = ICSGenerator()
        self.stats = self._init_stats()
        self._setup_templates()

        logger.info("Notifier initialized")
        logger.info(f"SMTP: {self.config['smtp']['server']}:{self.config['smtp']['port']}")
        logger.info(f"Base URL: {self.base_url}")

    def _load_config(self, path: Optional[str]) -> Dict:
        """Load email configuration with environment variable overrides"""
        default_config = {
            'smtp': {
                'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'port': int(os.getenv('SMTP_PORT', 587)),
                'use_tls': True,
                'username': os.getenv('SMTP_USERNAME', ''),
                'password': os.getenv('SMTP_PASSWORD', '')
            },
            'email': {
                'from': os.getenv('EMAIL_FROM', 'noreply@eventmind.ai'),
                'from_name': os.getenv('EMAIL_FROM_NAME', 'EventMind AI')
            },
            'reminder': {
                'default_hours': int(os.getenv('REMINDER_HOURS', '24')),
                'max_reminders_per_user': 3,
                'reminder_windows': [24, 2, 1],
                'enable_ics_attachment': True
            },
            'templates': {
                'path': 'templates',
                'default': 'email_template.html'
            }
        }

        if path and Path(path).exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    for key, value in loaded_config.items():
                        if key in default_config and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                logger.info(f"Loaded config from {path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")

        # Environment variables override config file
        default_config['smtp']['username'] = os.getenv('SMTP_USERNAME', default_config['smtp']['username'])
        default_config['smtp']['password'] = os.getenv('SMTP_PASSWORD', default_config['smtp']['password'])

        return default_config

    def _setup_templates(self):
        """Setup Jinja2 template environment with flexible path resolution"""
        # Try multiple possible template paths for Odoo compatibility
        possible_paths = [
            Path(__file__).parent / self.config['templates']['path'],  # standalone
            Path(__file__).parent.parent / self.config['templates']['path'],  # Odoo module
            Path(self.config['templates']['path']),  # absolute path
        ]
        
        template_path = None
        for path in possible_paths:
            if path.exists():
                template_path = path
                break
        
        if template_path:
            self.template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(str(template_path)),
                autoescape=True
            )
            logger.info(f"Loaded templates from {template_path}")
        else:
            self.template_env = None
            logger.warning(f"Template path not found in any of: {possible_paths}")

    def _init_stats(self) -> Dict:
        """Initialize statistics"""
        return {
            'total_sent': 0,
            'successful': 0,
            'failed': 0,
            'last_sent': None,
            'by_type': {'reminder': 0, 'welcome': 0, 'custom': 0}
        }

    def _escape_text(self, text: str) -> str:
        """Escape special characters for HTML email content"""
        if not text:
            return ''
        return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
        )

    def _build_absolute_url(self, path: str) -> str:
        """Build absolute URL from relative path for email links"""
        if path.startswith('http'):
            return path
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def send_reminder(self,
                      user_email: str,
                      user_name: str,
                      event: Dict,
                      hours_before: Optional[int] = None) -> bool:
        """
        Send a single reminder email

        Args:
            user_email: Recipient email
            user_name: Recipient name
            event: Event dictionary with id, name, date_begin, location, description
            hours_before: Hours before event (for message)

        Returns:
            True if sent successfully
        """
        if hours_before is None:
            hours_before = self.config['reminder']['default_hours']

        if not user_email:
            logger.warning(f"No email provided for user {user_name}")
            return False

        # Calculate time until event
        try:
            event_date = datetime.fromisoformat(event['date_begin'].replace('Z', '+00:00'))
            now = datetime.now(event_date.tzinfo)
            time_diff = event_date - now
            hours = int(time_diff.total_seconds() / 3600)
            days = hours // 24
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            hours = hours_before
            days = 0

        if days > 0:
            time_text = f"{days} day{'s' if days != 1 else ''}"
        elif hours > 0:
            time_text = f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            minutes = int(time_diff.total_seconds() / 60) if 'time_diff' in locals() else 0
            time_text = f"{minutes} minute{'s' if minutes != 1 else ''}"

        # Generate ICS attachment if enabled
        ics_content = None
        if self.config['reminder']['enable_ics_attachment']:
            ics_content = self.ics_gen.generate_ics(event)

        # Prepare email content
        subject = f"Reminder: {self._escape_text(event['name'])} starts in {time_text}"

        # Build absolute URL for ICS download (important for email clients)
        ics_url = self._build_absolute_url(f"/event/{event['id']}/ics")

        # Render HTML template
        html_content = self._render_template(
            'email_template.html',
            user_name=user_name,
            event_name=event['name'],
            event_date=event['date_begin'],
            event_location=event.get('location', 'Not specified'),
            event_description=event.get('description', ''),
            time_until=time_text,
            ics_url=ics_url,
            unsubscribe_url=self._build_absolute_url(f"/unsubscribe/{user_email}"),
            company_logo=os.getenv('COMPANY_LOGO_URL', '')
        )

        # Send email
        success = self._send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content,
            ics_content=ics_content,
            event_id=event['id']
        )

        # Update stats
        self.stats['total_sent'] += 1
        if success:
            self.stats['successful'] += 1
            self.stats['by_type']['reminder'] += 1
        else:
            self.stats['failed'] += 1

        self.stats['last_sent'] = datetime.now().isoformat()

        return success

    def _render_template(self, template_name: str, **kwargs) -> str:
        """Render HTML template with variables"""
        if self.template_env:
            try:
                template = self.template_env.get_template(template_name)
                return template.render(**kwargs)
            except jinja2.TemplateNotFound:
                logger.warning(f"Template {template_name} not found, using fallback")
            except Exception as e:
                logger.error(f"Template rendering error: {e}")

        # Fallback HTML template (inline styles for email client compatibility)
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 30px; text-align: center; border-radius: 10px; }}
                .event-card {{ background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .button {{ background: #667eea; color: white; padding: 12px 30px;
                         text-decoration: none; border-radius: 25px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Event Reminder</h1>
                </div>
                <p>Hello <strong>{self._escape_text(kwargs.get('user_name', 'there'))}</strong>!</p>
                <p>Your event starts in <strong>{kwargs.get('time_until', 'soon')}</strong>!</p>
                <div class="event-card">
                    <h2>{self._escape_text(kwargs.get('event_name', 'Event'))}</h2>
                    <p><strong>When:</strong> {kwargs.get('event_date', 'TBA')}</p>
                    <p><strong>Where:</strong> {self._escape_text(kwargs.get('event_location', 'TBA'))}</p>
                </div>
                <p>We look forward to seeing you there!</p>
                <p>— EventMind AI Team</p>
            </div>
        </body>
        </html>
        """

    def _send_email(self,
                   to_email: str,
                   subject: str,
                   html_content: str,
                   ics_content: Optional[str] = None,
                   event_id: Optional[int] = None) -> bool:
        """Send email via SMTP with error handling"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{self.config['email']['from_name']} <{self.config['email']['from']}>"
        msg['To'] = to_email

        msg.attach(MIMEText(html_content, 'html'))

        if ics_content:
            ics_part = MIMEBase('text', 'calendar', method='REQUEST')
            ics_part.set_payload(ics_content)
            encoders.encode_base64(ics_part)
            ics_part.add_header(
                'Content-Disposition',
                f'attachment; filename="event_{event_id}.ics"'
            )
            ics_part.add_header('Content-Type', 'text/calendar; charset=UTF-8')
            msg.attach(ics_part)

        try:
            if self.config['smtp']['username'] and self.config['smtp']['password']:
                server = smtplib.SMTP(
                    self.config['smtp']['server'],
                    self.config['smtp']['port']
                )
                if self.config['smtp'].get('use_tls', True):
                    server.starttls()
                server.login(
                    self.config['smtp']['username'],
                    self.config['smtp']['password']
                )
                server.send_message(msg)
                server.quit()
            else:
                # Local SMTP for development (MailHog, python debug server)
                server = smtplib.SMTP('localhost', 1025)
                server.send_message(msg)
                server.quit()

            logger.info(f"Email sent to {to_email}: {subject}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {type(e).__name__}: {e}")
            return False

    def send_batch_reminders(self, reminders: List[Dict]) -> Dict:
        """Send multiple reminders in batch with statistics"""
        logger.info(f"Sending batch of {len(reminders)} reminders")

        results = {
            'total': len(reminders),
            'successful': 0,
            'failed': 0,
            'details': []
        }

        for reminder in reminders:
            success = self.send_reminder(
                user_email=reminder['user_email'],
                user_name=reminder['user_name'],
                event=reminder['event'],
                hours_before=reminder.get('hours_before')
            )

            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1

            results['details'].append({
                'user': reminder['user_email'],
                'event': reminder['event']['name'],
                'success': success,
                'timestamp': datetime.now().isoformat()
            })

        logger.info(f"Batch complete: {results['successful']} sent, {results['failed']} failed")
        return results

    def get_upcoming_reminders(self,
                              events: List[Dict],
                              registrations: List[Dict],
                              window_hours: int = 24) -> List[Dict]:
        """
        Determine which reminders need to be sent

        Args:
            events: List of events (dict format)
            registrations: List of registrations (user-event pairs)
            window_hours: Hours before event to check

        Returns:
            List of reminders to send
        """
        reminders = []
        now = datetime.now()
        target_end = now + timedelta(hours=window_hours)

        event_dict = {e['id']: e for e in events}
        sent_tracker = set()

        for reg in registrations:
            event = event_dict.get(reg['event_id'])
            if not event:
                continue

            try:
                event_date = datetime.fromisoformat(event['date_begin'].replace('Z', '+00:00'))

                # Check if event is within reminder window
                if now <= event_date <= target_end:
                    key = (reg['user_id'], event['id'])
                    if key not in sent_tracker:
                        reminders.append({
                            'user_email': reg['user_email'],
                            'user_name': reg['user_name'],
                            'event': event,
                            'hours_before': window_hours,
                            'scheduled_time': (event_date - timedelta(hours=window_hours)).isoformat()
                        })
                        sent_tracker.add(key)

            except Exception as e:
                logger.error(f"Error processing registration: {e}")

        return reminders

    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = "Welcome to EventMind!"

        html_content = self._render_template(
            'welcome_template.html',
            user_name=user_name
        )

        success = self._send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content
        )

        if success:
            self.stats['by_type']['welcome'] += 1

        return success

    def get_stats(self) -> Dict:
        """Get notification statistics"""
        return self.stats

    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            if self.config['smtp']['username']:
                server = smtplib.SMTP(
                    self.config['smtp']['server'],
                    self.config['smtp']['port']
                )
                if self.config['smtp'].get('use_tls', True):
                    server.starttls()
                server.login(
                    self.config['smtp']['username'],
                    self.config['smtp']['password']
                )
                server.quit()
            else:
                server = smtplib.SMTP('localhost', 1025)
                server.quit()

            logger.info("SMTP connection test successful")
            return True

        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False


    # для оды

    def send_reminder_odoo(self, env, registration_id: int, base_url: Optional[str] = None) -> Dict:
        """
        Send reminder for an Odoo event.registration record

        Args:
            env: Odoo environment (self.env from model)
            registration_id: ID of event.registration record
            base_url: Optional base URL override

        Returns:
            dict: {'success': bool, 'message': str, 'registration_id': int}
        """
        try:
            reg = env['event.registration'].sudo().browse(registration_id)
            if not reg.exists():
                return {'success': False, 'message': f'Registration {registration_id} not found', 'registration_id': registration_id}
            
            if reg.reminder_sent:
                return {'success': False, 'message': 'Reminder already sent', 'registration_id': registration_id}

            event = reg.event_id
            partner = reg.partner_id
            
            if not partner.email:
                logger.warning(f"No email for partner {partner.id}")
                return {'success': False, 'message': 'No email for partner', 'registration_id': registration_id}
            
            # Convert Odoo record to dict (compatible with send_reminder)
            event_dict = {
                'id': event.id,
                'name': event.name or '',
                'date_begin': event.date_begin.isoformat() if event.date_begin else '',
                'date_end': event.date_end.isoformat() if event.date_end else None,
                'location': event.location or '',
                'description': event.note or '',
                'url': f"{base_url or self.base_url}/event/event/{event.id}"
            }
            
            # Use override base_url if provided
            original_base_url = self.base_url
            if base_url:
                self.base_url = base_url
            
            success = self.send_reminder(
                user_email=partner.email,
                user_name=partner.name or 'Participant',
                event=event_dict,
                hours_before=24
            )
            
            # Restore base_url
            self.base_url = original_base_url
            
            if success:
                # Mark as sent in Odoo
                reg.write({'reminder_sent': True})
                logger.info(f"Reminder sent for Odoo registration #{registration_id}")
                return {'success': True, 'message': 'Reminder sent', 'registration_id': registration_id}
            else:
                return {'success': False, 'message': 'Failed to send email', 'registration_id': registration_id}
                
        except Exception as e:
            logger.error(f"Error in send_reminder_odoo: {type(e).__name__}: {e}")
            return {'success': False, 'message': f'Error: {str(e)}', 'registration_id': registration_id}

    def get_registrations_for_reminder_odoo(self, env, window_hours: int = 24) -> List[int]:
        """
        Get list of registration IDs that need reminders (Odoo version)

        Args:
            env: Odoo environment
            window_hours: Hours before event to check

        Returns:
            list: Registration IDs ready for reminder
        """
        from odoo import fields
        
        now = fields.Datetime.now()
        window_end = fields.Datetime.add(now, hours=window_hours)
        
        registrations = env['event.registration'].sudo().search([
            ('event_id.date_begin', '>=', now),
            ('event_id.date_begin', '<=', window_end),
            ('state', 'in', ['open', 'done']),
            ('reminder_sent', '=', False),
            ('partner_id.email', '!=', False),
        ])
        
        logger.info(f"Found {len(registrations)} registrations due for reminder")
        return registrations.ids

    def send_batch_reminders_odoo(self, env, registration_ids: List[int], base_url: Optional[str] = None) -> Dict:
        """
        Send reminders for multiple Odoo registrations

        Args:
            env: Odoo environment
            registration_ids: List of event.registration IDs
            base_url: Optional base URL for links

        Returns:
            dict: Batch sending statistics
        """
        results = {
            'total': len(registration_ids),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for reg_id in registration_ids:
            result = self.send_reminder_odoo(env, reg_id, base_url)
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
            results['details'].append(result)
        
        logger.info(f"Odoo batch complete: {results['successful']} sent, {results['failed']} failed")
        return results


    # для фронта

    def api_send_reminder(self, payload: Dict) -> Dict:
        """
        API endpoint handler for sending a reminder
        
        Expected payload:
        {
            "user_email": "user@example.com",
            "user_name": "John Doe",
            "event": {
                "id": 123,
                "name": "Event Name",
                "date_begin": "2024-04-01T18:00:00+03:00",
                "location": "Moscow",
                "description": "Event description"
            },
            "hours_before": 24  // optional
        }
        
        Returns:
        {
            "success": true,
            "message": "Reminder sent",
            "data": {...}
        }
        """
        try:
            required = ['user_email', 'user_name', 'event']
            for field in required:
                if field not in payload:
                    return {'success': False, 'error': f'Missing field: {field}', 'code': 400}
            
            event = payload['event']
            if 'id' not in event or 'name' not in event or 'date_begin' not in event:
                return {'success': False, 'error': 'Event missing required fields', 'code': 400}
            
            success = self.send_reminder(
                user_email=payload['user_email'],
                user_name=payload['user_name'],
                event=event,
                hours_before=payload.get('hours_before')
            )
            
            if success:
                return {'success': True, 'message': 'Reminder sent', 'code': 200}
            else:
                return {'success': False, 'error': 'Failed to send email', 'code': 500}
                
        except Exception as e:
            logger.error(f"API error in api_send_reminder: {e}")
            return {'success': False, 'error': f'Internal error: {str(e)}', 'code': 500}

    def api_get_stats(self) -> Dict:
        """
        API endpoint for notification statistics
        
        Returns:
        {
            "success": true,
            "data": {
                "total_sent": 100,
                "successful": 95,
                "failed": 5,
                "by_type": {...}
            }
        }
        """
        return {
            'success': True,
            'data': self.get_stats(),
            'code': 200
        }

    def api_test_connection(self) -> Dict:
        """
        API endpoint for testing SMTP connection
        
        Returns:
        {
            "success": true,
            "message": "Connection successful",
            "code": 200
        }
        """
        success = self.test_connection()
        if success:
            return {'success': True, 'message': 'SMTP connection OK', 'code': 200}
        else:
            return {'success': False, 'error': 'SMTP connection failed', 'code': 500}

    def api_get_ics(self, event: Dict) -> Dict:
        """
        API endpoint for generating ICS content
        
        Args:
            event: Event dictionary
            
        Returns:
        {
            "success": true,
            "data": {
                "content": "BEGIN:VCALENDAR...",
                "filename": "event_123.ics",
                "content_type": "text/calendar"
            }
        }
        """
        try:
            content = self.ics_gen.generate_ics(event)
            return {
                'success': True,
                'data': {
                    'content': content,
                    'filename': f"event_{event.get('id', 'unknown')}.ics",
                    'content_type': 'text/calendar; charset=utf-8'
                },
                'code': 200
            }
        except Exception as e:
            logger.error(f"API error in api_get_ics: {e}")
            return {'success': False, 'error': f'Failed to generate ICS: {str(e)}', 'code': 500}


# Global instance (singleton pattern)
_notifier_instance: Optional[Notifier] = None

def get_notifier(config_path: Optional[str] = None, base_url: Optional[str] = None) -> Notifier:
    """
    Get or create the global notifier instance
    
    Args:
        config_path: Path to config file
        base_url: Base URL for absolute links
    
    Returns:
        Notifier instance
    """
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = Notifier(config_path, base_url)
    return _notifier_instance


def reset_notifier():
    """Reset the global instance (useful for testing)"""
    global _notifier_instance
    _notifier_instance = None
