import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Add your Telegram bot token here
TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'

# Your Vimeo credentials (only the username and password for the account)
VIMEO_USERNAME = 'VIMEO_USERNAME'
VIMEO_PASSWORD = 'VIMEO_PASSWORD'

# Directory to store videos
DOWNLOAD_DIR = 'downloads/'

# Ensure the download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Define conversation states
VIDEO_URL, VIDEO_PASSWORD = range(2)

# Function to download the video
def download_video(url: str, video_password: str) -> str:
    try:
        command = [
            'yt-dlp',
            '-u', VIMEO_USERNAME,
            '-p', VIMEO_PASSWORD,
            '--video-password', video_password,
            '-f', 'bestaudio[ext=m4a]+bestaudio[ext=mp4]/bestvideo[height<=720]+bestaudio/best',
            '-o', os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            url
        ]
        
        # Run the command to download the video
        subprocess.run(command, check=True)
        # Get the downloaded file's path
        video_file = max([f for f in os.listdir(DOWNLOAD_DIR)], key=lambda f: os.path.getctime(os.path.join(DOWNLOAD_DIR, f)))
        return os.path.join(DOWNLOAD_DIR, video_file)
    
    except Exception as e:
        return f"Error downloading video: {str(e)}"

# Start command
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Hello! Send me Vimeo video URLs, and I'll download them for you.")
    return VIDEO_URL

# Handle video URL input
def handle_video_url(update: Update, context: CallbackContext) -> int:
    video_url = update.message.text.strip()
    
    # Save the URL for the next step
    context.user_data['video_url'] = video_url
    
    # Check if the URL requires a password
    update.message.reply_text(f"Got it! This video may be password-protected. Please provide the video password:")
    return VIDEO_PASSWORD

# Handle video password input
def handle_video_password(update: Update, context: CallbackContext) -> int:
    video_password = update.message.text.strip()
    
    # Retrieve the saved video URL
    video_url = context.user_data.get('video_url')
    
    # Download the video with the provided password
    video_path = download_video(video_url, video_password)
    
    # If download was successful, send the video file back
    if os.path.exists(video_path):
        with open(video_path, 'rb') as video_file:
            update.message.reply_video(video_file)
        os.remove(video_path)  # Remove video file after sending
    else:
        update.message.reply_text(f"Failed to download video from {video_url}. Please check the password or URL.")
    
    # Clear the user data and return to the start state
    context.user_data.clear()
    return ConversationHandler.END

# Cancel command (can be used to stop the bot)
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Goodbye!")
    context.user_data.clear()
    return ConversationHandler.END

# Set up the conversation handler with states
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Define the conversation handler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            VIDEO_URL: [MessageHandler(Filters.text & ~Filters.command, handle_video_url)],
            VIDEO_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, handle_video_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add the conversation handler to the dispatcher
    dispatcher.add_handler(conversation_handler)

    # Start polling to receive updates
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
