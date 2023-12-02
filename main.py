import os
import telebot

# Read API Token from environment variables
BOT_TOKEN: str = os.environ.get('BOT_TOKEN')
if (not BOT_TOKEN):
    raise Exception("Invalid BOT_TOKEN")
if (len(BOT_TOKEN) < 10):
    raise Exception("Invalid BOT_TOKEN")
if (":" not in BOT_TOKEN):
    raise Exception("Invalid BOT_TOKEN")
# Generate bot object
bot = telebot.TeleBot(BOT_TOKEN)

# Handle AI command
@bot.message_handler(content_types=["text"], commands=['ai'])
def HandleAiMessage(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "* ai responds *")

# Welcome new users
@bot.message_handler(content_types=["text"], commands=['start', 'hello'])
def send_welcome(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "*Hello, " + inputMessage.from_user.first_name + "!*\nUse /help to get to know the available commands.\nHow can i assist you today?", parse_mode='Markdown')

# Give project information
@bot.message_handler(content_types=["text"], commands=['info'])
def send_welcome(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "This project is hosted on a GitHub repository. Here's the link: https://github.com/markoparfeniuk/Telegram-GPT")

# Provide user with a list of commands
@bot.message_handler(content_types=["text"], commands=['help'])
def send_welcome(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "*Let's chat!*\nTo continue, use any of the commands from the list:\n\n/start | /hello - start communicating with the bot\n/ai - for communication with AI\n/info - get more information on a project", parse_mode='Markdown')


if __name__ == "__main__":
    bot.infinity_polling()