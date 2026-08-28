import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

TOKEN = "8935546734:AAHolOJ5FvdRC5li3YVFTDmjdEJ8CIpBa8c"
bot = telebot.TeleBot(TOKEN)

REKLAMA_TEXT = (
    "📚 **Kitob sevuvchilar uchun maxsus loyiha!**\n\n"
    "📖 Har hafta yangi kitob yutib olish imkoniyati\n"
    "🌱 Aktiv bo'lib barg yig'asiz va ularni kitoblarga almashtirasiz!\n"
    "💖 Adminga rahmat aytish va tekin kitoblarga ega bo'lish uchun safimizga qo'shiling! ✨\n\n"
    "Haqiqiy kitobxon bo'lsangiz, bu imkoniyatni o'tkazib yubormang! 🎉\n\n"
    "👇 **Qo'shilish uchun havola** 👇\n"
    "https://t.me/Varaq_loyihasi_bot?start=896dbde3"
)


user_urls = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Salom! 👋\n"
        "Men All_skachat botiman. 🚀\n\n"
        "Menga Instagram, TikTok yoki YouTube'dan video havolasini (link) yuboring, men uni yuklab beraman! 📥"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text or ""
    if "http" not in text:
        bot.reply_to(message, "Iltimos, to'g'ri video havolasini (link) yuboring!")
        return

    words = text.split()
    url = None
    for word in words:
        if "http" in word:
            url = word
            break

    user_urls[message.chat.id] = url

    markup = InlineKeyboardMarkup()
    btn_video = InlineKeyboardButton("🎬 Video yuklash", callback_data="dl_video")
    btn_audio = InlineKeyboardButton("🎵 Audiosini yuklash (MP3)", callback_data="dl_audio")
    markup.add(btn_video, btn_audio)

    bot.reply_to(message, "Nimani yuklab beray? Tanlang 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["dl_video", "dl_audio"])
def process_download(call):
    chat_id = call.message.chat.id
    url = user_urls.get(chat_id)

    if not url:
        bot.answer_callback_query(call.id, "Havola topilmadi, qaytadan yuboring.")
        return

    bot.answer_callback_query(call.id, "Jarayon boshlandi...")
    bot.edit_message_text("⏳ Yuklab olinmoqda, iltimos kuting...", chat_id=chat_id, message_id=call.message.message_id)

    if call.data == "dl_video":
        file_name = f"video_{chat_id}.mp4"
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': file_name,
            'quiet': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open(file_name, 'rb') as file:
                bot.send_video(chat_id, file, caption="✨ Videongiz tayyor!")
            
            bot.send_message(chat_id, REKLAMA_TEXT, parse_mode="Markdown")

        except Exception as e:
            bot.send_message(chat_id, f"❌ Videoni yuklab bo'lmadi.\nXatolik: {e}")
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    elif call.data == "dl_audio":
        file_name = f"audio_{chat_id}.m4a"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_name,
            'quiet': True,
            'nocheckcertificate': True,
            'source_address': '0.0.0.0',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open(file_name, 'rb') as file:
                bot.send_audio(chat_id, file, caption="🎶 Audiongiz tayyor!")
            
            bot.send_message(chat_id, REKLAMA_TEXT, parse_mode="Markdown")

        except Exception as e:
            bot.send_message(chat_id, f"❌ Audioni yuklab bo'lmadi.\nXatolik: {e}")
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

print("Bot ishga tushdi...")
bot.infinity_polling(timeout=20, long_polling_timeout=10)
