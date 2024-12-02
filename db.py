import sqlite3

# Соединение с базой данных (если файла базы данных нет, он будет создан)
conn = sqlite3.connect('conversations.db')

# Создание курсора для выполнения SQL команд
cursor = conn.cursor()

# Создание таблицы для хранения истории диалогов
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversation_history (
    user_id TEXT PRIMARY KEY,
    history TEXT
)
''')

# Сохранение изменений и закрытие соединения
conn.commit()

# Создание таблицы для хранения истории диалогов
cursor.execute('''
CREATE TABLE IF NOT EXISTS gptsystem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    system_text TEXT
)
''')
conn.commit()
conn.close()