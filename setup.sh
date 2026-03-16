#!/bin/bash
echo "🚀 Налаштування Django проекту..."

# Встановлення залежностей
pip install django

# Міграції
python manage.py migrate

# Завантаження тестових даних
python manage.py loaddata blog/fixtures/initial_data.json

echo ""
echo "✅ Готово! Тепер створіть суперкористувача:"
echo "   python manage.py createsuperuser"
echo ""
echo "Потім запустіть сервер:"
echo "   python manage.py runserver"
echo ""
echo "Відкрийте браузер: http://127.0.0.1:8000/"
