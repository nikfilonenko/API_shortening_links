# URL Shortener Service

Сервис для сокращения URL с асинхронным API, кешированием и аналитикой переходов.

## 📌 Основные возможности

- Создание коротких ссылок (с возможностью кастомных алиасов)
- Редирект на оригинальные URL
- Аналитика переходов (по дням/часам/устройствам)
- JWT-аутентификация пользователей
- Группировка ссылок по категориям
- Автоматическое продление ссылок
- Кеширование в Redis

## 🚀 Технологический стек

- **Backend**: Python 3.12 + FastAPI
- **База данных**: PostgreSQL 15 + asyncpg
- **Кеширование**: Redis 7
- **Аутентификация**: JWT
- **Контейнеризация**: Docker + Docker Compose
- **Тестирование**: pytest

## 🛠 Установка и запуск

### Требования
- Docker 20.10+
- Docker Compose 2.0+

### Запуск в Docker
```bash
git clone https://github.com/your-repo/url-shortener.git
cd url-shortener
docker-compose up -d --build
```

Сервис будет доступен по адресу: http://localhost:8000/api/docs

- Переменные окружения

```python
DB_CONNECTION=postgresql+asyncpg://user:password@db:5432/dbname
REDIS_CONNECTION=redis://redis:6379/0
JWT_SECRET=your-secret-key
```


#### 📚 API Документация

- Доступна после запуска по адресу:

Swagger UI: /api/docs

ReDoc: /api/redoc

OpenAPI Schema: /api/openapi.json


#### 🧪 Тестирование

```
docker-compose exec app pytest
```

#### Структура проекта

```python
.
├── app/
│   ├── api/           # Эндпоинты API
│   ├── db/            # Работа с БД
│   ├── models/        # SQLAlchemy модели
│   ├── schemas/       # Pydantic модели
│   ├── services/      # Бизнес-логика
│   ├── settings/      # Конфигурация
│   └── main.py        # Точка входа
├── tests/             # Тесты
├── docker-compose.yml # Конфигурация Docker
└── Dockerfile         # Сборка образа
```

#### 🔧 Примеры запросов

Создание короткой ссылки

```python
curl -X POST "http://localhost:8000/api/links/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_url": "https://example.com", "custom_key": "my-link"}'
```

#### 📈 Мониторинг
Prometheus метрики: /metrics

Health check: /health