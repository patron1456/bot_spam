#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

# ========== التحميل التلقائي للمكتبات ==========
required_packages = ['pyTelegramBotAPI', 'aiohttp', 'requests']

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except:
        pass

for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
    except ImportError:
        print(f"📦 جاري تثبيت {package}...")
        install_package(package)

import time
import json
import threading
import logging
import asyncio
import aiohttp
from typing import Dict
from functools import wraps
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from telebot import apihelper
apihelper.ENABLE_MIDDLEWARE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== الإعدادات ==========
class Config:
    # التوكن الجديد
    BOT_TOKEN = '8711627371:AAGchxGtmwwJ_k-bxORl4YdgE5Junx-3E7Q
    
    # API لسبام الرومات
    ROOM_SPAM_API = "https://patroon-1top1.onrender.com/spam?user_id={}&duration={}"
    
    ADMIN_IDS = [6840838231]
    DEVELOPER_USERNAME = "@—͟͞͞★ＰＡＴＲＯＮ"
    CHANNEL_LINK = "https://t.me/+y3zm_ZWvWbM1ZTE0"
    BOT_NAME = "—͟͞͞★ＰＡＴＲＯＮ"
    
    # إعدادات السرعة
    TIMEOUT = 5

# ========== متغيرات السبام ==========
active_spams: Dict[str, Dict] = {}
spam_stop_events: Dict[str, threading.Event] = {}

