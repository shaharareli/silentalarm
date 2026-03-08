# Configuration file for Silent Alarm
# Copy this file to config.py and fill in your actual credentials

# Telegram API credentials
# Get these from https://my.telegram.org/apps
TELEGRAM_API_ID = 'your_api_id'
TELEGRAM_API_HASH = 'your_api_hash'

# Telegram Bot credentials
# Get these from @BotFather on Telegram
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"

# Zadarma API credentials
# Get these from your Zadarma account
ZADARMA_API_KEY = "your_zadarma_api_key"
ZADARMA_API_SECRET = "your_zadarma_api_secret"

# Phone numbers (in international format with country code)
FROM_NUMBER = "972XXXXXXXXX"  # The number making the call (caller ID)
TO_NUMBER = "972XXXXXXXXX"    # The number to call

# Telegram public channel usernames (can add multiple channels)
CHANNEL_USERNAMES = ['beforeredalert', 'Yemennews7071', 'PikudHaOref_2']

# Channel-specific filters: only process messages that contain these texts
CHANNEL_FILTERS = {
    'PikudHaOref_all': ['תל אביב - מרכז העיר']
}

# Keywords that bypass the cooldown
BYPASS_KEYWORDS = ["מרכז", "גוש דן"]

# Call cooldown in minutes
CALL_COOLDOWN_MINUTES = 15
