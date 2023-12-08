import asyncio
import os
import telebot
import threading
import g4f
import logging
import re
from collections import deque
from flask import Flask

# Specify logging level
logging.basicConfig(level=logging.DEBUG)

# Read API Token from environment variables
BOT_TOKEN: str = os.environ.get('BOT_TOKEN')
if (not BOT_TOKEN):
    logging.critical("Input token is empty!")
    raise Exception("Invalid BOT_TOKEN")
if (len(BOT_TOKEN) < 10):
    logging.critical("Input token is too short!")
    raise Exception("Invalid BOT_TOKEN")
if (":" not in BOT_TOKEN):
    logging.critical("Invalid input token format")
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

# Start a new conversation
@bot.message_handler(content_types=["text"], commands=['new'])
def start_new_conversation(inputMessage: telebot.types.Message):
    chat_id = inputMessage.chat.id
    if chat_id in chat_histories:
        del chat_histories[chat_id]
    bot.reply_to(inputMessage, "A new conversation has started. How can I assist you today?", parse_mode='Markdown')

# Provide user with a list of commands
@bot.message_handler(content_types=["text"], commands=['help'])
def send_welcome(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "To continue, use any of the commands from the list:\n/start | /hello - start communicating with the bot;\n/info - get more information on a project;\n/new - clear chat history and start a new conversation.\nOr ask anything you want to know just by sending a message.", parse_mode='Markdown')

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

# Handle non-text messages
@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
def default_command(inputMessage: telebot.types.Message):
    bot.reply_to(inputMessage, "Hi " + inputMessage.from_user.first_name + ",\nI'm very sorry but i have no idea on how to interact with this object")

# Create async reply
def ReplyAi(inputMessage: telebot.types.Message, botType):
    # Generate temporary reply
    newReply = bot.reply_to(inputMessage, "Please wait...")
    # Process the input query
    inputQuery = re.sub(r"\/(\w+)", "", inputMessage.text).strip()
    if (not inputQuery):
        inputQuery = "Hello, who are you?"
    logging.debug(inputQuery)
    # Get the conversation history for this chat
    chat_id = inputMessage.chat.id
    if chat_id not in chat_histories:
        chat_histories[chat_id] = deque(maxlen=15)
    chat_history = chat_histories[chat_id]
    # Add the new message to the conversation history
    chat_history.append({"role": "user", "content": inputQuery})
    # Create the GPT4FREE instance
    try:
        gptResponse: str = g4f.ChatCompletion.create(model=botType, messages=list(chat_history))
    except Exception as retExc:
        # Plot errors if needed
        logging.error(retExc)
        # Get response
        response = str(retExc)
        # Check if we have some known errors
        if (str(retExc).startswith("CaptchaChallenge:")):
            gptResponse = "This service is currently overloaded, please try again later"
        elif (str(retExc).startswith("\'adaptiveCards\'")):
            gptResponse = "Image generation is not yet supported"
        elif (str(retExc).startswith("\'message\'")):
            gptResponse = "This service is currently overloaded, please try again later"
        else:
            # Return the error message
            bot.edit_message_text(response, inputMessage.chat.id, newReply.id)
            return
    # Cleanup response from GPT if needed
    gptResponse = re.sub(r"(\[\^\d\^\])", "", gptResponse)
    # Handle some exceptions
    if (not gptResponse):
        gptResponse = "An empty response was returned..."
    # Add the AI's response to the conversation history
    chat_history.append({"role": "assistant", "content": gptResponse})
    # Process the input text
    bot.edit_message_text(gptResponse, inputMessage.chat.id, newReply.id)

app = Flask(__name__)

@app.route('/')
def index():
    logging.info("Starting bot")
    bot.infinity_polling()
