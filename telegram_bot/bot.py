import logging
import key
import os
import queue
import threading
import asyncio
from pytube import YouTube
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext


# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token
TELEGRAM_BOT_TOKEN = key.token

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

os.makedirs("./temp", exist_ok=True)

# Create a queue to manage URLs
url_queue = queue.Queue()
queue_lock = threading.Lock()

# Define a function to process URLs
async def process_url(bot: Bot):
    while True:
        item = url_queue.get()
        if item is None:
            break
        
        chat_id, url = item
        if 'youtube.com' in url or 'youtu.be' in url:
            try:
                yt = YouTube(url)
                audio_file = yt.streams.filter(only_audio=True).order_by("abr").desc().first().default_filename
                await bot.send_message(chat_id=chat_id, text=f'Downloading audio file {audio_file}, please wait...')
                logger.info(f'Downloading audio file {audio_file}, please wait... for user {chat_id}')
            except Exception as e:
                logger.error(e)
                await bot.send_message(chat_id=chat_id, text='An error occurred while fetching the link. Please make sure the link is correct')
                pass
            try:
                yt.streams.filter(only_audio=True).order_by("abr").desc().first().download("./temp")
                logger.info(f"{audio_file}, downloaded")
                await bot.send_message(chat_id=chat_id, text=f'audio file {audio_file} has been downloaed, sending...')
                audio_file = "./temp/" + audio_file
                print(audio_file)
            except Exception as e:
                logger.error(e)
                await bot.send_message(chat_id=chat_id, text=f'audio file {audio_file} couldnt be downloaed')
                pass
            try:
                await bot.send_audio(chat_id=chat_id, audio=open(audio_file, 'rb'))
                os.remove(audio_file)
            except Exception as e:
                logger.error(e)
                await bot.send_message(chat_id=chat_id, text='An error occurred while uploading the audio.')
        else:
            await bot.send_message(chat_id=chat_id, text='Please send a valid url')
        url_queue.task_done()

# Start a thread to process the URL queue
async def queue_worker(bot: Bot):
    while True:
        await process_url(bot)


# Define command handlers
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Send me a YouTube URL to get the audio.")

async def add_to_queue(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    chat_id = update.message.chat_id
    
    with queue_lock:
        url_queue.put((chat_id, url))
    
    await update.message.reply_text("Your URL has been added to the queue. Please wait...")


# Set up the Application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Register the handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_to_queue))

# Start the queue worker in an asyncio task
async def on_startup(application: Application):
    bot = application.bot
    asyncio.create_task(queue_worker(bot))

# Use post_init to add the on_startup hook
application.post_init(on_startup)

# Start the bot
application.run_polling()