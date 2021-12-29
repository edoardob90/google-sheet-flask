import os
import re
import requests
from flask import Blueprint, current_app, request, jsonify

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

# FIXME: uses Telegram bot's token as a url prefix if not None, otherwise use '/tg'. This should be enforced, not optional
bp = Blueprint('telegram', __name__, url_prefix=(f'/{TELEGRAM_BOT_TOKEN}' or '/tg'))

telegram_api_url = "https://api.telegram.org/bot{token}/"

def send_message(chat_id, text):
    """Send a message via Telegram API to `chat_id`"""
    url = telegram_api_url.format(token=TELEGRAM_BOT_TOKEN)
    
    payload = {
        "method": "sendMessage",
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    response = requests.post(url, data=payload)
    
    if response.status_code == requests.codes.ok:
        current_app.logger.info(f"Message sent to {chat_id} via Telegram Bot API.")
        return response.json()
    else:
        current_app.logger.error("Error occurred while sending message via Telegram Bot API.")
        return jsonify({"ok": False, "status_code": response.status_code, "reason": response.reason})

def get_chat_id(request: dict):
    """Retreive the `chat_id` of an Update object"""
    update = request.get('callback_query') or request.get('message')
    if update:
        return update['from']['id']

@bp.route('/echo', methods=['POST'])
def echo_message():
    payload = request.get_json()
    user_id = get_chat_id(payload)
    current_app.logger.info(f"Telegram Webhook: update received from user '{user_id}'.")

    if payload.get('message'):
        return send_message(user_id, f"Echoed message: {payload['message']['text']}")
    else:
        return send_message(user_id, "The update received was not of Message type.")   