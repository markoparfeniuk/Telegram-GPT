import asyncio
import os
import telebot
import threading
import g4f
import re
from collections import deque

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

# Create a dictionary to store the conversation history of each chat
chat_histories = {}

# Welcome new users
@bot.message_handler(content_types=["text"], commands=['start', 'hello'])
def send_welcome(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "*Hello, " + inputMessage.from_user.first_name + "!*\nUse /help to get to know the available commands or start chatting right away.\nHow can I assist you today?", parse_mode='Markdown')

# Give project information
@bot.message_handler(content_types=["text"], commands=['info'])
def send_welcome(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "This project is hosted on a GitHub repository. Here's the link: https://github.com/markoparfeniuk/Telegram-GPT")

# Provide user with a list of commands
@bot.message_handler(content_types=["text"], commands=['help'])
def send_welcome(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "*Let's chat!*\nTo continue, use any of the commands from the list:\n/start | /hello - start communicating with the bot;\n/info - get more information on a project.\nOr ask anything you want to know just by sending a message.", parse_mode='Markdown')

# Handle AI command
@bot.message_handler(content_types=["text"])
def HandleAiMessage(inputMessage: telebot.types.Message):
    # Check that the massage contains some text
    if (len(inputMessage.text) <= 5):
        bot.reply_to(inputMessage, "Hi " + inputMessage.from_user.first_name + ",\nplease give me some data to process.")
        return
    # Create async thread to handle replies
    thread = threading.Thread(target=ReplyAi, args=(inputMessage, "gpt-3.5-turbo"))
    thread.start()

# Create async reply
def ReplyAi(inputMessage: telebot.types.Message, botType):
    # Generate temporary reply
    newReply = bot.reply_to(inputMessage, "Please wait...")
    # Process the input query
    inputQuery = re.sub(r"\/(\w+)", "", inputMessage.text).strip()
    if (not inputQuery):
        inputQuery = "Hello, who are you?"
    # Get the conversation history for this chat
    chat_id = inputMessage.chat.id
    if chat_id not in chat_histories:
        chat_histories[chat_id] = deque(maxlen=15)
    chat_history = chat_histories[chat_id]
    # Add the new message to the conversation history
    chat_history.append({"role": "user", "content": inputQuery})
    # Create the GPT4FREE instance
    gptResponse: str = g4f.ChatCompletion.create(model=botType, messages=list(chat_history))
    # Cleanup response from GPT if needed
    gptResponse = re.sub(r"(\[\^\d\^\])", "", gptResponse)
    # Handle some exceptions
    if (not gptResponse):
        gptResponse = "An empty response was returned..."
    # Add the AI's response to the conversation history
    chat_history.append({"role": "assistant", "content": gptResponse})
    # Process the input text
    bot.edit_message_text(gptResponse, inputMessage.chat.id, newReply.id)


if __name__ == "__main__":
    bot.infinity_polling()