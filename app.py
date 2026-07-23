import os
import telebot
from flask import Flask, request
from database import db  # وارد کردن مدیریت دیتابیس

# تنظیمات اولیه
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN is not set in environment variables!")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- بخش منطق ربات (Bot Logic) ---

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    print(f"--- Command /start received from {user_id} ---")
    
    # ذخیره کاربر در دیتابیس
    db.add_user(user_id, username, first_name)
    
    bot.reply_to(message, f"سلام {first_name}! خوش آمدید. ربات با موفقیت فعال شد.")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    print(f"--- Message received: '{message.text}' from {user_id} ---")
    
    # بررسی اینکه آیا کاربر در دیتابیس هست یا خیر
    user = db.get_user(user_id)
    
    if user:
        # اینجا می‌توانید منطق AI یا سایر بخش‌ها را اضافه کنید
        bot.reply_to(message, "پیام شما دریافت شد. (در حال پردازش...)")
    else:
        bot.reply_to(message, "لطفاً ابتدا دستور /start را ارسال کنید.")

# --- بخش سرور Flask (Webhook Routing) ---

@app.route('/', methods=['GET'])
def health_check():
    return "Bot is Alive!", 200

@app.route('/', methods=['POST'])
def webhook():
    print("--- 1. POST Request Received from Telegram ---")
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        print("--- 2. JSON Data Received ---")
        
        try:
            update = telebot.types.Update.de_json(json_string)
            print(f"--- 3. Update Decoded: {update.message.text if update.message else 'Non-text message'} ---")
            
            bot.process_new_updates([update])
            print("--- 4. process_new_updates Completed ---")
            return 'OK', 200
        except Exception as e:
            print(f"!!! Error processing update: {e}")
            return 'Error', 500
    else:
        return 'Not a valid request', 400

if __name__ == '__main__':
    # برای اجرا در لوکال (Local)
    app.run(port=10000)
