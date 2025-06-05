import telebot
from telebot import types
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
TRC20_ADDRESS = "TGGZH5ZmNckTmuh3ZxLm3NoGUJ3yJifavP"

bot = telebot.TeleBot(API_TOKEN)

BONUS_MESSAGE = {
    "tier1": "\n🎁 Bonus: You get a surprise gift for orders over 20 USDT!",
    "tier2": "\n🎁 Bonus: You get a 15 USDT gift for orders over 50 USDT!",
    "tier3": "\n🎁 Bonus: You get a 30 USDT gift for orders over 100 USDT!"
}

GAMES = {
    "Free Fire": [
        ("530 Diamonds", "4.50 USDT"),
        ("1060 Diamonds", "9.00 USDT")
    ],
    "Mobile Legends": [
        ("300 Diamonds", "4.00 USDT"),
        ("1000 Diamonds", "8.50 USDT")
    ],
    "Roblox": [
        ("800 Robux", "7.50 USDT"),
        ("1700 Robux", "15.00 USDT")
    ],
    "CS:GO Skins": [
        ("AWP | Asiimov", "29.00 USDT"),
        ("AK-47 | Redline", "19.00 USDT"),
        ("USP-S | Cortex", "9.00 USDT")
    ],
    "PUBG Mobile": [
        ("690 UC", "5.50 USDT"),
        ("1800 UC", "12.00 USDT")
    ]
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for game in GAMES.keys():
        markup.add(game)
    bot.send_message(
        message.chat.id,
        """🎮 Welcome to LootBayBot!

Choose your game below and get your top-up instantly using crypto 💰

🎁 *Bonus system:*
• Orders over 20 USDT – Surprise gift
• Orders over 50 USDT – 15 USDT gift
• Orders over 100 USDT – 30 USDT gift

👇 Select a game:""",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    print(f"[START] User: {message.from_user.id} started the bot")

@bot.message_handler(func=lambda msg: msg.text in GAMES.keys())
def game_selected(message):
    game = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option, price in GAMES[game]:
        markup.add(f"{game} | {option} | {price}")
    bot.send_message(message.chat.id, f"💎 Choose top-up for {game}:", reply_markup=markup)
    print(f"[SELECT] {message.from_user.id} selected {game}")

@bot.message_handler(func=lambda msg: any(g in msg.text for g in GAMES))
def topup_selected(message):
    try:
        parts = message.text.split(" | ")
        game, option, price_str = parts
        price = float(price_str.replace("USDT", "").strip())

        bonus_text = ""
        if price >= 100:
            bonus_text = BONUS_MESSAGE["tier3"]
        elif price >= 50:
            bonus_text = BONUS_MESSAGE["tier2"]
        elif price >= 20:
            bonus_text = BONUS_MESSAGE["tier1"]

        bot.send_message(
            message.chat.id,
            f"✅ You selected: {game} - {option} for {price_str}{bonus_text}\n\n"
            f"💰 Please send *{price_str}* to:\n`{TRC20_ADDRESS}` (TRC20 USDT)\n\n"
            "📸 Then send proof of payment to admin.",
            parse_mode="Markdown"
        )
        print(f"[ORDER] {message.from_user.id} - {game} - {option} - {price_str}")
    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        bot.send_message(message.chat.id, "⚠️ Invalid selection. Please start again with /start")

@bot.message_handler(content_types=['photo', 'text'])
def forward_payment_proof(message):
    if message.caption or message.text:
        try:
            bot.forward_message(int(ADMIN_ID), message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "✅ Proof sent to admin. We will verify and respond shortly.")
            print(f"[PROOF] Forwarded from {message.from_user.id}")
        except Exception as e:
            print(f"[FORWARD ERROR] {e}")
            bot.send_message(message.chat.id, "❌ Failed to forward message.")
    else:
        bot.send_message(message.chat.id, "❗ Please send text or a photo with your Game ID and payment proof.")

# Start bot
print("✅ Botas veikia. Laukia žinučių...")
bot.polling(none_stop=True)
