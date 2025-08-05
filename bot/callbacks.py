# /bot/callbacks.py (Final, Perfected Version)

import logging
from telegram import (Update, ReplyKeyboardMarkup, KeyboardButton,
                        InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo)
from telegram.ext import ContextTypes, ConversationHandler

# --- 1. Setup & Configuration ---
logger = logging.getLogger(__name__)

# --- 2. Define Conversation States ---
# These constants represent the different steps in our game creation conversation.
AWAITING_STAKE, AWAITING_WIN_CONDITION = range(2)


# --- 3. Define the Main Keyboard (ReplyKeyboardMarkup) ---
# This is the permanent keyboard shown to the user.
# It's defined here so our start command can easily access it.
main_keyboard = [
    [KeyboardButton("Play 🎮")], # We will handle this text button
    [KeyboardButton("Deposit 💰"), KeyboardButton("Withdraw 💸")],
    [KeyboardButton("Balance 🏦"), KeyboardButton("Contact Us 📞")],
]
REPLY_MARKUP = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)


# --- 4. Main Command Callbacks ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command.
    Greets the user and displays the main menu keyboard.
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot.")
    
    welcome_message = (
        f"Welcome to Yeab Game Zone, {user.first_name}!\n\n"
        "Ready for the ultimate Ludo experience? Tap 'Play' to begin."
    )
    
    await update.message.reply_text(welcome_message, reply_markup=REPLY_MARKUP)


# --- 5. Game Creation Conversation (ConversationHandler Callbacks) ---

async def play_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point for the game creation conversation.
    Triggered by the 'Play 🎮' button. Asks for the stake amount.
    """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} initiated game creation.")

    # These are temporary buttons attached to the message.
    stake_buttons = [
        [
            InlineKeyboardButton("20 ETB", callback_data="stake_20"),
            InlineKeyboardButton("50 ETB", callback_data="stake_50"),
            InlineKeyboardButton("100 ETB", callback_data="stake_100"),
        ],
        [InlineKeyboardButton("Cancel", callback_data="cancel_creation")]
    ]
    inline_markup = InlineKeyboardMarkup(stake_buttons)
    
    await update.message.reply_text(
        "Please select a stake amount for the game:",
        reply_markup=inline_markup
    )
    
    # This tells the ConversationHandler to move to the AWAITING_STAKE state.
    return AWAITING_STAKE

async def receive_stake(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the user's stake selection.
    Saves the choice and asks for the winning condition.
    """
    query = update.callback_query
    await query.answer()  # Acknowledge the button tap

    # context.user_data is a temporary dictionary to store info during a conversation.
    stake_amount = int(query.data.split('_')[1])
    context.user_data['stake'] = stake_amount
    
    logger.info(f"User {query.from_user.id} chose stake: {stake_amount} ETB.")

    win_condition_buttons = [
        [
            InlineKeyboardButton("First Token Home", callback_data="win_1"),
            InlineKeyboardButton("Two Tokens Home", callback_data="win_2"),
            InlineKeyboardButton("All Four Home", callback_data="win_4"),
        ],
        [InlineKeyboardButton("Cancel", callback_data="cancel_creation")]
    ]
    inline_markup = InlineKeyboardMarkup(win_condition_buttons)

    # Edit the existing message to keep the chat clean.
    await query.edit_message_text(
        text="Great! Now, how many tokens does a player need to get home to win?",
        reply_markup=inline_markup
    )

    return AWAITING_WIN_CONDITION

async def receive_win_condition_and_create_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handles the win condition selection.
    Creates the game lobby message and ends the conversation.
    """
    query = update.callback_query
    await query.answer()

    win_condition = int(query.data.split('_')[1])
    stake = context.user_data.get('stake', 'N/A')
    user = query.from_user

    logger.info(f"User {user.id} chose win condition: {win_condition}. Creating game lobby.")

    # --- TODO: Database Logic Goes Here ---
    # 1. Check user's balance. If insufficient, send error and cancel.
    # 2. Create a new game record in the 'games' table with status 'lobby'.
    # 3. Get the unique game_id from the newly created record.
    game_id = 123  # Using a placeholder for now

    join_button = [[InlineKeyboardButton("Join Game", callback_data=f"join_{game_id}")]]
    inline_markup = InlineKeyboardMarkup(join_button)

    lobby_message = (
        f"📣 **Game Lobby Created!**\n\n"
        f"👤 **Creator:** {user.first_name}\n"
        f"💰 **Stake:** {stake} ETB\n"
        f"🏆 **Win Condition:** {win_condition} token(s) home\n\n"
        f"Waiting for an opponent to join..."
    )

    await query.edit_message_text(text=lobby_message, reply_markup=inline_markup, parse_mode='Markdown')
    
    # Clean up temporary data
    context.user_data.clear()
    
    # End the conversation
    return ConversationHandler.END

async def cancel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback for the 'Cancel' button during game creation.
    Ends the conversation cleanly.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Game creation has been cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

# --- 6. Other Callbacks (e.g., for 'Join Game' button) ---

async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles a player clicking the 'Join Game' button from a lobby message.
    """
    query = update.callback_query
    await query.answer()
    
    game_id = query.data.split('_')[1]
    joining_player = query.from_user
    logger.info(f"User {joining_player.id} attempting to join game {game_id}.")

    # --- TODO: Full Game Start Logic Goes Here ---
    # 1. Fetch game details and creator_id from the database using game_id.
    # 2. Check balances for both players.
    # 3. Deduct stake from both players.
    # 4. Update game status to 'active'.
    # 5. Create the LudoGame instance, render the board, and start the game.

    await query.edit_message_text(text=f"Game {game_id} is starting now!")