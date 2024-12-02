import sqlite3, json
from openai import OpenAI

client = OpenAI(api_key='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')

def get_conversation_history(user_id):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT history FROM conversation_history WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
    except Exception as e:
        print(f"when we find history have error ** {e}")
        row=None
    conn.close()
    if row:
        return json.loads(row[0])
    return []

def save_conversation_history(user_id, history):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO conversation_history (user_id, history) VALUES (?, ?)
    ''', (f"{user_id}", json.dumps(history)))
    conn.commit()
    conn.close()

def create_gptsystem_table():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_history (
        user_id TEXT PRIMARY KEY,
        history TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_system_prompt(prompt):
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO gptsystem (system_text)
        VALUES (?)
        ''', (prompt,))

    # Сохранение изменений в базе данных
    conn.commit()
    conn.close()
    return True

def get_system_prompt():
    conn = sqlite3.connect('conversations.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM gptsystem
        ORDER BY id DESC
        LIMIT 1
    ''')
    last_record = cursor.fetchone()
    conn.commit()
    conn.close()
    if last_record:
        system_text = last_record[1]
    else:
        system_text = "Ты тестовый ассистент, тебя зовут Куат. Отвечаешь очень коротко в 60 символов. Начало диалога приветствие и спрашиваешь имя. Максимально старайся расположить собеседника на позитивную волну"
    return system_text

def gpt_input(data_from_bitrix):
    user_message = data_from_bitrix["text"]
    print(f'User_message: {user_message}')
    user_id = data_from_bitrix["user_id"]

    conversation_history = get_conversation_history(user_id)
    
    system_prompt = get_system_prompt()

    default_conversation=[
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": system_prompt,
          }
        ]
      },
    ]
    response = client.chat.completions.create(model="gpt-4o",
    messages=default_conversation+conversation_history+[{"role": "user", "content": user_message}],
    temperature=1,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    response_format={
      "type": "text"
    })
    conversation_history.append({"role": "user", "content": user_message})
    assistant_reply = response.choices[0].message.content
    print(f'gpt response: {assistant_reply}')
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    save_conversation_history(user_id, conversation_history)
    return assistant_reply