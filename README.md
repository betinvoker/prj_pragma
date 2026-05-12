# prj_pragma

## Требования

- Python 3.10+
- PostgreSQL 14+
- Redis (опционально, для кэширования)
- Git

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/betinvoker/prj_pragma.git
cd prj_pragma
```

Или, если папка уже существует локально, перейдите в неё:

```bash
cd C:\Users\betin\Desktop\prj_pragma
```

### 2. Создание виртуального окружения

```bash
python -m venv env
```

Активация:
- Windows: `env\Scripts\activate`
- Linux/Mac: `source env/bin/activate`

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных PostgreSQL

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE postgres;
```

При необходимости измените параметры подключения в `digital_office/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

### 5. Миграции

```bash
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Запуск сервера

```bash
python manage.py runserver
```

Откройте http://127.0.0.1:8000 в браузере.

## Структура проекта

```
prj_pragma/
├── digital_office/       # Основное Django-приложение
│   ├── core/             # Модули приложения
│   ├── templates/        # HTML-шаблоны
│   └── settings.py       # Настройки
├── media/                # Загруженные файлы
├── env/                  # Виртуальное окружение
├── manage.py             # Django CLI
├── requirements.txt      # Зависимости
└── README.md             # Этот файл
```

## API

Проект использует Django REST Framework с JWT-аутентификацией.

Эндпоинты аутентификации:
- `POST /api/token/` — получение токенов
- `POST /api/token/refresh/` — обновление access-токена

## Команды Django

```bash
python manage.py migrate          # Миграции
python manage.py createsuperuser  # Создание админа
python manage.py collectstatic     # Сбор статики
python manage.py shell            # Интерактивная консоль
```
