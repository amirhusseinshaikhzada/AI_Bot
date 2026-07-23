import os
from flask import Flask, request
import telebot
from telebot import types
from database import DatabaseManager
from ai_handler import AIHandler
from dotenv import load_dotenv

load_dotenv()

# تنظیمات اولیه
app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_TOKEN")
# در هاست، آدرس باید HTTPS باشد. برای تست محلی از آدرس خود استفاده کنید.
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 

bot = telebot.TeleBot(TOKEN)
db = DatabaseManager()
ai = AIHandler()

LANGUAGES = {
    'fa': 'Persian (فارسی)',
    'en': 'English',
    'ar': 'Arabic',
    'zh': 'Chinese',
    'fr': 'French',
    'ru': 'Russian',
    'es': 'Spanish'
}

# --- بخش منطق ربات (Telebot Handlers) ---

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for code, name in LANGUAGES.items():
        markup.add(types.InlineKeyboardButton(name, callback_data=f"lang_{code}"))
    bot.send_message(message.chat.id, "Select Language / انتخاب زبان:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def callback_lang(call):
    lang_code = call.data.split('_')[1]
    user_id = call.message.from_user.id
    db.save_user(user_id, call.message.from_user.first_name, 
                 call.message.from_user.last_name or "", lang_code)
    bot.answer_callback_query(call.id)
    bot.edit_message_text(f"✅ Language set to {LANGUAGES[lang_code]}", 
                          call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "I received your message! Testing...")
    
    user_lang = user[3]
    bot.send_chat_action(message.chat.id, 'typing')
    ai_response = ai.get_response(message.text, user_lang)
    bot.reply_to(message, ai_response)

# --- بخش تنظیمات Webhook (اتصال تلگرام به Flask) ---

# --- بخش تنظیمات Webhook (اتصال تلگرام به Flask) ---

# فقط یک مسیر اصلی تعریف می‌کنیم که هم GET (برای تست) و هم POST (برای تلگرام) را بپذیرد
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        # اگر تلگرام درخواست POST فرستاد (پیام جدید)
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return 'OK', 200
        else:
            return 'Bad Request', 400
    
    # اگر کسی آدرس را در مرورگر باز کرد (GET)
    return "Bot is running! Webhook is active."

# تابع برای تنظیم اولیه Webhook
def set_webhook():
    bot.remove_webhook()
    # توجه: اینجا دیگر از TOKEN در انتهای URL استفاده نمی‌کنیم تا با مسیر اصلی ما یکی باشد
    bot.set_webhook(url=WEBHOOK_URL) 
    print(f"Webhook set to: {WEBHOOK_URL}")

if __name__ == "__main__":
    # در اولین اجرا، Webhook را ست می‌کنیم
    set_webhook()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
