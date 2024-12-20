
# A very simple Flask Hello World app for you to get started with...

from flask import Flask,request,jsonify,render_template
from gptconfig import gpt_input, add_system_prompt,get_conversation_history, get_system_prompt
import requests


app = Flask(__name__)

@app.route('/start')
def hello():
    return "hello world"

@app.route('/prompt')
def view_prompt():
    system_prompt_text = get_system_prompt()
    return render_template('addprompt2.html', data=system_prompt_text)

@app.route('/history', methods=['GET'])
def hello_history():
    user_id = request.args.get('userid')
    data = get_conversation_history(user_id)
    return render_template('history3.html', data=data)

@app.route('/webhook', methods=['POST'])
def hello_world():
    data = request.get_json()
    chanal = os.getenv("channal_id")
    if 'messages' in data and 'authorName' not in data['messages']:
        messages = data['messages']

        messages_iter = iter(messages)
        first_message = next(messages_iter, None)

        if first_message.get('channelId')==chanal and not None and (first_message.get('chatType')!='whatsgroup'):
            if first_message.get('type')!="text":
                message_to_manager(first_message)
                return jsonify({"message":"ok"}), 200
            data_test = webhook(first_message)
            
        return jsonify({"message":"ok"}), 200
    else:
        return jsonify({"message":"other request"}), 200

def message_to_manager(first_message):
    message_client = webhook(first_message, gpt_answer = 'хорошо, минутку')
    client_id = first_message.get('chatId')
    print('Finish text = ',message_client)
    first_message['chatId'] = os.getenv("admin_phone")
    message_manager = webhook(first_message, gpt_answer = f'Посмотри медиа файл, {first_message.get("contentUri")} \n а тут переписка - {os.getenv("BASE_URL")}/history?userid={client_id} \n Кстати, а вот и номер клиента +{client_id}')

def webhook(first_message, gpt_answer = 'code_gpt_base'):
    if gpt_answer == 'code_gpt_base':
        gpt_data = {}
        gpt_data['text'] = first_message.get('text')
        gpt_data['user_id'] = first_message.get('chatId')
        gpt_answer = gpt_input(gpt_data)

    json_data = {
                'channelId': first_message.get('channelId'),#'refMessageId': first_message.get('messageId'),
                'chatId': first_message.get('chatId'),
                'chatType': 'whatsapp',
                'text': f'{gpt_answer}',
                }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("wazzap_api_key")}',
    }
    try:
        response = requests.post("https://api.wazzup24.com/v3/message", headers=headers, json=json_data)
        response_data = response.json
    except Exception as e:
        response_data = e
    return {"message":f"{gpt_answer}","response_text":f"{response_data}"}

@app.route('/add', methods=['POST'])
def webhook_add_system():
    data = request.json
    prompt_text = data['system_prompt']
    if add_system_prompt(prompt_text):
        return jsonify({"message":"ok"}), 200
    else:
        return jsonify({"message":"not success"}), 400


if __name__ == '__main__':

    app.run(debug=True,port=8000)
