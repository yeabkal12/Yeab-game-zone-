# /bot/handlers.py (Final Version - All Features Combined)

import logging
import uuid
from decimal import Decimal
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
)

# Import our helper functions
from .wallet import send_otp_sms, initiate_chapa_deposit

logger = logging.getLogger(__name__)

# --- 1. Define Conversation States ---
# States for Game Creation
AWAITING_STAKE, AWAITING_WIN_CONDITION = range(2)
# States for Registration & Deposit
AWAITING_PHONE_FOR_REG, AWAITING_OTP, AWAITING_DEPOSIT_AMOUNT = range(2, 5)


# --- 2. Define the Main Keyboard Layout ---
main_keyboard = [
    [KeyboardButton("Play 🎮"), KeyboardButton("Register 👤")],
    [KeyboardButton("Deposit 💰"), KeyboardButton("Withdraw 💸")],
]
REPLY_MARKUP = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)


# --- 3. Main /start Command ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the main menu keyboard."""
    await update.message.reply_text(
        "Welcome to Yeab Game Zone! Please choose an option below.", 
        reply_markup=REPLY_MARKUP
    )


# --- 4. Game Creation Conversation Handlers (Preserved) ---

async def play_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point for the game creation conversation."""
    stake_buttons = [
        [InlineKeyboardButton("20 ETB", callback_data="stake_20"), InlineKeyboardButton("50 ETB", callback_data="stake_50")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_creation")]
    ]
    await update.message.reply_text("Please select a stake amount:", reply_markup=InlineKeyboardMarkup(stake_buttons))
    return AWAITING_STAKE

async def receive_stake(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves stake and asks for win condition."""
    query = update.callback_query
    await query.answer()
    context.user_data['stake'] = int(query.data.split('_')[1])
    win_buttons = [
        [InlineKeyboardButton("1 Token Home", callback_data="win_1"), InlineKeyboardButton("2 Tokens Home", callback_data="win_2")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_creation")]
    ]
    await query.edit_message_text("How many tokens to win?", reply_markup=InlineKeyboardMarkup(win_buttons))
    return AWAITING_WIN_CONDITION

async def receive_win_condition_and_create_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves win condition and creates the game lobby."""
    query = update.callback_query
    await query.answer()
    win_condition = int(query.data.split('_')[1])
    stake = context.user_data.get('stake', 'N/A')
    user = query.from_user
    game_id = 123 # Placeholder
    join_button = [[InlineKeyboardButton("Join Game", callback_data=f"join_{game_id}")]]
    lobby_message = f"📣 Game Lobby Created!\n👤 Creator: {user.first_name}\n💰 Stake: {stake} ETB\n🏆 Win: {win_condition} token(s)"
    await query.edit_message_text(text=lobby_message, reply_markup=InlineKeyboardMarkup(join_button))
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the game creation process."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Game creation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


# --- 5. Registration & Deposit Conversation Handlers (New) ---

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the registration process."""
    await update.message.reply_text("Please send your phone number to register (e.g., 0912345678).")
    return AWAITING_PHONE_FOR_REG

async def receive_phone_for_reg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives and saves the user's phone number."""
    # TODO: Save to DB with status 'unverified'
    await update.message.reply_text("Registration successful! Please use 'Deposit' to verify your account.", reply_markup=REPLY_MARKUP)
    return ConversationHandler.END

async def deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the deposit process, checking for verification."""
    # TODO: Fetch user status from DB
    user_status = "unverified" # Placeholder
    if user_status == "verified":
        await update.message.reply_text("Please enter the amount to deposit.")
        return AWAITING_DEPOSIT_AMOUNT
    else:
        otp_button = [[InlineKeyboardButton("Send OTP 📲", callback_data="send_otp")]]
        await update.message.reply_text("🔐 Please verify your account to continue.", reply_markup=InlineKeyboardMarkup(otp_button))
        return AWAITING_OTP

async def send_otp_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sends OTP to the user's phone."""
    query = update.callback_query
    await query.answer()
    # TODO: Fetch user's phone from DB
    phone_number = "0912345678" # Placeholder
    otp_code = send_otp_sms(phone_number)
    context.user_data['otp'] = otp_code
    await query.edit_message_text(text="✅ OTP sent! Please enter the code you received.")
    return AWAITING_OTP

async def receive_otp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verifies the OTP."""
    if update.message.text == context.user_data.get('otp'):
        # TODO: Update user status to 'verified' in DB
        context.user_data.clear()
        await update.message.reply_text("✅ Verification successful! Now, please enter the amount to deposit.")
        return AWAITING_DEPOSIT_AMOUNT
    else:
        await update.message.reply_text("❌ Invalid OTP. Please try again or /cancel.")
        return AWAITING_OTP

async def receive_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initiates Chapa transaction."""
    user_id = update.effective_user.id
    try:
        amount = Decimal(update.message.text)
        tx_ref = f"yeab-game-{user_id}-{uuid.uuid4()}"
        checkout_url = initiate_chapa_deposit(user_id, amount, tx_ref)
        if checkout_url:
            payment_button = [[InlineKeyboardButton("Click Here to Pay", url=checkout_url)]]
            await update.message.reply_text(f"To deposit {amount} ETB, please use the button below:", reply_markup=InlineKeyboardMarkup(payment_button))
        else:
            await update.message.reply_text("Sorry, we couldn't process your payment right now.")
        return ConversationHandler.END
    except (ValueError, TypeError):
        await update.message.reply_text("Please enter a valid number for the amount.")
        return AWAITING_DEPOSIT_AMOUNT

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """A generic cancel handler for all conversations."""
    await update.message.reply_text("Action cancelled.", reply_markup=REPLY_MARKUP)
    context.user_data.clear()
    return ConversationHandler.END


# --- 6. Main Setup Function (Combines All Handlers) ---
def setup_handlers(ptb_app: Application) -> Application:
    """Attaches all command and conversation handlers to the application."""

    # -- Conversation Handler for Game Creation --
    play_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Play 🎮$"), play_start)],
        states={
            AWAITING_STAKE: [CallbackQueryHandler(receive_stake, pattern="^stake_")],
            AWAITING_WIN_CONDITION: [CallbackQueryHandler(receive_win_condition_and_create_game, pattern="^win_")],
        },
        fallbacks=[CallbackQueryHandler(cancel_creation, pattern="^cancel_creation")],
    )
    
    # -- Conversation Handler for Registration & Deposit --
    reg_deposit_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Register 👤$"), register_start),
            MessageHandler(filters.Regex("^Deposit 💰$"), deposit_start),
        ],
        states={
            AWAITING_PHONE_FOR_REG: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone_for_reg)],
            AWAITING_OTP: [
                CallbackQueryHandler(send_otp_callback, pattern="^send_otp$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_otp),
            ],
            AWAITING_DEPOSIT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_deposit_amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
    )

    # Add all handlers to the application
    ptb_app.add_handler(CommandHandler("start", start_command))
    ptb_app.add_handler(play_conv_handler)
    ptb_app.add_handler(reg_deposit_conv_handler)
    
    # TODO: Add a CallbackQueryHandler for the "Join Game" button
    # ptb_app.add_handler(CallbackQueryHandler(join_game_callback, pattern="^join_"))

    return ptb_app