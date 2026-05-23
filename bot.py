import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import re

# ==========================================
# BOT TOKEN
# ==========================================
BOT_TOKEN = "8642899423:AAGDL5d5vyqDw-cKXjsBxzj85zAPmS9SUiQ"
bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# TMDB API
# ==========================================
API_KEY = "9749e1cc34cc81122cae6b163608aa03"
API = "https://api.themoviedb.org/3"

# ==========================================
# SETTINGS
# ==========================================
BOT_USERNAME = "MS_TG_01bot"   # ❗ NO @

WEBSITE = "https://moviestream.it.com"

SOURCE_CHAT_ID = -1001234567890
VIDEO_MESSAGE_ID = 992

REQUEST_GROUP = "@moviestreamrequset"

# ==========================================
# MEMORY
# ==========================================
user_requests = {}
warned_users = {}

# ==========================================
# WEBSITE CHECK
# ==========================================
def check_movie_on_site(title, year):
    slug = title.lower().replace(" ", "-")
    url = f"{WEBSITE}/{slug}-{year}"

    try:
        r = requests.get(url, timeout=5)
        return (r.status_code == 200), url
    except:
        return False, url

# ==========================================
# CHAT ID
# ==========================================
@bot.message_handler(commands=['chatid'])
def get_chat_id(message):
    bot.reply_to(message, f"CHAT ID:\n{message.chat.id}")

# ==========================================
# VIDEO ID
# ==========================================
@bot.message_handler(content_types=['video'])
def get_video_id(message):
    bot.reply_to(message, f"VIDEO MESSAGE ID:\n{message.message_id}")

# ==========================================
# WELCOME MESSAGE (UNCHANGED)
# ==========================================
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):

    for member in message.new_chat_members:

        user_name = member.first_name

        text = f"""
Hy 😊👋 ({user_name})

🍁 සාදරයෙන් පිලිගන්නවා Movie Stream Searching චැටි සමුහය වෙතට,

ඔබට මෙම Stream එක තුලින් 💯
ඔයා හොයන movie එකේ නම group එකට දාන්න.
Bot විසින් ඔයාට හොයන Movies/Drama දානවා.

ඔයාට ඕන Movie/Drama එක site එකේ නැතිවුනොත්
request එකක් දාන්න අමතක කරන්න එපා.

අපි ඔයාට පැය 24ත් - 48ත් අතර
Movie/Drama එක site එකට upload කරනවා 🎬

🚫 Group Rules 🚫

❌ Links දාන්න එපා
❌ Promotions කරන්න එපා
❌ Spam කරන්න එපා

ඔයාගේ යාලුවොත් Group එකට් add කරන්න අමතක කරන්න එපා 🫂
"""

        bot.reply_to(message, text)

        try:
            bot.forward_message(
                message.chat.id,
                SOURCE_CHAT_ID,
                VIDEO_MESSAGE_ID
            )
        except:
            pass

# ==========================================
# START COMMAND (FIXED LINK BUTTON)
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):

    args = message.text.split()

    if len(args) > 1:

        data = args[1].split("_")
        media = data[0]
        movie_id = data[1]

        if media == "movie":
            url = f"{API}/movie/{movie_id}?api_key={API_KEY}"
        else:
            url = f"{API}/tv/{movie_id}?api_key={API_KEY}"

        data = requests.get(url).json()

        title = data.get("title") or data.get("name", "-")

        year = "-"
        if data.get("release_date"):
            year = data["release_date"][:4]
        elif data.get("first_air_date"):
            year = data["first_air_date"][:4]

        rating = data.get("vote_average", "-")

        poster = None
        if data.get("poster_path"):
            poster = "https://image.tmdb.org/t/p/w500" + data["poster_path"]

        exists, website_link = check_movie_on_site(title, year)

        markup = InlineKeyboardMarkup()

        if exists:

            text = f"""
🎬 {title} ({year}) Sinhala Subtitles | English Subtitles

⭐ IMDB Rating : {rating}

🔰 Quality : 720p / 1080p

📅 Release : {year}

🌐 Web Site Link 👇
{website_link}
"""

            markup.add(
                InlineKeyboardButton("🌐 WATCH / DOWNLOAD", url=website_link)
            )

        else:

            text = f"""
ඔයා ඉල්ලන movie එක site එකේ නැහැ 😕

Request Button එක click කරන්න 👇

🎬 {title} ({year})

⭐ IMDB Rating : {rating}
"""

            # ✅ FIXED DEEP LINK BUTTON
            start_param = f"{media}_{movie_id}"
            markup.add(
    InlineKeyboardButton(
        "🎬 REQUEST MOVIE",
        callback_data=f"request|{media}|{movie_id}|{title}|{year}"
    )
)
        if poster:
            bot.send_photo(message.chat.id, poster, caption=text, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, text, reply_markup=markup)

    else:
        bot.send_message(message.chat.id, "Send movie name to search 🔎")

