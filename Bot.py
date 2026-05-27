import os, json, time, threading, random, traceback
from flask import Flask
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7142950609"))

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN Railway Variables me add karo.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
DATA_FILE = "data.json"
AUTO_DELETE_SECONDS = 300

DEFAULT = {
    "admins": [ADMIN_ID],
    "channels": [],
    "rewards": [],
    "users": [],
    "forward": True,
    "refer_on": True,
    "auto_delete": False,
    "refer": {"target": 2, "reward_index": 0, "refs": {}, "claimed": []},
    "ads": {"on": True, "interval": 3600, "items": [], "targets": []},
    "states": {}
}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load():
    if not os.path.exists(DATA_FILE):
        save(DEFAULT)
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    for k, v in DEFAULT.items():
        if k not in data:
            data[k] = v
    return data

db = load()

if ADMIN_ID not in db["admins"]:
    db["admins"].append(ADMIN_ID)
    save(db)

def is_admin(uid):
    return int(uid) in db["admins"]

def add_user(uid):
    if uid not in db["users"]:
        db["users"].append(uid)
        save(db)

def set_state(uid, state):
    db["states"][str(uid)] = state
    save(db)

def get_state(uid):
    return db["states"].get(str(uid))

def clear_state(uid):
    db["states"].pop(str(uid), None)
    save(db)

def delete_later(chat_id, msg_id):
    def run():
        try:
            bot.delete_message(chat_id, msg_id)
        except:
            pass
    threading.Timer(AUTO_DELETE_SECONDS, run).start()

def send_msg(chat_id, text, **kwargs):
    msg = bot.send_message(chat_id, text, **kwargs)
    if db.get("auto_delete"):
        delete_later(chat_id, msg.message_id)
    return msg

def join_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for ch in db["channels"]:
        buttons.append(types.InlineKeyboardButton(
            f"📢 Join {ch.replace('@','')}",
            url=f"https://t.me/{ch.replace('@','')}"
        ))
    if buttons:
        kb.add(*buttons)
    kb.add(types.InlineKeyboardButton("✅ VERIFY NOW", callback_data="verify"))
    return kb

def admin_start_kb(uid):
    kb = types.InlineKeyboardMarkup()
    if is_admin(uid):
        kb.add(types.InlineKeyboardButton("🎛 ADMIN PANEL", callback_data="open_admin"))
    return kb

def admin_panel_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("➕ Add Channel", callback_data="add_channel"),
        types.InlineKeyboardButton("❌ Remove Channel", callback_data="remove_channel"),
        types.InlineKeyboardButton("📋 List Channels", callback_data="list_channels"),
        types.InlineKeyboardButton("🎁 Add Reward", callback_data="add_reward"),
        types.InlineKeyboardButton("🗑 Remove Reward", callback_data="remove_reward"),
        types.InlineKeyboardButton("📦 List Rewards", callback_data="list_rewards"),
        types.InlineKeyboardButton("📊 Stats", callback_data="stats"),
        types.InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
        types.InlineKeyboardButton("🔘 Button Broadcast", callback_data="button_broadcast"),
        types.InlineKeyboardButton("🖼 Media Broadcast", callback_data="media_broadcast"),
        types.InlineKeyboardButton("🔐 Forward ON/OFF", callback_data="toggle_forward"),
        types.InlineKeyboardButton("🔁 Refer ON/OFF", callback_data="toggle_refer"),
        types.InlineKeyboardButton("📣 Ads Panel", callback_data="ads_panel"),
        types.InlineKeyboardButton("➕ Add Ads", callback_data="add_ads"),
        types.InlineKeyboardButton("🗑 Remove Ads", callback_data="remove_ads"),
        types.InlineKeyboardButton("✅ Ads ON/OFF", callback_data="toggle_ads"),
        types.InlineKeyboardButton("⏱ Ads Time", callback_data="ads_time"),
        types.InlineKeyboardButton("🎯 Add Ads Target", callback_data="add_ads_target"),
        types.InlineKeyboardButton("❌ Remove Ads Target", callback_data="remove_ads_target"),
        types.InlineKeyboardButton("📋 List Ads Target", callback_data="list_ads_target"),
        types.InlineKeyboardButton("🚀 Run Ads Now", callback_data="run_ads_now"),
        types.InlineKeyboardButton("🧹 Auto Delete ON/OFF", callback_data="toggle_autodelete"),
        types.InlineKeyboardButton("👮 Admin Control", callback_data="admin_control")
    )
    return kb

