# 🔒 Чеклист безопасности для деплоя

## ⚠️ ОБЯЗАТЕЛЬНО перед публикацией в интернет!

### 1. Переменные окружения (КРИТИЧНО!)

На сервере (Render/Heroku) установите эти переменные окружения:

```bash
SECRET_KEY=ваш_случайный_длинный_ключ_минимум_50_символов
DEBUG=False
DATABASE_URL=ваша_база_данных  # если используете PostgreSQL
```

**Как сгенерировать SECRET_KEY:**

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. База данных

✅ Для production используйте PostgreSQL, а не SQLite
✅ Регулярно делайте бэкапы базы данных
✅ Используйте сильные пароли для БД

### 3. ALLOWED_HOSTS

В `settings.py` добавьте только ваши реальные домены:

```python
ALLOWED_HOSTS = ['ваш-домен.com', 'www.ваш-домен.com']
```

### 4. CORS настройки

Проверьте что в `CORS_ALLOWED_ORIGINS` только ваши фронтенд домены:

```python
CORS_ALLOWED_ORIGINS = [
    "https://ваш-фронтенд.netlify.app",
]
```

### 5. Админ-панель

✅ Измените URL админ-панели (не используйте /admin/)
✅ Используйте сильный пароль для superuser
✅ Включите двухфакторную аутентификацию (2FA) если возможно

### 6. Медиа файлы

✅ Используйте AWS S3, Cloudinary или другой CDN для media файлов
✅ Не храните sensitive данные в media папке
✅ Настройте правильные CORS для media файлов

### 7. HTTPS

✅ Всегда используйте HTTPS в production
✅ Настройте SSL сертификат (Let's Encrypt бесплатно)
✅ Проверьте что `SECURE_SSL_REDIRECT = True`

### 8. Мониторинг

✅ Настройте логирование ошибок (Sentry)
✅ Мониторьте попытки взлома
✅ Регулярно проверяйте логи

### 9. Обновления

✅ Регулярно обновляйте Django и зависимости
✅ Подпишитесь на security уведомления Django
✅ Проверяйте уязвимости: `pip install safety && safety check`

### 10. Дополнительная защита

✅ Ограничьте количество запросов (Rate Limiting) - уже настроено
✅ Защита от SQL injection - Django ORM защищает автоматически
✅ Защита от XSS - включена
✅ Защита от CSRF - включена
✅ Защита от Clickjacking - включена

## 🚀 Команды для проверки безопасности

```bash
# Проверка настроек безопасности Django
python manage.py check --deploy

# Проверка уязвимостей в зависимостях
pip install safety
safety check

# Проверка устаревших пакетов
pip list --outdated
```

## 📋 Checklist перед деплоем

- [ ] DEBUG=False в production
- [ ] SECRET_KEY установлен через переменные окружения
- [ ] ALLOWED_HOSTS содержит только реальные домены
- [ ] CORS_ALLOWED_ORIGINS содержит только фронтенд домены
- [ ] Используется PostgreSQL (не SQLite)
- [ ] HTTPS настроен и работает
- [ ] Изменен URL админ-панели
- [ ] Настроен strong superuser пароль
- [ ] Медиа файлы на CDN (S3/Cloudinary)
- [ ] Настроено логирование (Sentry/CloudWatch)
- [ ] Сделан backup базы данных
- [ ] Все зависимости обновлены
- [ ] Проверено: `python manage.py check --deploy`

## 🔐 Что уже защищено в коде:

1. ✅ **CORS** - только разрешенные домены
2. ✅ **CSRF** - защита от подделки запросов
3. ✅ **XSS** - защита от скриптовых атак
4. ✅ **Clickjacking** - защита X-Frame-Options
5. ✅ **Rate Limiting** - ограничение запросов
6. ✅ **HTTPS Redirect** - автоматический редирект на HTTPS
7. ✅ **Secure Cookies** - cookies только через HTTPS
8. ✅ **SQL Injection** - Django ORM защищает
9. ✅ **Password Validation** - строгие требования к паролям
10. ✅ **HSTS** - принудительное использование HTTPS

## ⚡ Быстрый старт для Render.com

1. Создайте Web Service на Render
2. Подключите GitHub репозиторий
3. Установите переменные окружения:
   - `SECRET_KEY` - ваш секретный ключ
   - `DEBUG` - `False`
   - `PYTHON_VERSION` - `3.11.9`
4. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Start Command: `gunicorn config.wsgi:application`

## 📚 Полезные ссылки

- [Django Security](https://docs.djangoproject.com/en/5.0/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