# ==========================================
# SEARCH FUNCTION (FIXED)
# ==========================================
@bot.message_handler(func=lambda m: m.text and not m.text.startswith("/"))
def search_movie(message):

    user_id = message.from_user.id
    name = message.from_user.first_name

    link_pattern = r"(https?://\S+|t\.me/\S+|www\.\S+)"

    # BLOCK LINKS
    if re.search(link_pattern, message.text):

        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass

        if user_id not in warned_users:
            warned_users[user_id] = 1
            bot.send_message(message.chat.id, f"🚫 Warning {name}")
        else:
            try:
                until_time = datetime.datetime.now() + datetime.timedelta(hours=2)

                bot.restrict_chat_member(
                    message.chat.id,
                    user_id,
                    permissions=telebot.types.ChatPermissions(
                        can_send_messages=False
                    ),
                    until_date=until_time
                )

                bot.send_message(message.chat.id, f"⛔ {name} muted 2 hours")
            except:
                pass

        return

    # SEARCH TMDB
    bot.send_chat_action(message.chat.id, "typing")

    query = message.text
    url = f"{API}/search/multi?api_key={API_KEY}&query={query}"

    try:
        data = requests.get(url, timeout=10).json()
    except:
        bot.send_message(message.chat.id, "Error")
        return

    results = data.get("results", [])

    if not results:
        bot.send_message(message.chat.id, "කනගාටැයි. 😔
ඔයා හොයන එක මට හොයාගන්න අමාරුයි.
හරියට නම සහ වර්ෂය ඇතුලත් කර නැවත උත්සහ කරන්න. 😇
Sorry. 😔
I'm having trouble finding what you're looking for.
Please enter the correct name and year and try again. 😇")
        return

    markup = InlineKeyboardMarkup()

    for item in results[:10]:

        title = item.get("title") or item.get("name")
        if not title:
            continue

        movie_id = item.get("id")
        media = item.get("media_type")

        if media not in ["movie", "tv"]:
            continue

        year = ""
        if item.get("release_date"):
            year = item["release_date"][:4]
        elif item.get("first_air_date"):
            year = item["first_air_date"][:4]

        start_param = f"{media}_{movie_id}"

        # ✅ FIXED BUTTON LINK
        markup.add(
            InlineKeyboardButton(
                f"{title} ({year})",
                url=f"https://t.me/{BOT_USERNAME}?start={start_param}"
            )
        )

    bot.send_message(message.chat.id, f"""🔎 Your Search 👉 {query}

Select Movie 👇

-- Powered By MOVIE STREAM --""", reply_markup=markup)

# ==========================================
# REQUEST SYSTEM (UNCHANGED LOGIC)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("request"))
def request_movie(call):

    parts = call.data.split("|")

    title = parts[1]
    year = parts[2]
    movie_id = parts[3]

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "SEND REQUEST",
            callback_data=f"sendreq|{title}|{year}|{movie_id}"
        )
    )

    bot.send_message(call.from_user.id,
        "🎬 Request movie below 👇",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("sendreq"))
def send_request(call):

    parts = call.data.split("|")

    title = parts[1]
    year = parts[2]
    movie_id = parts[3]

    user = call.from_user.id
    name = call.from_user.first_name
    username = call.from_user.username or "NoUsername"

    now = datetime.datetime.now()

    if user in user_requests:
        diff = (now - user_requests[user]).total_seconds()
        if diff < 1800:
            remaining = int((1800 - diff) / 60)
            bot.answer_callback_query(call.id, f"Wait {remaining} min")
            return

    user_requests[user] = now

    bot.send_message(call.from_user.id,
        f"""
🎬 MOVIE REQUEST SENT

👤 User : {name}
🔗 Username : @{username}

📥 Title : {title}
📅 Year : {year}
🆔 TMDB ID : {movie_id}
"""
    )

    bot.send_message(REQUEST_GROUP,
        f"""
Hy prabhash,

user කෙනෙක් movie / tv serious එකක් ඉල්ලනවා කියලා.

user ; {name} (@{username if username else "No Username"}),

Movie name : < {title} >
"""
    )

    bot.answer_callback_query(call.id, "Request Sent ✅")

# ==========================================
# RUN BOT
# ==========================================
print("BOT RUNNING...")
bot.infinity_polling()
