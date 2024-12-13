import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Define states for the conversation handler
VIMEO_USERNAME_STATE = 1
VIMEO_PASSWORD_STATE = 2
URL_STATE = 3
VIDEO_PASSWORD_STATE = 4

# Dictionary to store user data temporarily
user_data = {}

# Start command that sends an introduction message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Please send me your Vimeo username.")

# Ask for Vimeo Username
async def handle_vimeo_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()

    if username:
        user_data[update.message.from_user.id] = {"vimeo_username": username, "vimeo_password": None, "url": None, "video_password": None}
        await update.message.reply_text("Now, please send me your Vimeo password.")
        return VIMEO_PASSWORD_STATE
    else:
        await update.message.reply_text("Please provide a valid Vimeo username.")
        return VIMEO_USERNAME_STATE

# Ask for Vimeo Password
async def handle_vimeo_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()

    if password:
        user_data[update.message.from_user.id]["vimeo_password"] = password
        await update.message.reply_text("Great! Now send me the Vimeo URL of the video you'd like to download.")
        return URL_STATE
    else:
        await update.message.reply_text("Please provide a valid Vimeo password.")
        return VIMEO_PASSWORD_STATE

# Handle Vimeo URL input
async def handle_vimeo_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # Check if the message contains a valid Vimeo URL
    if 'vimeo.com' in url:
        user_data[update.message.from_user.id]["url"] = url
        await update.message.reply_text("If the video is password-protected, please provide the video password.")
        return VIDEO_PASSWORD_STATE
    else:
        await update.message.reply_text("Please provide a valid Vimeo URL.")
        return URL_STATE

# Handle video password input and download the video using yt-dlp
async def handle_video_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    password = update.message.text.strip()  # Strip spaces from password

    if password:
        user_data[user_id]["video_password"] = password
    else:
        user_data[user_id]["video_password"] = None

    # Get Vimeo credentials from user data
    vimeo_username = user_data[user_id]["vimeo_username"]
    vimeo_password = user_data[user_id]["vimeo_password"]
    url = user_data[user_id]["url"]
    video_password = user_data[user_id]["video_password"]

    # Use yt-dlp to download the Vimeo video
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]+bestaudio[ext=mp4]/bestvideo[height<=720]+bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'username': vimeo_username,
            'password': vimeo_password,
            'video_password': video_password,  # Pass the video password provided by the user
            'verbose': True,  # Enable verbose logging for debugging
        }

        # Attempt to download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'Video')
            await update.message.reply_text(f"Downloaded {video_title} successfully!")

        # Clear the stored data for the user after download
        del user_data[user_id]

    except yt_dlp.utils.DownloadError as e:
        await update.message.reply_text(f"Error downloading video: {str(e)}")
        del user_data[user_id]  # Clear password and URL after failure

    return ConversationHandler.END

# If the conversation ends (user input invalid or completed)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

def main():
    # Create the Application and pass the bot token
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()

    # Create the ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            VIMEO_USERNAME_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vimeo_username)],
            VIMEO_PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vimeo_password)],
            URL_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vimeo_url)],
            VIDEO_PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add the conversation handler to the application
    application.add_handler(conversation_handler)

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
