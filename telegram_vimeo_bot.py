import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Replace with your actual credentials
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Use environment variables for security

# Dictionary to store the URL and password temporarily
user_passwords = {}

# Telegram bot handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a Vimeo URL, and I'll download it for you.")

async def handle_vimeo_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text  # Get the user's URL message

    # Ask the user for the video password
    user_passwords[update.message.from_user.id] = {"url": url}
    await update.message.reply_text("Please provide the video password:")

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_passwords and "url" in user_passwords[user_id]:
        password = update.message.text
        url = user_passwords[user_id]["url"]

        # Use yt-dlp to download the video
        try:
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]+bestaudio[ext=mp4]/bestvideo[height<=720]+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',  # Saves to a 'downloads' folder
                'noplaylist': True,  # Don't download entire playlists
                'username': None,  # If you need to authenticate for the video, use Vimeo username here
                'password': password,  # Use the user-provided password for the Vimeo video
            }

            # Start the download process
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', 'Video')
                await update.message.reply_text(f"Downloaded {video_title}")

            # Clear the stored password after the download is complete
            del user_passwords[user_id]
        except Exception as e:
            await update.message.reply_text(f"Error downloading video: {str(e)}")
            del user_passwords[user_id]  # Clear password on failure
    else:
        await update.message.reply_text("You need to send a valid Vimeo URL first.")

def main():
    # Create the Application and pass the bot token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vimeo_url))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))

    # Run the bot with webhook (or use run_polling() for polling)
    application.run_polling()

if __name__ == '__main__':
    main()
