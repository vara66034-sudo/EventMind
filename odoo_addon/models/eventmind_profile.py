from odoo import fields, models


class EventMindProfile(models.Model):
    _name = "eventmind.profile"
    _description = "EventMind Profile"

    name = fields.Char(required=True, default="EventMind Profile")
    user_id = fields.Many2one("res.users", required=True, ondelete="cascade")
    interests = fields.Char(
        string="Interests",
        help="Comma-separated interests used for recommendation sync.",
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "eventmind_profile_user_unique",
            "unique(user_id)",
            "Each user can have only one EventMind profile.",
        )
    ]