def check_join(uid):
    if not db["channels"]:
        return True
    for ch in db["channels"]:
        try:
            mem = bot.get_chat_member(ch, uid)
            if mem.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def loading(chat_id, title):
    msg = bot.send_message(chat_id, f"{title}\n\n▰▱▱▱▱▱▱▱▱▱ 10%")
    steps = [
        "▰▰▱▱▱▱▱▱▱▱ 20%",
        "▰▰▰▰▱▱▱▱▱▱ 40%",
        "▰▰▰▰▰▰▱▱▱▱ 60%",
        "▰▰▰▰▰▰▰▰▱▱ 80%",
        "▰▰▰▰▰▰▰▰▰▰ 100%"
    ]
    for s in steps:
        time.sleep(0.35)
        try:
            bot.edit_message_text(f"{title}\n\n{s}", chat_id, msg.message_id)
        except:
            pass

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    add_user(uid)

    parts = message.text.split()
    if len(parts) > 1 and parts[1].isdigit() and db["refer_on"]:
        ref = parts[1]
        if str(uid) != ref:
            db["refer"]["refs"].setdefault(ref, [])
            if uid not in db["refer"]["refs"][ref]:
                db["refer"]["refs"][ref].append(uid)
                save(db)

    loading(uid, "👑 𝙂𝙊𝘿 𝙍𝘼𝙁𝙏𝘼𝘼𝙍 𝘽𝙊𝙏")

    text = f"""
🔥 <b>WELCOME RAFTAAR ⚡</b>

Hey <b>{message.from_user.first_name}</b>

👥 Users: <b>{len(db["users"])}</b>

📢 Join all channels.
✅ Then click VERIFY NOW.
"""

    try:
        photos = bot.get_user_profile_photos(uid, limit=1)
        if photos.total_count > 0:
            bot.send_photo(uid, photos.photos[0][-1].file_id, caption=text, reply_markup=join_kb())
        else:
            bot.send_message(uid, text, reply_markup=join_kb())
    except:
        bot.send_message(uid, text, reply_markup=join_kb())

    if is_admin(uid):
        bot.send_message(uid, "🎛 Admin panel ready.", reply_markup=admin_start_kb(uid))

    if db["ads"]["on"] and db["ads"]["items"]:
        send_msg(uid, "📣 <b>Sponsored Ad</b>\n\n" + random.choice(db["ads"]["items"]))
      @bot.callback_query_handler(func=lambda c: c.data == "open_admin")
def open_admin(c):
    if not is_admin(c.from_user.id):
        return
    bot.send_message(c.message.chat.id, "👑 <b>ADMIN PANEL</b>", reply_markup=admin_panel_kb())


@bot.callback_query_handler(func=lambda c: c.data == "verify")
def verify(c):
    uid = c.from_user.id

    msg = bot.send_message(uid, "🔎 Starting verification...\n\n▰▱▱▱▱▱▱▱▱▱ 10%")
    steps = [
        "📢 Checking channels...\n\n▰▰▰▱▱▱▱▱▱▱ 30%",
        "⚡ Verifying membership...\n\n▰▰▰▰▰▱▱▱▱▱ 50%",
        "🎁 Preparing reward...\n\n▰▰▰▰▰▰▰▱▱▱ 70%",
        "✅ Final checking...\n\n▰▰▰▰▰▰▰▰▰▱ 90%"
    ]

    for s in steps:
        time.sleep(0.45)
        try:
            bot.edit_message_text(s, uid, msg.message_id)
        except:
            pass

    if check_join(uid):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🎁 CLAIM REWARD", callback_data="claim_reward"))
        kb.add(types.InlineKeyboardButton("👥 MY REFER LINK", callback_data="my_ref"))
        bot.edit_message_text(
            "✅ Verification Successful!\n\n🎁 Claim your reward below.",
            uid,
            msg.message_id,
            reply_markup=kb
        )
    else:
        bot.edit_message_text(
            "❌ Verification Failed!\n\nPehle sab channel join karo.",
            uid,
            msg.message_id,
            reply_markup=join_kb()
        )


