import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
import yt_dlp

# Environment variables for security
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Define states for the conversation handler
URL_STATE = 1
PASSWORD_STATE = 2

# Dictionary to store the Vimeo URL and password temporarily for each user
user_data = {}

# Start command that sends an introduction message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a Vimeo URL, and I'll download it for you.")

# Handle Vimeo URL input
async def handle_vimeo_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # Check if the message contains a valid Vimeo URL (basic check for 'vimeo' in URL)
    if 'vimeo.com' in url:
        user_data[update.message.from_user.id] = {"url": url, "password": None}
        await update.message.reply_text("Please provide the video password (if applicable):")
        return PASSWORD_STATE
    else:
        await update.message.reply_text("Please provide a valid Vimeo URL.")
        return URL_STATE

# Handle password input and download the video using yt-dlp
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    password = update.message.text.strip()  # Strip spaces from the password
    url = user_data[user_id]["url"]

    # Store the password provided by the user
    user_data[user_id]["password"] = password

    # Use yt-dlp to download the Vimeo video
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]+bestaudio[ext=mp4]/bestvideo[height<=720]+bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'video_password': password,  # Correct way to pass the video password
        }

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
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Create the ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),
                      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vimeo_url)],
        states={
            URL_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_vimeo_url)],
            PASSWORD_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
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
