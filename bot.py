import os
from telegram.constants import ParseMode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import logging
import dotenv

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

TOKEN = os.environ.get('TOKEN')  # Replace with your Bot Token
PASSWORD = os.environ.get('PASSWORD')  # Set your password here
OWNER_ID = os.environ.get('OWNER_ID')  # Set the owner's Telegram ID here

# Store authenticated users and subscribers
authenticated_users = set()
subscribers = set()
blocked_users = set()
posts = {}

# Bot data
bot_data = {
    'name': '𝗪𝗮𝗳𝗶𝘆𝕭𝖔𝖙𝓥2😈',
    'about': 'This is a bot for managing subscribers.',
    'description': 'A detailed description of the bot.',
    'pic': 'path_to_default_picture'  # Replace with the path to your picture
}

# Check if the user is the owner
def is_owner(user_id):
    return user_id == OWNER_ID

# Start command with menu
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in blocked_users:
        await update.message.reply_text("You are blocked from using this bot.", parse_mode=ParseMode.MARKDOWN)
        return
    
    keyboard = [
        [InlineKeyboardButton("Help", callback_data='help')],
        [InlineKeyboardButton("Settings", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_owner(user_id):
        await update.message.reply_text("Welcome, Owner!", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        if user_id in authenticated_users:
            await update.message.reply_text("You're already authenticated!", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("I'm alive! Please enter the password to proceed.", parse_mode=ParseMode.MARKDOWN)

# Password handling
async def check_password(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    
    if user_id in blocked_users:
        await update.message.reply_text("You are blocked from using this bot.", parse_mode=ParseMode.MARKDOWN)
        return
    
    if user_id == OWNER_ID:
        authenticated_users.add(user_id)  # Owner is always authenticated
        await update.message.reply_text("Access granted! You can now use the bot.\n", parse_mode=ParseMode.MARKDOWN)
    elif user_id not in authenticated_users:
        if update.message.text == PASSWORD:
            authenticated_users.add(user_id)
            subscribers.add(user_id)  # Automatically subscribe user upon authentication
            await update.message.reply_text("Access granted! You can now use the bot.\n/start", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("Incorrect password. Please try again.", parse_mode=ParseMode.MARKDOWN)

# Settings handling
async def settings(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.from_user.id
    if is_owner(user_id):
        keyboard = [
            [InlineKeyboardButton("Remove Subscriber by Username", callback_data='remove_subscriber_command')],
            [InlineKeyboardButton("View All Subscribers", callback_data='view_subscribers_command')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text("Choose a setting to edit:", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        await update.callback_query.answer()
    else:
        await update.callback_query.answer(text="You are not admin.\n/start")


# Remove subscriber by username
async def remove_subscriber(update: Update, context: CallbackContext) -> None:
    if is_owner(update.message.from_user.id):
        if context.args:
            username = context.args[0]
            user_to_remove = None

            # Attempt to find the subscriber with the given username
            for subscriber_id in subscribers:
                try:
                    user = await context.bot.get_chat(subscriber_id)
                    if user.username == username:
                        user_to_remove = subscriber_id
                        break
                except Exception as e:
                    logger.error(f"Failed to fetch subscriber info for {subscriber_id}: {e}")

            if user_to_remove:
                subscribers.remove(user_to_remove)
                authenticated_users.discard(user_to_remove)  # Remove authentication on unsubscribe
                await update.message.reply_text(f"Subscriber @{username} has been removed.", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"Subscriber @{username} not found.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("Please provide the username to remove. \nUsage: /remove_subscriber <username>", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)


# View all subscribers
async def view_subscribers(update: Update, context: CallbackContext) -> None:
    if is_owner(update.message.from_user.id):
        if not subscribers:
            await update.message.reply_text("No subscribers found.", parse_mode=ParseMode.MARKDOWN)
            return
        
        subscribers_text = f"Subscribers ({len(subscribers)} total):\n"
        for subscriber_id in subscribers:
            status = "Blocked" if subscriber_id in blocked_users else "Active"
            try:
                user = await context.bot.get_chat(subscriber_id)
                username = user.username if user.username else "No username"
                first_name = user.first_name
                last_name = user.last_name if user.last_name else "No last name"
                subscribers_text += f"@{username} - {first_name} {last_name} ({status})\n"
            except Exception as e:
                logger.error(f"Failed to fetch subscriber info for {subscriber_id}: {e}")
        
        # Split subscribers list into chunks if it exceeds the limit
        max_message_length = 4096
        for i in range(0, len(subscribers_text), max_message_length):
            await update.message.reply_text(subscribers_text[i:i + max_message_length], parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)

# Store all interacted users
all_users = set()

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    if user_id in blocked_users:
        await update.message.reply_text("You are blocked from using this bot.", parse_mode=ParseMode.MARKDOWN)
        return

    # Add user to all_users
    all_users.add(user_id)

    keyboard = [
        [InlineKeyboardButton("Help", callback_data='help')],
        [InlineKeyboardButton("Settings", callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_owner(user_id):
        await update.message.reply_text("Welcome, Owner!", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    else:
        if user_id in authenticated_users:
            await update.message.reply_text("You're already authenticated!\nUse /off to pause your subscription.", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("I'm alive! Please enter the password to proceed.", parse_mode=ParseMode.MARKDOWN)

async def post_message(update: Update, context: CallbackContext) -> None:
    if is_owner(update.message.from_user.id):
        if not context.args:
            await update.message.reply_text("Please provide a message to post.", parse_mode=ParseMode.MARKDOWN)
            return

        message_type = context.args[0].lower()
        content = ' '.join(context.args[1:])

        if message_type not in ['text', 'photo', 'document']:
            await update.message.reply_text("Invalid message type. Use 'text', 'photo', or 'document'.", parse_mode=ParseMode.MARKDOWN)
            return

        if message_type in ['text', 'document'] and not content.strip():
            await update.message.reply_text(f"{message_type.capitalize()} content cannot be empty.", parse_mode=ParseMode.MARKDOWN)
            return

        photo_url = content if message_type == 'photo' else None
        text = content if message_type != 'photo' else None

        keyboard = [
            [InlineKeyboardButton("From Admin", callback_data=f'done_{update.message.message_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send message to all users
        sent_count = 0
        failed_count = 0

        for user_id in all_users:
            try:
                if message_type == 'text':
                    await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup)
                elif message_type == 'photo':
                    await context.bot.send_photo(chat_id=user_id, photo=photo_url, caption=text, reply_markup=reply_markup)
                elif message_type == 'document':
                    await context.bot.send_document(chat_id=user_id, document=content, caption=text, reply_markup=reply_markup)
                sent_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send {message_type} to {user_id}: {e}")

        posts[update.message.message_id] = {'type': message_type, 'content': content, 'reactions': {'like': 0, 'dislike': 0}, 'viewed_by': set()}

        if sent_count > 0:
            await update.message.reply_text(f"{message_type.capitalize()} posted to {sent_count} users.", parse_mode=ParseMode.MARKDOWN)
        if failed_count > 0:
            await update.message.reply_text(f"Failed to send {message_type} to {failed_count} users.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)




# View reactions
async def view_reactions(update: Update, context: CallbackContext) -> None:
    if is_owner(update.message.from_user.id):
        if context.args:
            try:
                post_id = int(context.args[0])
                if post_id in posts:
                    reactions = posts[post_id]['reactions']
                    viewed_by = posts[post_id]['viewed_by']
                    reactions_text = (
                        f"Post ID: {post_id}\n"
                        f"Likes: {reactions['like']}\n"
                        f"Dislikes: {reactions['dislike']}\n"
                        f"Viewed by: {len(viewed_by)} users"
                    )
                    await update.message.reply_text(reactions_text, parse_mode=ParseMode.MARKDOWN)
                else:
                    await update.message.reply_text("Post ID not found.", parse_mode=ParseMode.MARKDOWN)
            except ValueError:
                await update.message.reply_text("Invalid post ID format.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("Please provide a post ID to view reactions.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)

# Handle callback queries
async def callback_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data == 'help':
        help_text = (
            "Use the following commands:\n"
            "/start - Start the bot\n"
            "/remove_subscriber <username> - Remove a subscriber\n"
            "/view_subscribers - View all subscribers\n"
            "/post_message <message> [photo] - Post a message with an optional photo to all subscribers\n"
            "/post_message text nani kore\n"
            "/view_reactions <post_id> - View reactions to a specific post\n"
            "/block <username> - Block a subscriber\n"
            "/unblock <username> - Unblock a subscriber"
        )
        await query.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    elif data == 'settings':
        await settings(update, context)
    elif data == 'remove_subscriber_command':
        if is_owner(user_id):
            await query.message.reply_text("/remove_subscriber", parse_mode=ParseMode.MARKDOWN)
        else:
            await query.answer("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)
    elif data == 'view_subscribers_command':
        if is_owner(user_id):
            await query.message.reply_text("/view_subscribers", parse_mode=ParseMode.MARKDOWN)
        else:
            await query.answer("You are not admin.\n/start")
    elif data.startswith('like_') or data.startswith('dislike_'):
        post_id = int(data.split('_')[1])
        if post_id in posts:
            reaction_type = 'like' if data.startswith('like_') else 'dislike'
            posts[post_id]['reactions'][reaction_type] += 1
            user_id = update.callback_query.from_user.id
            posts[post_id]['viewed_by'].add(user_id)
            await query.answer(f"{reaction_type.capitalize()} recorded!")
    elif data.startswith('done_'):
        post_id = int(data.split('_')[1])
        if post_id in posts:
            await query.answer("Thank you! Your response has been recorded.")
        else:
            await query.answer("Post ID not found.")



# Block a subscriber
async def block_subscriber(update: Update, context: CallbackContext) -> None:
    if is_owner(update.message.from_user.id):
        if context.args:
            username = context.args[0]
            user_to_block = None
            for subscriber_id in subscribers:
                try:
                    user = await context.bot.get_chat(subscriber_id)
                    if user.username == username:
                        user_to_block = subscriber_id
                        break
                except Exception as e:
                    logger.error(f"Failed to fetch subscriber info for {subscriber_id}: {e}")
            
            if user_to_block:
                blocked_users.add(user_to_block)
                await update.message.reply_text(f"Subscriber @{username} has been blocked.", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"Subscriber @{username} not found.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("Please provide the username to block.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)

# Unblock a subscriber
async def unblock_subscriber(update: Update, context: CallbackContext) -> None:
    if is_owner(update.message.from_user.id):
        if context.args:
            username = context.args[0]
            user_to_unblock = None
            for subscriber_id in blocked_users:
                try:
                    user = await context.bot.get_chat(subscriber_id)
                    if user.username == username:
                        user_to_unblock = subscriber_id
                        break
                except Exception as e:
                    logger.error(f"Failed to fetch subscriber info for {subscriber_id}: {e}")
            
            if user_to_unblock:
                blocked_users.remove(user_to_unblock)
                await update.message.reply_text(f"Subscriber @{username} has been unblocked.", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(f"Subscriber @{username} not found.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("Please provide the username to unblock.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)
        
# Command Handlers for /on and /off commands
async def subscribe(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id == OWNER_ID or user_id in authenticated_users:
        if user_id not in subscribers:
            subscribers.add(user_id)
            await update.message.reply_text("You have been subscribed.", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("You are already subscribed.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)

async def unsubscribe(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id == OWNER_ID or user_id in authenticated_users:
        if user_id in subscribers:
            subscribers.remove(user_id)
            authenticated_users.discard(user_id)  # Discard authentication on unsubscribe
            await update.message.reply_text("Your subscription is paused.\nPlease enter password to subscribe!", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("You are not subscribed.", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("You are not admin.\n/start", parse_mode=ParseMode.MARKDOWN)        

# Main function to run the bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler('on', subscribe))
    application.add_handler(CommandHandler('off', unsubscribe))
    application.add_handler(CommandHandler("remove_subscriber", remove_subscriber))
    application.add_handler(CommandHandler("view_subscribers", view_subscribers))
    application.add_handler(CommandHandler("post_message", post_message))
    application.add_handler(CommandHandler("view_reactions", view_reactions))
    application.add_handler(CommandHandler("block", block_subscriber))
    application.add_handler(CommandHandler("unblock", unblock_subscriber))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_password))
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
