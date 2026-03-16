from odoo import http
from odoo.http import request

class EventMindRecommendAPI(http.Controller):

    @http.route('/api/recommendations', type='json', auth='user', methods=['POST'])
    def get_recommendations(self):
        """Возвращает рекомендованные события для текущего пользователя."""
        user = request.env.user
        events = user.get_recommended_events(limit=10)
        data = []
        for event in events:
            data.append({
                'id': event.id,
                'name': event.name,
                'date_begin': event.date_begin.isoformat() if event.date_begin else None,
                'location': event.location,
                'description': event.description,
                'tags': [{'id': t.id, 'name': t.name} for t in event.tag_ids],
            })
        return {'result': data}

