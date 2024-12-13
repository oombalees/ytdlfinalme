import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import yt_dlp

# Environment variables for security
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Dictionary to store the Vimeo URL and password temporarily for each user
user_data = {}

# State management constants
URL_STATE = 1
PASSWORD_STATE = 2

# Start command that sends an introduction message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a Vimeo URL, and I'll download it for you.")

# Handle Vimeo URL input
async def handle_vimeo_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # Check if the message contains a valid Vimeo URL (basic check for 'vimeo' in URL)
    if 'vimeo.com' in url:
        user_data[update.message.from_user.id] = {"url": url, "password": None, "state": PASSWORD_STATE}
        await update.message.reply_text("Please provide the video password (if applicable):")
    else:
        await update.message.reply_text("Please provide a valid Vimeo URL.")

# Handle password input and download the video using yt-dlp
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data and user_data[user_id]["state"] == PASSWORD_STATE:
        password = update.message.text
        url = user_data[user_id]["url"]

        # Store the password provided by the user
        user_data[user_id]["password"] = password

        # Use yt-dlp to download the Vimeo video
        try:
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]+bestaudio[ext=mp4]/bestvideo[height<=720]+bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'noplaylist': True,
                'password': password,  # Pass the user-provided password
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                video_title = info_dict.get('title', 'Video')
                await update.message.reply_text(f"Downloaded {video_title} successfully!")

            # Clear the stored data for the user after download
            del user_data[user_id]

        except Exception as e:
            await update.message.reply_text(f"Error downloading video: {str(e)}")
            del user_data[user_id]  # Clear password and URL after failure

    else:
        await update.message.reply_text("You need to send a valid Vimeo URL first.")

def main():
    # Create the Application and pass the bot token
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vimeo_url))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password))

    # Run the bot with webhook
    port = int(os.getenv("PORT", 5000))  # Render sets this environment variable
    application.run_webhook(
        listen="0.0.0.0",  # Listen on all available network interfaces
        port=port,         # Use the port Render provides
        url_path="",       # You can leave this blank if you don't need a custom path
        webhook_url=f"https://ytdlfinalme.onrender.com/"  # Replace with your actual Render URL
    )

if __name__ == '__main__':
    main()
