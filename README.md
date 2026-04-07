## EventMind — AI-ассистент для поиска мероприятий

**EventMind** помогает студентам и молодым специалистам не пропускать важные события: конференции, митапы, хакатоны, лекции. Сервис автоматически собирает мероприятия из VK и TimePad, анализирует интересы пользователя и предлагает персонализированный календарь с рекомендациями и напоминаниями.

---

### Ключевые возможности
- **Сбор данных** из VK API и TimePad API (название, дата, место, описание, ссылка, категория)
- **Автоматическое тегирование** событий (KeyBERT + spaCy)
- **Персонализированные рекомендации** на основе выбранных пользователем интересов
- **Персональный календарь** с экспортом в .ics (Google/Apple календарь)
- **Напоминания** (push / email) за 24 часа до события

---

### Пользовательский сценарий
1. Регистрация → выбор интересов (теги)
2. Получение персонализированной ленты событий
3. Добавление событий в личный календарь
4. Напоминания о предстоящих мероприятиях

---

### Технологический стек
| Компонент | Технологии |
|-----------|------------|
| **Бэкенд API** | FastAPI, Python 3.10+ |
| **Платформа данных** | Odoo + PostgreSQL |
| **Рекомендации** | Jaccard similarity + GigaChat (Function Calling) |
| **Автотегирование** | KeyBERT, Sentence‑Transformers (paraphrase-multilingual-MiniLM-L12-v2) |
| **Парсеры** | Python (requests), VK API, TimePad API, GitHub Actions (cron) |
| **Фронтенд** | React 18, JavaScript, Axios, Tailwind CSS |
| **Уведомления** | Email (SMTP), .ics генерация |
| **LLM (ИИ-агент)** | GigaChat (российская LLM, бесплатный API) |
| **Инфраструктура** | Docker, docker-compose, GitHub Actions, Railway/Vercel |
| **Расписание** | In-memory кэш (UserCalendar) |

---

### Команда и роли

| Роль | Имя | Основные задачи |
|------|-----|-----------------|
| **Тимлид + рекомендации** | Настя | Координация, рекомендательная система, API, подготовка к защите |
| **Data Engineer** | Тина | Парсеры VK/TimePad, структура БД, автоматическое обновление данных |
| **NLP/Автотегирование** | Полина | Модуль тегирования, интеграция с данными, тестирование |
| **Frontend + Уведомления** | Ксюша | React-приложение, интеграция API, .ics экспорт, напоминания |
| **UI/UX Дизайнер** | Лилия | Макеты (Figma), UI Kit, адаптивный дизайн |
| **DevOps** | Варя | Docker, развертывание Odoo, бэкапы |

---

### Структура репозитория

```
EventMind/
├── artifacts/
│   └── frontend-build/          # production-сборка frontend (готовые css/js/html)
│
├── backend/                     # серверная часть (FastAPI)
│   ├── app/
│   │   ├── agent/
│   │   │   └── core/            # базовая логика ядра агента
│   │   │
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── agent.py     # API для взаимодействия с агентом
│   │   │
│   │   ├── integrations/        # внешние интеграции
│   │   │   ├── parsers/         # парсинг событий (TimePad, VK)
│   │   │   ├── llm/
│   │   │   │   └── gigachat_service.py
│   │   │   ├── notifications/
│   │   │   │   └── email_notifier.py
│   │   │   └── calendar/
│   │   │       └── ics_generator.py
│   │   │
│   │   ├── services/            # бизнес-логика
│   │   │   ├── agent/
│   │   │   │   └── orchestrator.py
│   │   │   ├── calendar/        # работа с календарём пользователя
│   │   │   ├── recommendations/ # рекомендательная система
│   │   │   └── tagging/         # NLP: обработка и тегирование событий
│   │   │
│   │   └── main.py              # запуск FastAPI
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                    # клиентская часть (React)
│   ├── public/                  # статические файлы (index.html, иконки)
│   ├── src/
│   │   ├── app/                 # точка входа (App.js, index.js)
│   │   ├── api/                 # запросы к backend
│   │   ├── components/          # UI-компоненты (events, common, layout)
│   │   ├── pages/               # страницы приложения
│   │   ├── hooks/               # кастомные React-хуки
│   │   ├── services/
│   │   │   └── api.js           # общий API-клиент
│   │   ├── styles/
│   │   │   └── global.css
│   │   └── utils/
│   │       └── theme.js
│   │
│   ├── package.json
│   └── .env
│
├── odoo_addon/                  # Odoo-модуль
│   ├── models/
│   │   └── eventmind_profile.py
│   ├── views/
│   │   └── eventmind_profile_views.xml
│   ├── security/
│   │   └── ir.model.access.csv
│   ├── __init__.py
│   └── __manifest__.py
│
├── infra/                       # инфраструктура и деплой
│   ├── docker/
│   │   └── docker-compose.yml
│   └── scripts/
│       └── deploy.sh
│
├── config/
│   └── agent_config.json        # конфигурация агента
│
├── docs/
│   └── product/
│       └── maket.txt            # продуктовые материалы
│
├── .gitignore
└── README.md
```
