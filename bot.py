import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import re

# BOT TOKEN
BOT_TOKEN = "8642899423:AAEex0efz-uWzDyhUAWv_rwzXWn3Snvi2rM"

bot = telebot.TeleBot(BOT_TOKEN)

# TMDB API
API_KEY = "9749e1cc34cc81122cae6b163608aa03"
API = "https://api.themoviedb.org/3"

# BOT USERNAME
BOT_USERNAME = "MS_TG_01bot"

# WEBSITE
WEBSITE = "https://www.moviestream.it.com"

# USER REQUEST DATABASE
user_requests = {}


# --------------------------
# 🔥 GROUP LINK BLOCKER (NEW)
# --------------------------
@bot.message_handler(content_types=['text'])
def delete_links(message):

    if message.chat.type in ["group", "supergroup"]:

        url_pattern = r"(https?://\S+|www\.\S+|t\.me/\S+)"

        if message.text and re.search(url_pattern, message.text):

            try:
                bot.delete_message(message.chat.id, message.message_id)

                bot.send_message(
                    message.chat.id,
                    "🚫 Links not allowed!",
                    reply_to_message_id=message.message_id
                )

            except:
                pass

            return  # ⛔ IMPORTANT (stop other handlers)


# --------------------------
# CHECK WEBSITE
# --------------------------
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


# --------------------------
# START COMMAND
# --------------------------
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

        if exists:

            text = f"""
🎬 {title} ({year}) Sinhala Subtitles

⭐ IMDB Rating : {rating}

📅 Year : {year}

👇 Watch / Download
"""

            markup.add(
                InlineKeyboardButton(
                    "🌐 WATCH / DOWNLOAD",
                    url=website_link
                )
            )

        else:

            text = f"""
❌ Not available

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
            "🎬 MOVIE STREAM BOT\n\nSend movie name to search 🔎"
        )


# --------------------------
# SEARCH MOVIE
# --------------------------
@bot.message_handler(func=lambda m: True)
def search_movie(message):

    bot.send_chat_action(message.chat.id, "typing")

    query = message.text

    url = f"{API}/search/multi?api_key={API_KEY}&query={query}"

    data = requests.get(url).json()

    markup = InlineKeyboardMarkup()

    if not data["results"]:

        bot.send_message(
            message.chat.id,
            "❌ Not found",
            reply_to_message_id=message.message_id
        )
        return

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
        f"🔎 {query}",
        reply_markup=markup,
        reply_to_message_id=message.message_id
    )


# --------------------------
# REQUEST BUTTON
# --------------------------
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
        "Movie not available. Request කරන්න 👇",
        reply_markup=markup
    )


# --------------------------
# SEND REQUEST
# --------------------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("sendreq"))
def send_request(call):

    parts = call.data.split("|")

    title = parts[1]
    year = parts[2]
    movie_id = parts[3]

    user = call.from_user.id
    now = datetime.datetime.now()

    if user in user_requests:
        last = user_requests[user]
        if (now - last).days < 7:
            bot.answer_callback_query(call.id, "❌ Try again after 7 days")
            return

    user_requests[user] = now

    bot.send_message(
        call.from_user.id,
        f"✅ Request Sent\n\n{title} ({year})"
    )

    bot.answer_callback_query(call.id, "Done")


print("BOT RUNNING...")
bot.infinity_polling()
