import hashlib
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------------- CONFIG ----------------
API_ID = 33834818         # your API ID
API_HASH = "0437bebaf533e518eb104350ae581cec"    # your API HASH
BOT_TOKEN = "8266240853:AAHUnYe8Z41roW6qlv-mfa6wFs-lfCDCFoo"  # your BOT TOKEN

# Add one or more channel IDs
CHANNEL_IDS = [-1003535566355]  # 👈 add your channel IDs here

# ---------------- MEMORY STORAGE ----------------
movie_data = {}

# ---------------- BOT INIT ----------------
app = Client(
    "movie_filter_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ---------------- WELCOME MESSAGE ----------------
@app.on_message(filters.private & filters.command("start"))
async def welcome(client, message):
    welcome_text = (
        "🎬 **Welcome to Movie Filter Bot!**\n\n"
        "Search & watch your favorite movies instantly.\n\n"
        "💡 **How to use:**\n"
        "1️⃣ Send the movie name (e.g., `avengers`).\n"
        "2️⃣ Click on the movie from the search results.\n"
        "3️⃣ Enjoy the movie directly here!\n\n"
        "✨ Only main movie names are searchable.\n"
        "⏱️ Movies auto delete in 1 minute"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📺 Our Channel", url="https://t.me/YourChannel")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

    await message.reply_text(welcome_text, reply_markup=buttons)

# ---------------- AUTO INDEX ----------------
@app.on_message(filters.chat(CHANNEL_IDS) & (filters.document | filters.video))
async def auto_index(client, message):
    file = message.document or message.video
    file_name = file.file_name or "Unknown.Movie"

    main_name = file_name.split(".")[0].lower()
    uid = hashlib.md5(file.file_id.encode()).hexdigest()[:10]

    movie_data[uid] = {
        "name": main_name,
        "file_id": file.file_id,
        "caption": file_name
    }

    print(f"✅ Indexed: {main_name}")

# ---------------- SEARCH ----------------
@app.on_message(filters.private & filters.text)
async def search_movie(client, message):
    if message.text.startswith("/"):
        return

    query = message.text.lower().strip()

    results = {
        uid: info for uid, info in movie_data.items()
        if query in info["name"]
    }

    if not results:
        await message.reply_text(
           "⚡ Movie not found! Check spelling & try again.\n"
            "🚫 Oops! That one isn’t on OTT yet.\n"
            "🔎 No results! Use [Movie, Language] for better search.\n"
            "😕 Hmmm… we can’t locate this movie.\n"
            "🎬 Not available! Make sure it’s released on OTT."
        )
        return

    buttons = []
    for uid, info in list(results.items())[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=info["caption"][:35],
                callback_data=f"send:{uid}"
            )
        ])

    await message.reply_text(
        f"🎬 Found {len(results)} result(s):",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- SEND MOVIE (AUTO DELETE) ----------------
@app.on_callback_query(filters.regex("^send:"))
async def send_movie(client, callback_query):
    uid = callback_query.data.split(":")[1]
    movie = movie_data.get(uid)

    if not movie:
        await callback_query.answer("❌ Movie not found!", show_alert=True)
        return

    sent = await client.send_cached_media(
        chat_id=callback_query.message.chat.id,
        file_id=movie["file_id"],
        caption=(
            f"🎥 **{movie['caption']}**\n\n"
            "⚠️ Hurry up!\n"
            "⏱️ This movie will auto delete in 1 minute.\n"
            "📤 Forward it to another chat to save it."
        )
    )

    await callback_query.answer("📤 Movie sent!")

    # ⏱️ Wait 60 seconds
    await asyncio.sleep(60)

    # 🗑️ Delete movie message
    try:
        await client.delete_messages(
            chat_id=sent.chat.id,
            message_ids=sent.id
        )
    except:
        pass

# ---------------- HELP ----------------
@app.on_callback_query(filters.regex("^help$"))
async def help_button(client, callback_query):
    help_text = (
       "1️⃣ Send only the **main movie name** (e.g., `avengers`).\n"
        "2️⃣ Avoid extra words like `1080p`, `hindi`, `2022`.\n"
        "3️⃣ Click on the result button to get the movie.\n"
        "4️⃣ For any issues, contact @YourSupport."
    )
    await callback_query.message.edit_text(help_text)
    await callback_query.answer()

# ---------------- START BOT ----------------
print("🎬 Movie Filter Bot Started...")
app.run()
