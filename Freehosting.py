import os
import subprocess
import telebot
import signal
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

BOT_TOKEN = os.getenv("8705628494:AAHFfe-Bc5PGdabbzYllKiaAsxWqScK9Cs0")
if not BOT_TOKEN:
    raise ValueError("❌ التوكن غير موجود! يرجى إضافته في ملف .env")

bot = telebot.TeleBot(BOT_TOKEN)

UPLOAD_DIR = "hosted_scripts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# قاموس لتتبع العمليات (البوتات) التي تعمل حالياً
# الشكل: {PID: "file_name.py"}
running_bots = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 **مرحباً بك في مدير استضافة البوتات!**\n\n"
        "📁 أرسل أي ملف `.py` وسأقوم بتشغيله كـ (بوت في الخلفية).\n"
        "🛠️ **الأوامر المتاحة:**\n"
        "`/list` - عرض جميع البوتات التي تعمل حالياً.\n"
        "`/stop <PID>` - إيقاف بوت معين باستخدام رقم العملية الخاصة به."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['list'])
def list_running_bots(message):
    if not running_bots:
        bot.reply_to(message, "ℹ️ لا يوجد أي بوت يعمل في الخلفية حالياً.")
        return
    
    text = "🤖 **البوتات التي تعمل حالياً:**\n\n"
    for pid, name in running_bots.items():
        text += f"🔹 الملف: `{name}` | رقم العملية (PID): `{pid}`\n"
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['stop'])
def stop_bot_process(message):
    try:
        # استخراج رقم الـ PID من الرسالة (مثال: /stop 1234)
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "⚠️ يرجى إدخال رقم العملية. مثال:\n`/stop 1234`", parse_mode="Markdown")
            return
        
        pid_to_stop = int(command_parts[1])
        
        if pid_to_stop in running_bots:
            # إرسال إشارة إغلاق للعملية
            os.kill(pid_to_stop, signal.SIGTERM)
            bot_name = running_bots.pop(pid_to_stop)
            bot.reply_to(message, f"✅ تم إيقاف البوت `{bot_name}` (PID: {pid_to_stop}) بنجاح.", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ رقم العملية غير موجود أو البوت لا يعمل حالياً.")
            
    except ValueError:
        bot.reply_to(message, "❌ يرجى إدخال رقم صحيح للعملية.")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء إيقاف البوت: {e}")

@bot.message_handler(content_types=['document'])
def handle_python_file(message):
    try:
        file_name = message.document.file_name

        if not file_name.endswith('.py'):
            bot.reply_to(message, "⚠️ يرجى إرسال ملف يتضمن امتداد `.py` فقط.")
            return

        bot.reply_to(message, f"⏳ جاري تحميل وتشغيل البوت: `{file_name}` في الخلفية...", parse_mode="Markdown")

        # تنزيل الملف
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        saved_file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(saved_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # إنشاء ملف لحفظ مخرجات وأخطاء البوت المرفوع (Logs)
        log_file_path = os.path.join(UPLOAD_DIR, f"{file_name}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8')

        # تشغيل البوت في الخلفية باستخدام Popen (لاحظ أننا لم نستخدم timeout)
        # ملاحظة: إذا كنت تستخدم سيرفر لينكس، غيّر 'python' إلى 'python3'
        process = subprocess.Popen(
            ['python3', saved_file_path], 
            stdout=log_file, 
            stderr=log_file
        )

        # حفظ رقم العملية في القاموس
        running_bots[process.pid] = file_name

        response = (
            f"✅ **تم تشغيل البوت بنجاح في الخلفية!**\n\n"
            f"📁 الملف: `{file_name}`\n"
            f"🔑 رقم العملية (PID): `{process.pid}`\n\n"
            f"🛑 لإيقاف هذا البوت لاحقاً، أرسل الأمر:\n`/stop {process.pid}`"
        )
        bot.reply_to(message, response, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء المعالجة: `{str(e)}`", parse_mode="Markdown")

print("🚀 مدير البوتات يعمل الآن...")
bot.infinity_polling()
