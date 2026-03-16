from odoo import models, fields, api
from datetime import datetime

class ResUsers(models.Model):
    _inherit = 'res.users'

    interest_tag_ids = fields.Many2many(
        'event.tag',
        string='Interests',
        help='Tags that the user is interested in'
    )

    def get_recommended_events(self, limit=20):
        """Return recommended events based on user interests."""
        if not self.interest_tag_ids:
            return self.env['event.event'].search([
                ('date_begin', '>=', datetime.now())
            ], order='date_begin', limit=limit)

       
        events = self.env['event.event'].search([
            ('date_begin', '>=', datetime.now())
        ])
        user_tag_ids = set(self.interest_tag_ids.ids)
        scored = []

        for event in events:
            event_tag_ids = set(event.tag_ids.ids)
            common = user_tag_ids & event_tag_ids
            if common:
                score = len(common) / len(user_tag_ids)
                scored.append((event, score))


        scored.sort(key=lambda x: -x[1])
        return [event for event, _ in scored[:limit]]

