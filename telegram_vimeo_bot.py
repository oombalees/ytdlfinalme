import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import Application

# Replace with your actual credentials
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Use environment variables for security
VIMEO_USERNAME = os.getenv('VIMEO_USERNAME')
VIMEO_PASSWORD = os.getenv('VIMEO_PASSWORD')

# Telegram bot handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a Vimeo URL, and I'll download it for you.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0] if context.args else None
    if not url:
        await update.message.reply_text("Please provide a Vimeo URL.")
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
            await update.message.reply_text(f"Downloaded {video_title}")
    
    except Exception as e:
        await update.message.reply_text(f"Error downloading video: {str(e)}")

# Start the bot
def main():
    # Create the Application and pass the bot token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("download", download_video))

    # Set up the webhook URL (adjust the URL based on your Render app URL)
    webhook_url = "https://<your-app-name>.onrender.com/"  # Replace with your Render app URL

    # Set the webhook
    application.run_webhook(listen="0.0.0.0", port=5000, url_path="", webhook_url=webhook_url)

if __name__ == '__main__':
    main()
