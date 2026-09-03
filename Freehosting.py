import os
import subprocess
import telebot

# ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8705628494:AAHFfe-Bc5PGdabbzYllKiaAsxWqScK9Cs0"

bot = telebot.TeleBot(BOT_TOKEN)

# إنشاء مجلد مخصص لحفظ الملفات المرفوعة
UPLOAD_DIR = "hosted_scripts"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 **مرحباً بك في بوت استضافة وتشغيل ملفات بايثون!**\n\n"
        "📁 أرسل لي أي ملف بايثون بصلامة (`.py`) وسأقوم باستضافته، "
        "تشغيله، وإرسال مخرجات الكود إليك فوراً."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")


@bot.message_handler(content_types=['document'])
def handle_python_file(message):
    try:
        file_name = message.document.file_name

        # التحقق من أن الملف المرسل هو ملف بايثون
        if not file_name.endswith('.py'):
            bot.reply_to(message, "⚠️ يرجى إرسال ملف يتضمن امتداد `.py` فقط.")
            return

        bot.reply_to(message, f"⏳ جاري تحميل وتشغيل الملف: `{file_name}`...", parse_mode="Markdown")

        # تنزيل الملف من سيرفرات تلجرام
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # حفظ الملف في مجلد الاستضافة المحلي
        saved_file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(saved_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # تشغيل الملف المرفوع باستخدام subprocess
        # تم تحديد مهلة زمنية (timeout) بـ 15 ثانية لمنع الحلقات اللانهائية
        result = subprocess.run(
            ['python', saved_file_path],
            capture_output=True,
            text=True,
            timeout=15
        )

        stdout = result.stdout
        stderr = result.stderr

        # صياغة النتيجة وإرسالها للمستخدم
        response = f"🖥️ **نتيجة تشغيل الملف `{file_name}`:**\n\n"

        if stdout:
            response += f"📋 **المخرجات" (Output):**\n
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
3. افتح التلجرام، توجه إلى البوت الخاص بك، وأرسل له أي ملف بايثون بسيط (مثال: ملف يحتوي على `print("Hello World")`).
4. سيقوم البوت باستلام الملف، تنفيذه، وإعادة النتيجة إليك في الشات مباشرة.

---

### 💡 ملاحظات أمنية واستضافة دائمية:
* **الأمان:** تشغيل أكواد بايثون من مستخدمين آخرين على جهازك مباشرة يعتبر خطراً أمنياً، حيث يمكن للكود المرفوع الوصول لملفات النظام. يُفضل تشغيل البوت داخل بيئة معزولة مثل **Docker Container** أو **VPS**.
* **الاستضافة الدائمة:** لتشغيل البوت 24/7 يمكنك رفع سكريبت البوت على خوادم VPS (مثل DigitalOcean أو Linode) أو منصات استضافة مثل Render أو PythonAnywhere.