# ========== مدير سبام الرومات ==========
class SpamManager:
    
    async def send_room_spam(self, user_id: str) -> Dict:
        try:
            url = Config.ROOM_SPAM_API.format(user_id, 999999)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=Config.TIMEOUT) as response:
                    return {"success": response.status == 200, "status": response.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_room_spam(self, user_id: str, chat_id: int, stop_event: threading.Event):
        start_time = time.time()
        total_sent = 0
        total_success = 0
        status_message = None
        last_update = start_time
        
        try:
            status_message = bot.send_message(
                chat_id,
                f"🌟 **╔══════════════════════════════════════════╗**\n"
                f"🌟 **║     🔥 سـبـام رومـات - قـوة خـارقـة 🔥     ║**\n"
                f"🌟 **╠══════════════════════════════════════════╣**\n"
                f"🌟 **║** 🎯 **المستهدف:** `{user_id}`                  **║**\n"
                f"🌟 **║** 🚀 **الحالة:** جاري الإرسال...          **║**\n"
                f"🌟 **║** ⚡ **السرعة:** فورية - بدون تأخير        **║**\n"
                f"🌟 **║** 🛑 **لإيقاف:** `/stop {user_id}`          **║**\n"
                f"🌟 **╚══════════════════════════════════════════╝**",
                parse_mode='Markdown'
            )
        except:
            pass
        
        async def send_loop():
            nonlocal total_sent, total_success
            while not stop_event.is_set():
                try:
                    result = await self.send_room_spam(user_id)
                    total_sent += 1
                    if result.get('success'):
                        total_success += 1
                except:
                    total_sent += 1
        
        send_task = asyncio.create_task(send_loop())
        
        while not stop_event.is_set():
            now = time.time()
            if now - last_update >= 1.0 and status_message:
                elapsed = now - start_time
                speed = total_sent / elapsed if elapsed > 0 else 0
                
                bar_length = 20
                if total_sent > 0:
                    progress = min(100, (total_success / total_sent) * 100)
                    filled = int(bar_length * total_success // max(total_sent, 1))
                    bar = "█" * filled + "░" * (bar_length - filled)
                else:
                    bar = "░" * bar_length
                    progress = 0
                
                update_text = (
                    f"🌟 **╔══════════════════════════════════════════╗**\n"
                    f"🌟 **║     🔥 سـبـام رومـات - قـوة خـارقـة 🔥     ║**\n"
                    f"🌟 **╠══════════════════════════════════════════╣**\n"
                    f"🌟 **║** 🎯 **المستهدف:** `{user_id}`                  **║**\n"
                    f"🌟 **║** ⏱️ **المدة:** `{elapsed:.0f}` ثانية            **║**\n"
                    f"🌟 **║** 📊 **الإجمالي:** `{total_sent:,}` طلب          **║**\n"
                    f"🌟 **║** ✅ **الناجح:** `{total_success:,}`              **║**\n"
                    f"🌟 **║** ⚡ **السرعة:** `{speed:.0f}` طلب/ث             **║**\n"
                    f"🌟 **║** 📈 **النجاح:** `{progress:.1f}%`                **║**\n"
                    f"🌟 **║** ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ **║**\n"
                    f"🌟 **║** `{bar}` **║**\n"
                    f"🌟 **╠══════════════════════════════════════════╣**\n"
                    f"🌟 **║** 🔥 **يعمل بدون توقف - بدون أي تأخير** 🔥    **║**\n"
                    f"🌟 **║** 🛑 **لإيقاف:** `/stop {user_id}`          **║**\n"
                    f"🌟 **╚══════════════════════════════════════════╝**"
                )
                try:
                    bot.edit_message_text(update_text, chat_id, status_message.message_id, parse_mode='Markdown')
                except:
                    pass
                last_update = now
            
            await asyncio.sleep(0.1)
        
        send_task.cancel()
        
        elapsed = time.time() - start_time
        avg_speed = total_sent / elapsed if elapsed > 0 else 0
        success_rate = (total_success / total_sent * 100) if total_sent > 0 else 0
        
        final_text = (
            f"✅ **╔══════════════════════════════════════════╗**\n"
            f"✅ **║     ✅ تـم إيـقـاف الـسـبـام بـنـجـاح ✅      ║**\n"
            f"✅ **╠══════════════════════════════════════════╣**\n"
            f"✅ **║** 🎯 **المستهدف:** `{user_id}`                  **║**\n"
            f"✅ **║** ⏱️ **المدة:** `{elapsed:.0f}` ثانية            **║**\n"
            f"✅ **║** 📊 **الإجمالي:** `{total_sent:,}` طلب          **║**\n"
            f"✅ **║** ✅ **الناجح:** `{total_success:,}`              **║**\n"
            f"✅ **║** ⚡ **متوسط السرعة:** `{avg_speed:.0f}` طلب/ث     **║**\n"
            f"✅ **║** 📈 **نسبة النجاح:** `{success_rate:.1f}%`         **║**\n"
            f"✅ **╚══════════════════════════════════════════╝**\n\n"
            f"🌟 **╔══════════════════════════════════════════╗**\n"
            f"🌟 **║         🤖 بــوت الـسـبـام —͟͞͞★ＰＡＴＲＯＮ        ║**\n"
            f"🌟 **╠══════════════════════════════════════════╣**\n"
            f"🌟 **║**  👑 **المطور:** {Config.DEVELOPER_USERNAME}        **║**\n"
            f"🌟 **║**  📢 **قناتنا:** [انضم الآن]({Config.CHANNEL_LINK})     **║**\n"
            f"🌟 **╚══════════════════════════════════════════╝**"
        )
        try:
            await bot.send_message(chat_id, final_text, parse_mode='Markdown')
        except:
            pass

spam_manager = SpamManager()
bot = telebot.TeleBot(Config.BOT_TOKEN)

# ========== الأزرار ==========
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🚀 سبام روم", callback_data="spam_room"),
        InlineKeyboardButton("📊 الحالة", callback_data="status"),
        InlineKeyboardButton("👑 المطور", callback_data="developer"),
        InlineKeyboardButton("📢 القناة", callback_data="channel"),
        InlineKeyboardButton("❓ المساعدة", callback_data="help")
    )
    return keyboard

# ========== الأوامر ==========
@bot.message_handler(commands=['spam', 'srgo'])
def room_spam(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, 
            f"🌟 **╔══════════════════════════════════════════╗**\n"
            f"🌟 **║     🚀 سـبـام رومـات - —͟͞͞★ＰＡＴＲＯＮ🚀        ║**\n"
            f"🌟 **╠══════════════════════════════════════════╣**\n"
            f"🌟 **║**  📝 **الاستخدام:**                         **║**\n"
            f"🌟 **║**  `/spam [المعرف]` أو `/srgo [المعرف]`   **║**\n"
            f"🌟 **║**                                          **║**\n"
            f"🌟 **║**  📌 **مثال:**                             **║**\n"
            f"🌟 **║**  `/spam 123456789`                      **║**\n"
            f"🌟 **╠══════════════════════════════════════════╣**\n"
            f"🌟 **║**  🔥 **الميزات:**                          **║**\n"
            f"🌟 **║**  • سبام رومات بدون توقف                  **║**\n"
            f"🌟 **║**  • بدون أي تأخير - سرعة خارقة           **║**\n"
            f"🌟 **║**  • آلاف الطلبات في الثانية              **║**\n"
            f"🌟 **╚══════════════════════════════════════════╝**",
            parse_mode='Markdown')
        return
    
    user_id = args[1]
    chat_id = message.chat.id
    
    if not user_id.isdigit():
        bot.reply_to(message, "❌ **المعرف يجب أن يكون أرقام فقط!**", parse_mode='Markdown')
        return
    
    spam_key = f"room_{user_id}"
    if spam_key in active_spams:
        bot.reply_to(message, 
            f"⚠️ **يوجد سبام نشط للمستخدم** `{user_id}`\n🛑 استخدم `/stop {user_id}` للإيقاف",
            parse_mode='Markdown')
        return
    
    stop_event = threading.Event()
    spam_stop_events[spam_key] = stop_event
    active_spams[spam_key] = {
        'type': 'room',
        'user_id': user_id,
        'start_time': time.time(),
        'active': True,
        'stop_event': stop_event
    }
    
    control_keyboard = InlineKeyboardMarkup()
    control_keyboard.add(
        InlineKeyboardButton(f"🛑 إيقاف {user_id}", callback_data=f"stop_{user_id}"),
        InlineKeyboardButton("📊 الحالة", callback_data="status")
    )
    
    bot.reply_to(message,
        f"🚀 **╔══════════════════════════════════════════╗**\n"
        f"🚀 **║     🔥 تـم بـدء سـبـام رومـات —͟͞͞★ＰＡＴＲＯＮ 🔥   ║**\n"
        f"🚀 **╠══════════════════════════════════════════╣**\n"
        f"🚀 **║** 🎯 **المستهدف:** `{user_id}`                  **║**\n"
        f"🚀 **║** ⚡ **يعمل بدون توقف - بدون أي تأخير**     **║**\n"
        f"🚀 **║** 🔥 **سرعة خارقة - آلاف الطلبات في الثانية** **║**\n"
        f"🚀 **║** 🛑 **لإيقاف:** `/stop {user_id}`          **║**\n"
        f"🚀 **╚══════════════════════════════════════════╝**",
        parse_mode='Markdown', reply_markup=control_keyboard)
    
    def run():
        asyncio.run(spam_manager.start_room_spam(user_id, chat_id, stop_event))
        if spam_key in active_spams:
            del active_spams[spam_key]
        if spam_key in spam_stop_events:
            del spam_stop_events[spam_key]
    
    threading.Thread(target=run, daemon=True).start()

@bot.message_handler(commands=['stop'])
def stop_spam(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ **الاستخدام:** `/stop [UID]`", parse_mode='Markdown')
        return
    
    user_id = args[1]
    stopped = False
    
    for key in list(active_spams.keys()):
        if user_id in key:
            if key in spam_stop_events:
                spam_stop_events[key].set()
            active_spams[key]['active'] = False
            stopped = True
    
    if stopped:
        bot.reply_to(message, f"✅ **تم إيقاف السبام للمستخدم** `{user_id}`", parse_mode='Markdown')
    else:
        bot.reply_to(message, f"⚠️ **لا يوجد سبام نشط للمستخدم** `{user_id}`", parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def show_status(message):
    if not active_spams:
        bot.reply_to(message, 
            "📊 **╔══════════════════════════════════════════╗**\n"
            "📊 **║     ℹ️ لا يوجد سبامات نشطة حالياً ℹ️       ║**\n"
            "📊 **╚══════════════════════════════════════════╝**",
            parse_mode='Markdown')
        return
    
    status = "📊 **╔══════════════════════════════════════════╗**\n"
    status += "📊 **║        📊 الـسـبـامـات الـنـشـطـة 📊         ║**\n"
    status += "📊 **╠══════════════════════════════════════════╣**\n"
    for key, spam in active_spams.items():
        if spam.get('active', False):
            elapsed = time.time() - spam['start_time']
            status += f"📊 **║**  🚀 **سبام روم**                         **║**\n"
            status += f"📊 **║**     👤 `{spam['user_id']}`                **║**\n"
            status += f"📊 **║**     ⏱️ `{elapsed:.0f}` ثانية              **║**\n"
            status += f"📊 **║**  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ **║**\n"
    status += f"📊 **╠══════════════════════════════════════════╣**\n"
    status += f"📊 **║**  📌 **المجموع:** `{len(active_spams)}` سبام نشط    **║**\n"
    status += f"📊 **╚══════════════════════════════════════════╝**"
    bot.reply_to(message, status, parse_mode='Markdown')

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
    welcome_text = (
        f"🌟 **╔══════════════════════════════════════════╗**\n"
        f"🌟 **║      🤖 بــوت الـسـبـام —͟͞͞★ＰＡＴＲＯＮ 🤖        ║**\n"
        f"🌟 **╠══════════════════════════════════════════╣**\n"
        f"🌟 **║**                                          **║**\n"
        f"🌟 **║**  🚀 `/spam [UID]` - سبام روم بدون توقف   **║**\n"
        f"🌟 **║**  🚀 `/srgo [UID]` - نفس الأمر           **║**\n"
        f"🌟 **║**  🛑 `/stop [UID]` - إيقاف سبام           **║**\n"
        f"🌟 **║**  📊 `/status` - عرض الحالة             **║**\n"
        f"🌟 **║**  🎨 `/menu` - القائمة الرئيسية         **║**\n"
        f"🌟 **║**                                          **║**\n"
        f"🌟 **╠══════════════════════════════════════════╣**\n"
        f"🌟 **║**  🔥 **الميزات الخارقة:**                  **║**\n"
        f"🌟 **║**  • سبام رومات بدون توقف نهائياً         **║**\n"
        f"🌟 **║**  • بدون أي تأخير - إرسال فوري           **║**\n"
        f"🌟 **║**  • سرعة خارقة - آلاف الطلبات في الثانية **║**\n"
        f"🌟 **║**  • واجهة جذابة ومتطورة                  **║**\n"
        f"🌟 **║**  • تحكم كامل بالسبامات                  **║**\n"
        f"🌟 **╚══════════════════════════════════════════╝**\n\n"
        f"🌟 **╔══════════════════════════════════════════╗**\n"
        f"🌟 **║         🔥 —͟͞͞★ＰＡＴＲＯＮ  S P A M 🔥           ║**\n"
        f"🌟 **╠══════════════════════════════════════════╣**\n"
        f"🌟 **║**  👑 **المطور:** {Config.DEVELOPER_USERNAME}        **║**\n"
        f"🌟 **║**  📢 **قناتنا:** [انضم الآن]({Config.CHANNEL_LINK})     **║**\n"
        f"🌟 **╚══════════════════════════════════════════╝**"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=main_menu())

@bot.message_handler(commands=['menu'])
def menu_command(message):
    bot.reply_to(message, "🎨 **لوحة تحكم SARGO:**", parse_mode='Markdown', reply_markup=main_menu())

# ========== معالجة الأزرار ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "spam_room":
        bot.answer_callback_query(call.id, "🚀 أرسل المعرف بعد الأمر /spam", show_alert=True)
        bot.send_message(call.message.chat.id, 
            "🚀 **لبدء سبام الروم:**\n`/spam [المعرف]`\n\n📌 **مثال:** `/spam 123456789`",
            parse_mode='Markdown')
    
    elif call.data == "status":
        if not active_spams:
            bot.answer_callback_query(call.id, "ℹ️ لا يوجد سبامات نشطة", show_alert=True)
        else:
            bot.answer_callback_query(call.id, f"📊 يوجد {len(active_spams)} سبام نشط", show_alert=True)
            show_status(call.message)
    
    elif call.data == "developer":
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📞 تواصل مع المطور", url="https://t.me/L3abassi1235"))
        bot.send_message(call.message.chat.id, 
            f"👑 **المطور:** {Config.DEVELOPER_USERNAME}", parse_mode='Markdown', reply_markup=keyboard)
    
    elif call.data == "channel":
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 انضم للقناة", url=Config.CHANNEL_LINK))
        bot.send_message(call.message.chat.id, 
            f"📢 **قناتنا:** {Config.CHANNEL_LINK}", parse_mode='Markdown', reply_markup=keyboard)
    
    elif call.data == "help":
        help_text = (
            f"❓ **الأوامر المتاحة:**\n\n"
            f"🚀 `/spam [UID]` - بدء سبام روم\n"
            f"🛑 `/stop [UID]` - إيقاف سبام\n"
            f"📊 `/status` - عرض الحالة\n"
            f"🎨 `/menu` - القائمة الرئيسية\n\n"
            f"⚡ **السبام يعمل بدون توقف - بدون أي تأخير**"
        )
        bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    
    elif call.data.startswith("stop_"):
        user_id = call.data.replace("stop_", "")
        stopped = False
        for key in list(active_spams.keys()):
            if user_id in key:
                if key in spam_stop_events:
                    spam_stop_events[key].set()
                active_spams[key]['active'] = False
                stopped = True
        if stopped:
            bot.answer_callback_query(call.id, f"✅ تم إيقاف سبام {user_id}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, f"⚠️ لا يوجد سبام نشط للمستخدم {user_id}", show_alert=True)

# ===== تشغيل البوت =====
if __name__ == '__main__':
    try:
        print("=" * 60)
        print("🌟 🤖 بوت السبام —͟͞͞★ＰＡＴＲＯＮ - قوة خارقة 🤖 🌟")
        print("=" * 60)
        print(f"👑 المطور: @—͟͞͞★ＰＡＴＲＯＮ")
        print(f"📢 القناة: https://t.me/+qHzADSvKbJthZmQ0")
        print(f"🚀 API: https://patroon-1top1.onrender.com")
        print("=" * 60)
        print("✅ البوت يعمل...")
        print("🔥 الأمر: /spam [UID]")
        print("🛑 للإيقاف: /stop [UID]")
        print("=" * 60)
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ خطأ: {e}")
        sys.exit(1)