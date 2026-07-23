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
    user = db.get_user(message.from_user.id)
    if not user:
        bot.reply_to(message, "Please use /start first.")
        return
    
    user_lang = user[3]
    bot.send_chat_action(message.chat.id, 'typing')
    ai_response = ai.get_response(message.text, user_lang)
    bot.reply_to(message, ai_response)

# --- بخش تنظیمات Webhook (اتصال تلگرام به Flask) ---

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    # این تابع پیام‌ها را از تلگرام می‌گیرد و به کتابخانه Telebot می‌دهد
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '!', 200
    else:
        return '!', 400

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # اینجا باید منطق دریافت پیام از تلگرام قرار بگیرد
        # یا اگر از کتابخانه Telebot استفاده می‌کنید، 
        # باید تابع webhook را اینجا صدا بزنید
        bot.process_new_updates() 
        return "OK", 200
    return "Bot is running!"

# تابع برای تنظیم اولیه Webhook
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    print(f"Webhook set to: {WEBHOOK_URL}/{TOKEN}")

if __name__ == "__main__":
    # در اولین اجرا، Webhook را ست می‌کنیم
    # نکته: در هاست واقعی، این کار را فقط یکبار انجام دهید
    set_webhook()
    
    # اجرای Flask
    # پورت باید با پورت هاست شما (مثلا 5000 یا 8080) هماهنگ باشد
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
