# Silent Alarm

A Telegram channel monitoring system that makes phone calls when important alerts are received.

## Features

- Monitors multiple Telegram channels simultaneously
- Makes phone calls via Zadarma API when alerts are detected
- Channel-specific message filters
- 15-minute cooldown between calls (configurable)
- Bypass keywords for urgent alerts that ignore cooldown
- Sends Telegram notifications for all detected messages

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/shaharareli/silentalarm.git
cd silentalarm
```

### 2. Install dependencies

```bash
pip install telethon requests
```

### 3. Configure credentials

Copy the example configuration file and fill in your credentials:

```bash
cp config.example.py config.py
```

Edit `config.py` and add your actual credentials:

- **Telegram API credentials**: Get from https://my.telegram.org/apps
- **Telegram Bot credentials**: Get from @BotFather on Telegram
- **Zadarma API credentials**: Get from your Zadarma account
- **Phone numbers**: Your caller ID and destination number

### 4. Run the application

```bash
python silent_alarm.py
```

## Configuration

Edit `config.py` to customize:

- `CHANNEL_USERNAMES`: List of Telegram channels to monitor
- `CHANNEL_FILTERS`: Optional filters to only process specific messages from certain channels
- `BYPASS_KEYWORDS`: Keywords that ignore the call cooldown for urgent alerts
- `CALL_COOLDOWN_MINUTES`: Minutes to wait between calls (default: 15)

## How it works

1. The script monitors specified Telegram channels for new messages
2. When a message is detected:
   - If it matches channel filters (if configured), it proceeds
   - Sends a Telegram notification
   - Makes a phone call if:
     - 15 minutes have passed since the last call, OR
     - The message contains bypass keywords, OR
     - The message matches channel filters
3. Continues monitoring without blocking (no sleep after calls)

## Security

- Never commit `config.py` to git - it contains your credentials
- The `.gitignore` file is configured to exclude sensitive files
- Always use `config.example.py` as a template
