import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime

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

# video eka thiyana group/channel id
SOURCE_CHAT_ID = -1001234567890

# video message id
VIDEO_MESSAGE_ID = 992

# ==========================================
# USER REQUEST DATABASE
# ==========================================
user_requests = {}

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

        else:
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
🎬 Welcome to Our MOVIE STREAM Channel! 🍿

Hey there 👋 ({user_name})
Thanks for joining!
"""

        # welcome message
        bot.reply_to(message, text)

        # auto forward video
        bot.forward_message(
            message.chat.id,
            SOURCE_CHAT_ID,
            VIDEO_MESSAGE_ID
        )


# ==========================================
# START COMMAND
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

🎬 Watch movies and TV series 🎬

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
කනගාටැයි. 😔
ඔයා හොයන එක මට හොයාගන්න අමාරුයි.
හරියට නම (අකුරු නිවැරදිව) සහ වර්ෂය ඇතුලත් කර නැවත උත්සහ කරන්න. 😇
Sorry. 😔
I'm having trouble finding what you're looking for.
Please enter the correct name and year and try again. 😇
""",

            reply_to_message_id=message.message_id
        )

        return

    # ==========================================
    # SEARCH RESULTS
    # ==========================================
    for item in data["results"][:10]:

        title = item.get("title") or item.get("name")

        year = ""

        if item.get("release_date"):
            year = item["release_date"][:4]

        if item.get("first_air_date"):
            year = item["first_air_date"][:4]

        movie_id = item["id"]

        media = item["media_type"]

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

    if user in user_requests:

        last = user_requests[user]

        diff = (now - last).days

        if diff < 7:

            bot.answer_callback_query(
                call.id,
                "❌ Request again after 7 days"
            )

            return

    user_requests[user] = now

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

    bot.answer_callback_query(
        call.id,
        "✅ Request Sent"
    )


# ==========================================
# START BOT
# ==========================================
print("✅ BOT RUNNING SUCCESSFULLY...")

bot.infinity_polling()
