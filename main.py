import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7525042799:AAG0QPaFHayvOM6i21hos3Sw0NBOleUr1II'
ADMIN_ID = 7343018188

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("📤 Submit Proof + Game ID", callback_data="submit_proof")
    )
    bot.send_message(message.chat.id, "Welcome! Choose an option below:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "submit_proof")
def handle_proof_request(call):
    bot.send_message(call.message.chat.id, "📎 Please send your *payment proof* and *in-game ID* in one message.", parse_mode="Markdown")

@bot.message_handler(content_types=['photo', 'text'])
def handle_submission(message):
    if message.photo or message.text:
        bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
        bot.send_message(message.chat.id, "✅ Submitted! We will review and get back to you shortly.")
    else:
        bot.send_message(message.chat.id, "❗ Please send a screenshot or details. Try again with /start.")

print("🤖 Bot started...")
bot.infinity_polling()
