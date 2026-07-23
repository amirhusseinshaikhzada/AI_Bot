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
    print(f"--- 5. Inside handle_message. User ID: {message.from_user.id} ---")
    
    try:
        user = db.get_user(message.from_user.id)
        print(f"--- 6. Database check done. User found: {bool(user)} ---") # بررسی وجود کاربر
        
        if not user:
            print("--- 7. User not found in DB. Sending /start prompt ---")
            bot.reply_to(message, "Please use /start first.")
            return
        
        # بقیه کد شما...
        print("--- 8. Proceeding to AI/Logic ---")
        bot.reply_to(message, "Hello! I am working!") # یک پاسخ ساده برای تست
        
    except Exception as e:
        print(f"!!! ERROR in handle_message: {e}")

# --- بخش تنظیمات Webhook (اتصال تلگرام به Flask) ---

# --- بخش تنظیمات Webhook (اتصال تلگرام به Flask) ---

# فقط یک مسیر اصلی تعریف می‌کنیم که هم GET (برای تست) و هم POST (برای تلگرام) را بپذیرد
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        print("--- 1. POST Request Received ---") # لاگ مرحله اول
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            print("--- 2. JSON Data Received ---") # لاگ مرحله دوم
            update = telebot.types.Update.de_json(json_string)
            print(f"--- 3. Update Decoded: {update.message.text if update.message else 'No message text'} ---") # لاگ متن پیام
            
            # در تابع webhook
            try:
                print("--- Before bot.process_new_updates ---")
                bot.process_new_updates([update])
                print("--- After bot.process_new_updates ---")
           except Exception as e:
               print(f"!!! CRITICAL ERROR: {e}")
                
            return 'OK', 200
        print("--- Error: Not a JSON Request ---")
        return 'Bad Request', 400
    return "Bot is running!"

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
