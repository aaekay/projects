
import key
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext, ApplicationBuilder
from pytube import YouTube
import os
from pathlib import Path

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

os.makedirs("./temp", exist_ok=True)
# Define your bot token here
TOKEN = key.token

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me a YouTube link and I will send you the extracted audio.')

async def download_audio(update: Update, context: CallbackContext) -> None:
    """Download audio from YouTube link and send it back to the user."""
    url = update.message.text
    if 'youtube.com' in url or 'youtu.be' in url:
        await update.message.reply_text('Getting the link, please wait...')
        try:
            yt = YouTube(url)
            audio_file = yt.streams.filter(only_audio=True).order_by("abr").desc().first().default_filename
            await update.message.reply_text(f'Downloading audio file {audio_file}, please wait...')
            logger.info(f'Downloading audio file {audio_file}, please wait...')
        except Exception as e:
            logger.error(e)
            await update.message.reply_text('An error occurred while fetching the link. Please make sure the link is correct')
            pass
        try:
            yt.streams.filter(only_audio=True).order_by("abr").desc().first().download("./temp")
            logger.info(f"{audio_file}, downloaded")
            await update.message.reply_text(f'audio file {audio_file} has been downloaed, sending...')
            audio_file = "./temp/" + audio_file
            print(audio_file)
        except Exception as e:
            logger.error(e)
            await update.message.reply_text(f'audio file {audio_file} couldnt be downloaed')
            pass
        try:
            await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(audio_file, 'rb'))
            os.remove(audio_file)
        except Exception as e:
            logger.error(e)
            await update.message.reply_text('An error occurred while uploading the audio.')
    else:
        await update.message.reply_text('Please send a valid YouTube link.')

def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_audio))

    application.run_polling()

if __name__ == '__main__':
    main()
