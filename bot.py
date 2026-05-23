import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import re

# ==========================================
# BOT TOKEN
# ==========================================
BOT_TOKEN = "8642899423:AAEex0efz-uWzDyhUAWv_rwzXWn3Snvi2rM"

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# TMDB API
# ==========================================
API_KEY = "9749e1cc34cc81122cae6b163608aa03"
API = "https://api.themoviedb.org/3"

# ==========================================
# BOT USERNAME
# ==========================================
BOT_USERNAME = "MS_TG_01bot"

# ==========================================
# WEBSITE
# ==========================================
WEBSITE = "https://moviestream.it.com"

# ==========================================
# AUTO FORWARD VIDEO SETTINGS
# ==========================================
SOURCE_CHAT_ID = -1001234567890
VIDEO_MESSAGE_ID = 992

# ==========================================
# REQUEST GROUP
# ==========================================
REQUEST_GROUP = "@moviestreamrequset"

# ==========================================
# DATABASE
# ==========================================
user_requests = {}
warned_users = {}

# ==========================================
# CHECK WEBSITE
# ==========================================
def check_movie_on_site(title, year):

    slug = title.lower().replace(" ", "-")
    url = f"{WEBSITE}/{slug}-{year}"

    try:

        r = requests.get(url, timeout=5)

        if r.status_code == 200:
            return True, url

        return False, url

    except:
        return False, url


# ==========================================
# GET CHAT ID
# ==========================================
@bot.message_handler(commands=['chatid'])
def get_chat_id(message):

    bot.reply_to(
        message,
        f"CHAT ID:\n{message.chat.id}"
    )


# ==========================================
# GET VIDEO MESSAGE ID
# ==========================================
@bot.message_handler(content_types=['video'])
def get_video_id(message):

    bot.reply_to(
        message,
        f"VIDEO MESSAGE ID:\n{message.message_id}"
    )


# ==========================================
# WELCOME NEW USERS
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

ඔයාගේ යාලුවොත් add කරන්න 🫂
"""

        bot.reply_to(message, text)

        # AUTO FORWARD VIDEO
        try:

            bot.forward_message(
                message.chat.id,
                SOURCE_CHAT_ID,
                VIDEO_MESSAGE_ID
            )

        except Exception as e:
            print(e)


# ==========================================
# START COMMAND
# ==========================================
@bot.message_handler(commands=['start'])
def start(message):

    args = message.text.split()

    # ==========================================
    # OPEN MOVIE
    # ==========================================
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

        if data.get("first_air_date"):
            year = data["first_air_date"][:4]

        rating = data.get("vote_average", "-")

        poster = None

        if data.get("poster_path"):

            poster = "https://image.tmdb.org/t/p/w500" + data["poster_path"]

        exists, website_link = check_movie_on_site(title, year)

        markup = InlineKeyboardMarkup()

        # ==========================================
        # MOVIE EXISTS
        # ==========================================
        if exists:

            text = f"""
🎬 {title} ({year}) Sinhala Subtitles

⭐ IMDB Rating : {rating}

🔰 Quality : 720p / 1080p

📅 Release : {year}

🌐 Web Site Link 👇
{website_link}
"""

            markup.add(
                InlineKeyboardButton(
                    "🌐 WATCH / DOWNLOAD",
                    url=website_link
                )
            )

        # ==========================================
        # MOVIE NOT EXISTS
        # ==========================================
        else:

            text = f"""
ඔයා ඉල්ලන movie එක site එකේ නැහැ 😕

Request Button එක click කරන්න 👇

🎬 {title} ({year})

⭐ IMDB Rating : {rating}
"""

            markup.add(
                InlineKeyboardButton(
                    "📥 REQUEST FILM",
                    callback_data=f"request|{title}|{year}|{movie_id}"
                )
            )

        if poster:

            bot.send_photo(
                message.chat.id,
                poster,
                caption=text,
                reply_markup=markup
            )

        else:

            bot.send_message(
                message.chat.id,
                text,
                reply_markup=markup
            )

    # ==========================================
    # NORMAL START
    # ==========================================
    else:

        bot.send_message(
            message.chat.id,
            """
🎬 MOVIE STREAM BOT

Send Movie Name To Search 🔎
"""
        )


# ==========================================
# SEARCH MOVIES
# ==========================================
@bot.message_handler(func=lambda m: True)
def search_movie(message):

    if not message.text:
        return

    # ==========================================
    # LINK FILTER
    # ==========================================
    link_pattern = r"(https?://\S+|t\.me/\S+|www\.\S+)"

    if re.search(link_pattern, message.text):

        user_id = message.from_user.id
        name = message.from_user.first_name

        try:

            bot.delete_message(
                message.chat.id,
                message.message_id
            )

        except:
            pass

        # ==========================================
        # FIRST WARNING
        # ==========================================
        if user_id not in warned_users:

            warned_users[user_id] = 1

            warning_text = f"""
