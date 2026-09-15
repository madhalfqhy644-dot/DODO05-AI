import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

openai = OpenAI(api_key=OPENAI_API_KEY)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def ask_ai(message):
    response = openai.responses.create(
        model="gpt-5",
        instructions="""
أنت DODO، مساعد شخصي ذكي يعمل نيابةً عن صاحب الحساب في تيليجرام.

أسلوبك:
- طبيعي وودود.
- ردود قصيرة ومناسبة للمحادثة.
- استخدم اللهجة الليبية عندما تكون مناسبة.
- لا تقل إنك بوت إلا إذا سُئلت مباشرة.
- لا تخترع معلومات عن صاحب الحساب.
- إذا كانت الرسالة تحتاج معلومات غير متوفرة، اسأل سؤالاً بسيطاً للتوضيح.
""",
        input=message,
        store=False
    )

    return response.output_text.strip()


def send_message(chat_id, business_connection_id, text):
    url = f"{TELEGRAM_API}/sendMessage"

    data = {
        "chat_id": chat_id,
        "business_connection_id": business_connection_id,
        "text": text
    }

    requests.post(url, json=data, timeout=30)


@app.route("/", methods=["GET"])
def home():
    return "DODO AI is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}

    message = update.get("business_message")

    if not message:
        return "OK", 200

    text = message.get("text")
    chat = message.get("chat", {})
    business_connection_id = message.get("business_connection_id")

    if not text or not business_connection_id:
        return "OK", 200

    chat_id = chat.get("id")

    if not chat_id:
        return "OK", 200

    try:
        reply = ask_ai(text)

        if reply:
            send_message(
                chat_id,
                business_connection_id,
                reply
            )

    except Exception as e:
        print("ERROR:", e)

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
