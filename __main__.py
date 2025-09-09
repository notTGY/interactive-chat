import asyncio
import random
import os
from telegram import Update, InputMediaVideo, ReplyParameters
from telegram.ext import Application, MessageHandler, filters
from telegram.error import TelegramError
from dotenv import load_dotenv
import schedule

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables")
CHAT_ID = -1002678420298
MESSAGE_ID = 15


# CHAT_ID = -1002171080268
# MESSAGE_ID = 304

VIDEO_DIR = 'videos/'  # Folder with MP4s (e.g., vid1.mp4, vid2.mp4)
VIDEO_FILES = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')]
if not VIDEO_FILES:
    raise ValueError("No videos found in videos/ folder!")

minutes_between_updates = 1

caption = "The cycle continues..."
prev_video = ''

async def update_post(bot):
    global prev_video
    if prev_video:
        prev_video = random.choice(list(filter(lambda x: x != prev_video, VIDEO_FILES)))
    else:
        prev_video = random.choice(VIDEO_FILES)
    video_path = os.path.join(VIDEO_DIR, prev_video)

    try:
        with open(video_path, 'rb') as video:
            await bot.edit_message_media(
                chat_id=CHAT_ID,
                message_id=MESSAGE_ID,
                media=InputMediaVideo(media=video, caption=caption)
            )
    except TelegramError as e:
        print(f"Error updating post: {e}")

async def handle_interaction(update: Update, context):
    if (
        update.message
        and update.message.reply_to_message
        and update.message.reply_to_message.message_id == MESSAGE_ID
    ):
        print("Comment detected, updating video...")
        schedule.clear()  # Reset timer
        await update_post(context.bot)

def schedule_update(bot):
    schedule.every(minutes_between_updates).minutes.do(lambda: asyncio.create_task(update_post(bot)))

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interaction))
    await update_post(app.bot)
    schedule_update(app.bot)
    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        print("Bot is running...")
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)  # Prevent CPU hogging
    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = Application.builder().token(TOKEN).build()
    loop.run_until_complete(main())