🚫━━━━━━━━━━━━🚫

Red line {name}

ඔයාට මේපාරට විතරක් සමාව දෙනවා 😕

ආයෙ Link දැම්මොත් remove කරනවා 😡

🚫━━━━━━━━━━━━🚫
"""

            bot.send_message(
                message.chat.id,
                warning_text
            )

# ==========================================
# SECOND TIME = 2 HOURS MUTE
# ==========================================
else:

    try:

        # 2 hours from now
        until_time = datetime.datetime.now() + datetime.timedelta(hours=2)

        # Restrict user
        bot.restrict_chat_member(
            message.chat.id,
            user_id,
            permissions=telebot.types.ChatPermissions(
                can_send_messages=False
            ),
            until_date=until_time
        )

        mute_text = f"""
⛔━━━━━━━━━━━━⛔

{name} ට පැය 2ක Mute එකක් දීලා තියෙනවා 😡

Reason :
Repeated Link Sharing 🚫

🕒 Mute Time : 2 Hours

⛔━━━━━━━━━━━━⛔
"""

        bot.send_message(
            message.chat.id,
            mute_text
        )

    except Exception as e:
        print(e)

    return

    # ==========================================
    # SEARCH MOVIES
    # ==========================================
    bot.send_chat_action(message.chat.id, "typing")

    query = message.text

    url = f"{API}/search/multi?api_key={API_KEY}&query={query}"

    data = requests.get(url).json()

    markup = InlineKeyboardMarkup()

    # ==========================================
    # NOT FOUND
    # ==========================================
    if not data["results"]:

        bot.send_message(
            message.chat.id,
            """
කනගාටැයි 😔

ඔයා හොයන එක හොයාගන්න බැරිවුනා.

Correct Name + Year දාලා try කරන්න 😇
""",
            reply_to_message_id=message.message_id
        )

        return

    # ==========================================
    # RESULTS
    # ==========================================
    for item in data["results"][:10]:

        title = item.get("title") or item.get("name")

        if not title:
            continue

        year = ""

        if item.get("release_date"):
            year = item["release_date"][:4]

        if item.get("first_air_date"):
            year = item["first_air_date"][:4]

        movie_id = item["id"]

        media = item["media_type"]

        if media not in ["movie", "tv"]:
            continue

        markup.add(
            InlineKeyboardButton(
                f"{title} ({year})",
                url=f"https://t.me/{BOT_USERNAME}?start={media}_{movie_id}"
            )
        )

    bot.send_message(
        message.chat.id,
        f"""
🔎 Your Search 👉 {query}

Select Movie 👇

-- Powered By MOVIE STREAM --
""",
        reply_markup=markup,
        reply_to_message_id=message.message_id
    )


# ==========================================
# REQUEST BUTTON
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
            "📤 SEND REQUEST",
            callback_data=f"sendreq|{title}|{year}|{movie_id}"
        )
    )

    bot.send_message(
        call.from_user.id,
        """
🎬 Movie not available on website

Request movie below 👇
""",
        reply_markup=markup
    )


# ==========================================
# SEND REQUEST
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("sendreq"))
def send_request(call):

    parts = call.data.split("|")

    title = parts[1]
    year = parts[2]
    movie_id = parts[3]

    user = call.from_user.id
    name = call.from_user.first_name
    username = call.from_user.username

    now = datetime.datetime.now()

    # ==========================================
    # 1 HOUR LIMIT
    # ==========================================
    if user in user_requests:

        last = user_requests[user]

        diff = (now - last).total_seconds()

        if diff < 3600:

            remaining = int((3600 - diff) / 60)

            bot.answer_callback_query(
                call.id,
                f"❌ Try again after {remaining} minutes"
            )

            return

    user_requests[user] = now

    # ==========================================
    # USER MESSAGE
    # ==========================================
    text = f"""
🎬 MOVIE REQUEST SENT

👤 User : {name}

🔗 Username : @{username}

📥 Title : {title}

📅 Year : {year}

🆔 TMDB ID : {movie_id}
"""

    bot.send_message(
        call.from_user.id,
        text
    )

    # ==========================================
    # GROUP MESSAGE
    # ==========================================
    group_text = f"""
Hy prabhash,

user කෙනෙක් movie / tv series එකක් ඉල්ලනවා 🎬

👤 User : {name}

🔗 Username : @{username}

🎥 Movie Name : {title}

📅 Year : {year}

🆔 TMDB ID : {movie_id}
"""

    bot.send_message(
        REQUEST_GROUP,
        group_text
    )

    # ==========================================
    # CALLBACK ALERT
    # ==========================================
    bot.answer_callback_query(
        call.id,
        "✅ Request Sent"
    )


# ==========================================
# START BOT
# ==========================================
print("✅ BOT RUNNING SUCCESSFULLY...")

bot.infinity_polling()
