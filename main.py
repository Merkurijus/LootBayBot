import telebot
from telebot import types
import os
import math

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TRC20_ADDRESS = os.getenv("TRC20_ADDRESS")

bot = telebot.TeleBot(API_TOKEN)

# Prekių sąrašas
GAMES = {
    "Free Fire": [("530 Diamonds", 4.99), ("1060 Diamonds", 9.99)],
    "Mobile Legends": [("300 Diamonds", 3.99), ("1000 Diamonds", 8.49)],
    "Roblox": [("800 Robux", 7.49), ("1700 Robux", 14.99)],
    "CS:GO Skins": [("AWP | Asiimov", 28.49), ("USP-S | Cortex", 8.99)],
    "PUBG Mobile": [("690 UC", 5.49), ("1800 UC", 11.99)]
}

BONUSES = {
    100: "🎁 Bonus: You get a 30.00 $ gift!",
    50: "🎁 Bonus: You get a 10.00 $ gift!",
    25: "🎁 Bonus: You get a 5.00 $ gift!"
}

user_cart = {}

# Parinkimas žaidimo
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for game in GAMES:
        markup.add(game)
    markup.add("🛒 View Cart", "✅ Confirm Order")
    bot.send_message(message.chat.id, "🎮 Choose a game:", reply_markup=markup)

# Žaidimo prekių rodymas
@bot.message_handler(func=lambda msg: msg.text in GAMES)
def show_items(message):
    game = message.text
    markup = types.InlineKeyboardMarkup()
    for name, price in GAMES[game]:
        price_floor = math.floor(price)
        markup.add(types.InlineKeyboardButton(
            f"{name} - {price_floor}.00 $",
            callback_data=f"select:{game}:{name}:{price_floor}"
        ))
    bot.send_message(message.chat.id, f"🛍 Choose quantity for {game}:", reply_markup=markup)

# Kiekio pasirinkimas
@bot.callback_query_handler(func=lambda c: c.data.startswith("select:"))
def choose_quantity(call):
    _, game, name, price = call.data.split(":")
    markup = types.InlineKeyboardMarkup()
    for qty in [1, 2, 3, 5]:
        markup.add(types.InlineKeyboardButton(
            f"{qty}x", callback_data=f"add:{game}:{name}:{price}:{qty}"
        ))
    bot.edit_message_text(
        f"➕ How many *{name}*?",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Pridėjimas į krepšelį
@bot.callback_query_handler(func=lambda c: c.data.startswith("add:"))
def add_to_cart(call):
    _, game, name, price, qty = call.data.split(":")
    price = int(price)
    qty = int(qty)
    user_id = call.from_user.id

    if user_id not in user_cart:
        user_cart[user_id] = []

    user_cart[user_id].append({
        "game": game,
        "item": name,
        "price": price,
        "qty": qty
    })

    bot.send_message(call.message.chat.id, f"✅ Added {qty}x {name} to your cart.")

# Krepšelio peržiūra
@bot.message_handler(func=lambda msg: msg.text == "🛒 View Cart")
def view_cart(message):
    user_id = message.from_user.id
    cart = user_cart.get(user_id, [])
    if not cart:
        bot.send_message(message.chat.id, "🛒 Your cart is empty.")
        return

    msg = "🧾 Your cart:\n"
    total = 0
    for item in cart:
        line_total = item["price"] * item["qty"]
        total += line_total
        msg += f"- {item['qty']}x {item['item']} ({item['game']}) - {line_total}.00 $\n"

    bonus = ""
    for threshold, text in sorted(BONUSES.items(), reverse=True):
        if total >= threshold:
            bonus = text
            break

    msg += f"\n💰 Total: {total}.00 $\n{bonus}\n\n"
    msg += "📸 Send proof of payment to confirm."

    bot.send_message(message.chat.id, msg)

# Užsakymo patvirtinimas
@bot.message_handler(func=lambda msg: msg.text == "✅ Confirm Order")
def confirm_order(message):
    user_id = message.from_user.id
    cart = user_cart.get(user_id, [])
    if not cart:
        bot.send_message(message.chat.id, "❗ Your cart is empty.")
        return

    total = sum(item["price"] * item["qty"] for item in cart)
    msg = (
        f"✅ Please send *{total}.00 $* in USDT (TRC20) to:\n"
        f"`{TRC20_ADDRESS}`\n\n"
        f"📸 Then send payment screenshot + list gift preference (if any) here."
    )
    bot.send_message(message.chat.id, msg, parse_mode="Markdown")

# Mokėjimo įrodymas
@bot.message_handler(content_types=['photo', 'text'])
def handle_proof(message):
    user_id = message.from_user.id
    cart = user_cart.get(user_id, [])
    if cart:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ Submitted. Admin will check shortly.")
        user_cart[user_id] = []  # clear cart
    else:
        bot.send_message(message.chat.id, "❗ No items in your cart. Use /start")

# Paleidimas
print("✅ Bot is running...")
bot.polling(none_stop=True)