@bot.callback_query_handler(func=lambda c: c.data == "claim_reward")
def claim_reward(c):
    uid = c.from_user.id

    if not check_join(uid):
        bot.answer_callback_query(c.id, "Pehle channels join karo.", show_alert=True)
        return

    ridx = db["refer"]["reward_index"]
    reward = "Reward admin ne set nahi kiya."

    if db["rewards"] and 0 <= ridx < len(db["rewards"]):
        reward = db["rewards"][ridx]

    bot.send_message(uid, f"🎁 <b>Your Reward:</b>\n\n{reward}")


@bot.callback_query_handler(func=lambda c: c.data == "my_ref")
def my_ref(c):
    uid = str(c.from_user.id)
    count = len(db["refer"]["refs"].get(uid, []))
    link = f"https://t.me/{bot.get_me().username}?start={uid}"

    bot.send_message(
        c.from_user.id,
        f"👥 <b>Your Referrals:</b> {count}/{db['refer']['target']}\n\n🔗 {link}"
    )


@bot.callback_query_handler(func=lambda c: is_admin(c.from_user.id))
def admin_buttons(c):
    data = c.data
    uid = c.from_user.id
    chat_id = c.message.chat.id

    if data == "add_channel":
        set_state(uid, "add_channel")
        send_msg(chat_id, "➕ Send channel username:\nExample: @channelname")

    elif data == "remove_channel":
        if not db["channels"]:
            return send_msg(chat_id, "No channels added.")
        text = "❌ Send channel number to remove:\n\n"
        text += "\n".join([f"{i+1}. {ch}" for i, ch in enumerate(db["channels"])])
        set_state(uid, "remove_channel")
        send_msg(chat_id, text)

    elif data == "list_channels":
        text = "\n".join([f"{i+1}. {ch}" for i, ch in enumerate(db["channels"])])
        send_msg(chat_id, "📋 <b>Channels:</b>\n\n" + (text or "No channels."))

    elif data == "add_reward":
        set_state(uid, "add_reward")
        send_msg(chat_id, "🎁 Send reward text/link:")

    elif data == "remove_reward":
        if not db["rewards"]:
            return send_msg(chat_id, "No rewards added.")
        text = "🗑 Send reward number to remove:\n\n"
        text += "\n".join([f"{i+1}. {r}" for i, r in enumerate(db["rewards"])])
        set_state(uid, "remove_reward")
        send_msg(chat_id, text)

    elif data == "list_rewards":
        text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(db["rewards"])])
        send_msg(chat_id, "📦 <b>Rewards:</b>\n\n" + (text or "No rewards."))

    elif data == "stats":
        send_msg(chat_id, f"""
📊 <b>BOT STATS</b>

👥 Users: <b>{len(db["users"])}</b>
📢 Channels: <b>{len(db["channels"])}</b>
🎁 Rewards: <b>{len(db["rewards"])}</b>
📣 Ads: <b>{len(db["ads"]["items"])}</b>
🎯 Ad Targets: <b>{len(db["ads"]["targets"])}</b>

🔐 Forward: <b>{"ON ✅" if db["forward"] else "OFF ❌"}</b>
🔁 Refer: <b>{"ON ✅" if db["refer_on"] else "OFF ❌"}</b>
📣 Ads: <b>{"ON ✅" if db["ads"]["on"] else "OFF ❌"}</b>
🧹 Auto Delete: <b>{"ON ✅" if db["auto_delete"] else "OFF ❌"}</b>
""")

    elif data == "broadcast":
        set_state(uid, "broadcast")
        send_msg(chat_id, "📢 Send text/media message for broadcast:")

    elif data == "button_broadcast":
        set_state(uid, "button_broadcast_text")
        send_msg(chat_id, "🔘 Send broadcast text first:")

    elif data == "media_broadcast":
        set_state(uid, "media_broadcast")
        send_msg(chat_id, "🖼 Send photo/video/file/message for media broadcast:")

    elif data == "toggle_forward":
        db["forward"] = not db["forward"]
        save(db)
        send_msg(chat_id, f"🔐 Forward is now: <b>{'ON ✅' if db['forward'] else 'OFF ❌'}</b>")

    elif data == "toggle_refer":
        db["refer_on"] = not db["refer_on"]
        save(db)
        send_msg(chat_id, f"🔁 Refer is now: <b>{'ON ✅' if db['refer_on'] else 'OFF ❌'}</b>")

    elif data == "ads_panel":
        send_msg(chat_id, f"""
📣 <b>ADS CONTROL PANEL</b>

Status: <b>{"ON ✅" if db["ads"]["on"] else "OFF ❌"}</b>
Time: <b>{db["ads"]["interval"]} sec</b>
Ads: <b>{len(db["ads"]["items"])}</b>
Targets: <b>{len(db["ads"]["targets"])}</b>

Buttons se control karo:
➕ Add Ads
🗑 Remove Ads
✅ Ads ON/OFF
⏱ Ads Time
🎯 Add Ads Target
❌ Remove Ads Target
🚀 Run Ads Now
""")

    elif data == "add_ads":
        set_state(uid, "add_ads")
        send_msg(chat_id, "➕ Send ad text/link:")

    elif data == "remove_ads":
        if not db["ads"]["items"]:
            return send_msg(chat_id, "No ads added.")
        text = "🗑 Send ad number to remove:\n\n"
        text += "\n".join([f"{i+1}. {a}" for i, a in enumerate(db["ads"]["items"])])
        set_state(uid, "remove_ads")
        send_msg(chat_id, text)

    elif data == "toggle_ads":
        db["ads"]["on"] = not db["ads"]["on"]
        save(db)
        send_msg(chat_id, f"📣 Ads: <b>{'ON ✅' if db['ads']['on'] else 'OFF ❌'}</b>")

    elif data == "ads_time":
        set_state(uid, "ads_time")
        send_msg(chat_id, "⏱ Send ads interval in seconds:\nExample: 3600")

    elif data == "add_ads_target":
        set_state(uid, "add_ads_target")
        send_msg(chat_id, "🎯 Send channel/group username for ads:\nExample: @channelname")

    elif data == "remove_ads_target":
        if not db["ads"]["targets"]:
            return send_msg(chat_id, "No ads target added.")
        text = "❌ Send target number to remove:\n\n"
        text += "\n".join([f"{i+1}. {t}" for i, t in enumerate(db["ads"]["targets"])])
        set_state(uid, "remove_ads_target")
        send_msg(chat_id, text)

    elif data == "list_ads_target":
        text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(db["ads"]["targets"])])
        send_msg(chat_id, "📋 <b>Ads Targets:</b>\n\n" + (text or "No targets."))

    elif data == "run_ads_now":
        sent = run_ads()
        send_msg(chat_id, f"🚀 Ads sent to <b>{sent}</b> targets.")

    elif data == "toggle_autodelete":
        db["auto_delete"] = not db["auto_delete"]
        save(db)
        send_msg(chat_id, f"🧹 Auto Delete 5 min: <b>{'ON ✅' if db['auto_delete'] else 'OFF ❌'}</b>")

    elif data == "admin_control":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("➕ Add Admin", callback_data="add_admin"),
            types.InlineKeyboardButton("❌ Remove Admin", callback_data="remove_admin"),
            types.InlineKeyboardButton("📋 List Admins", callback_data="list_admins"),
            types.InlineKeyboardButton("🎯 Set Refer Target", callback_data="set_refer_target"),
            types.InlineKeyboardButton("🎁 Set Refer Reward", callback_data="set_refer_reward")
        )
        send_msg(chat_id, "👮 <b>ADMIN CONTROL</b>", reply_markup=kb)

    elif data == "add_admin":
        set_state(uid, "add_admin")
        send_msg(chat_id, "➕ Send new admin user ID:")

    elif data == "remove_admin":
        set_state(uid, "remove_admin")
        send_msg(chat_id, "❌ Send admin user ID to remove:")

    elif data == "list_admins":
        send_msg(chat_id, "📋 <b>Admins:</b>\n\n" + "\n".join(map(str, db["admins"])))

    elif data == "set_refer_target":
        set_state(uid, "set_refer_target")
        send_msg(chat_id, "🎯 Send refer target number:\nExample: 2")

    elif data == "set_refer_reward":
        if not db["rewards"]:
            return send_msg(chat_id, "No rewards added.")
        text = "🎁 Send reward number for refer reward:\n\n"
        text += "\n".join([f"{i+1}. {r}" for i, r in enumerate(db["rewards"])])
        set_state(uid, "set_refer_reward")
        send_msg(chat_id, text)
      def run_ads():
    if not db["ads"]["on"] or not db["ads"]["items"]:
        return 0

    ad = random.choice(db["ads"]["items"])
    sent = 0

    for target in db["ads"]["targets"]:
        try:
            bot.send_message(target, "📣 <b>Sponsored Ad</b>\n\n" + ad)
            sent += 1
        except:
            pass

    return sent


