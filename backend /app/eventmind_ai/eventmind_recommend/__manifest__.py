{
    'name': 'EventMind Recommendations',
    'version': '1.0',
    'summary': 'Personalized event recommendations based on user interests',
    'depends': ['event', 'eventmind_tags'],  # зависимость от модуля Полины
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}

