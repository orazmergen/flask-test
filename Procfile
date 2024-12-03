# Установка зависимостей
install:
	pip install -r requirements.txt

# Команда для инициализации базы данных
migrate:
	python db.py

web: gunicorn app:app
