import os
import yt_dlp
from telegram import Bot
from telegram.ext import CommandHandler, Updater

# Replace with your actual credentials
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Use environment variables for security
VIMEO_USERNAME = os.getenv('VIMEO_USERNAME')
VIMEO_PASSWORD = os.getenv('VIMEO_PASSWORD')

# Telegram bot handler
def start(update, context):
    update.message.reply_text("Hi! Send me a Vimeo URL, and I'll download it for you.")

def download_video(update, context):
    url = context.args[0] if context.args else None
    if not url:
        update.message.reply_text("Please provide a Vimeo URL.")
        return
    
    # Use yt-dlp to download the video
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]+bestaudio[ext=mp4]/bestvideo[height<=720]+bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # Saves to a 'downloads' folder
            'username': VIMEO_USERNAME,
            'password': VIMEO_PASSWORD,
            'noplaylist': True,  # Don't download entire playlists
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'Video')
            update.message.reply_text(f"Downloaded {video_title}")
    
    except Exception as e:
        update.message.reply_text(f"Error downloading video: {str(e)}")

# Start the bot
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("download", download_video))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