@bot.message_handler(content_types=["text", "photo", "video", "document", "audio", "voice"])
def handle_all(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    add_user(uid)

    state = get_state(uid)

    if is_admin(uid) and state:

        if state == "add_channel":
            ch = message.text.strip()
            if not ch.startswith("@"):
                return send_msg(chat_id, "Channel username @ se start hona chahiye.")
            if ch not in db["channels"]:
                db["channels"].append(ch)
            save(db)
            clear_state(uid)
            return send_msg(chat_id, f"✅ Channel added: {ch}")

        if state == "remove_channel":
            try:
                i = int(message.text.strip()) - 1
                removed = db["channels"].pop(i)
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"🗑 Removed: {removed}")
            except:
                return send_msg(chat_id, "Valid number bhejo.")

        if state == "add_reward":
            db["rewards"].append(message.text.strip())
            save(db)
            clear_state(uid)
            return send_msg(chat_id, "✅ Reward added.")

        if state == "remove_reward":
            try:
                i = int(message.text.strip()) - 1
                removed = db["rewards"].pop(i)
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"🗑 Reward removed:\n{removed}")
            except:
                return send_msg(chat_id, "Valid number bhejo.")

        if state == "broadcast":
            ok = 0
            for u in db["users"]:
                try:
                    bot.copy_message(u, chat_id, message.message_id)
                    ok += 1
                except:
                    pass
            clear_state(uid)
            return send_msg(chat_id, f"✅ Broadcast sent: {ok}")

        if state == "button_broadcast_text":
            db["temp_button_text"] = message.text
            save(db)
            set_state(uid, "button_broadcast_button")
            return send_msg(chat_id, "🔘 Ab button text bhejo:\nExample: JOIN NOW")

        if state == "button_broadcast_button":
            db["temp_button_name"] = message.text
            save(db)
            set_state(uid, "button_broadcast_url")
            return send_msg(chat_id, "🔗 Ab button URL bhejo:\nExample: https://t.me/username")

        if state == "button_broadcast_url":
            url = message.text.strip()
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(db.get("temp_button_name", "OPEN"), url=url))

            ok = 0
            for u in db["users"]:
                try:
                    bot.send_message(u, db.get("temp_button_text", ""), reply_markup=kb)
                    ok += 1
                except:
                    pass

            db.pop("temp_button_text", None)
            db.pop("temp_button_name", None)
            save(db)
            clear_state(uid)
            return send_msg(chat_id, f"✅ Button broadcast sent: {ok}")

        if state == "media_broadcast":
            ok = 0
            for u in db["users"]:
                try:
                    bot.copy_message(u, chat_id, message.message_id)
                    ok += 1
                except:
                    pass
            clear_state(uid)
            return send_msg(chat_id, f"✅ Media broadcast sent: {ok}")

        if state == "add_ads":
            db["ads"]["items"].append(message.text.strip())
            save(db)
            clear_state(uid)
            return send_msg(chat_id, "✅ Ad added.")

        if state == "remove_ads":
            try:
                i = int(message.text.strip()) - 1
                removed = db["ads"]["items"].pop(i)
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"🗑 Ad removed:\n{removed}")
            except:
                return send_msg(chat_id, "Valid number bhejo.")

        if state == "ads_time":
            try:
                sec = int(message.text.strip())
                db["ads"]["interval"] = sec
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"⏱ Ads time set: {sec} seconds")
            except:
                return send_msg(chat_id, "Sirf number bhejo. Example: 3600")

        if state == "add_ads_target":
            target = message.text.strip()
            if not target.startswith("@"):
                return send_msg(chat_id, "Target @ se start hona chahiye.")
            if target not in db["ads"]["targets"]:
                db["ads"]["targets"].append(target)
            save(db)
            clear_state(uid)
            return send_msg(chat_id, f"🎯 Ads target added: {target}")

        if state == "remove_ads_target":
            try:
                i = int(message.text.strip()) - 1
                removed = db["ads"]["targets"].pop(i)
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"🗑 Ads target removed:\n{removed}")
            except:
                return send_msg(chat_id, "Valid number bhejo.")

        if state == "add_admin":
            try:
                new_admin = int(message.text.strip())
                if new_admin not in db["admins"]:
                    db["admins"].append(new_admin)
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"✅ Admin added: {new_admin}")
            except:
                return send_msg(chat_id, "Valid user ID bhejo.")

        if state == "remove_admin":
            try:
                old_admin = int(message.text.strip())
                if old_admin == ADMIN_ID:
                    return send_msg(chat_id, "Main owner admin remove nahi ho sakta.")
                if old_admin in db["admins"]:
                    db["admins"].remove(old_admin)
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"🗑 Admin removed: {old_admin}")
            except:
                return send_msg(chat_id, "Valid user ID bhejo.")

        if state == "set_refer_target":
            try:
                target = int(message.text.strip())
                db["refer"]["target"] = target
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"🎯 Refer target set: {target}")
            except:
                return send_msg(chat_id, "Number bhejo. Example: 2")

        if state == "set_refer_reward":
            try:
                i = int(message.text.strip()) - 1
                if i < 0 or i >= len(db["rewards"]):
                    return send_msg(chat_id, "Valid reward number bhejo.")
                db["refer"]["reward_index"] = i
                save(db)
                clear_state(uid)
                return send_msg(chat_id, f"🎁 Refer reward set: {i+1}")
            except:
                return send_msg(chat_id, "Valid number bhejo.")

    if db["forward"] and not is_admin(uid):
        try:
            bot.forward_message(ADMIN_ID, chat_id, message.message_id)
        except:
            pass


def ad_loop():
    while True:
        try:
            time.sleep(int(db["ads"]["interval"]))
            run_ads()
        except:
            time.sleep(10)


app = Flask(__name__)

@app.route("/")
def home():
    return "Bot running!"


def web():
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))


def start_bot():
    while True:
        try:
            print("Bot polling started...")
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        except Exception:
            print("Bot crashed. Restarting in 5 sec...")
            traceback.print_exc()
            time.sleep(5)


threading.Thread(target=web, daemon=True).start()
threading.Thread(target=ad_loop, daemon=True).start()
start_bot()
      
