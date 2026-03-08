from datetime import datetime, timedelta
from telethon.sync import TelegramClient
from time import sleep
import sys
import requests
import hashlib
import hmac
import time
import asyncio

# Import configuration
try:
    from config import (
        TELEGRAM_API_ID,
        TELEGRAM_API_HASH,
        TELEGRAM_BOT_TOKEN,
        TELEGRAM_CHAT_ID,
        ZADARMA_API_KEY,
        ZADARMA_API_SECRET,
        FROM_NUMBER,
        TO_NUMBER,
        CHANNEL_USERNAMES,
        CHANNEL_FILTERS,
        BYPASS_KEYWORDS,
        CALL_COOLDOWN_MINUTES
    )
except ImportError:
    print("ERROR: config.py not found!")
    print("Please copy config.example.py to config.py and fill in your credentials.")
    sys.exit(1)

# -*- coding: utf-8 -*-
__version__ = '1.1.0'
from hashlib import sha1, md5
from collections import OrderedDict
if sys.version_info.major > 2:
    from urllib.parse import urlencode
else:
    from urllib import urlencode
import hmac
import base64


class ZadarmaAPI(object):

    def __init__(self, key, secret, is_sandbox=False):
        """
        Constructor
        :param key: key from personal
        :param secret: secret from personal
        :param is_sandbox: (True|False)
        """
        self.key = key
        self.secret = secret
        self.is_sandbox = is_sandbox
        self.__url_api = 'https://api.zadarma.com'
        if is_sandbox:
            self.__url_api = 'https://api-sandbox.zadarma.com'

    def call(self, method, params={}, request_type='GET', format='json', is_auth=True):
        """
        Function for send API request
        :param method: API method, including version number
        :param params: Query params
        :param request_type: (get|post|put|delete)
        :param format: (json|xml)
        :param is_auth: (True|False)
        :return: response
        """
        request_type = request_type.upper()
        if request_type not in ['GET', 'POST', 'PUT', 'DELETE']:
            request_type = 'GET'
        params['format'] = format
        auth_str = None
        is_nested_data = False
        for k in params.values():
            if not isinstance(k, str):
                is_nested_data = True
                break
        if is_nested_data:
            params_string = self.__http_build_query(OrderedDict(sorted(params.items())))
            params = params_string
        else:
            params_string = urlencode(OrderedDict(sorted(params.items())))

        if is_auth:
            auth_str = self.__get_auth_string_for_header(method, params_string)

        if request_type == 'GET':
            result = requests.get(self.__url_api + method + '?' + params_string, headers={'Authorization': auth_str})
        elif request_type == 'POST':
            result = requests.post(self.__url_api + method, headers={'Authorization': auth_str}, data=params)
        elif request_type == 'PUT':
            result = requests.put(self.__url_api + method, headers={'Authorization': auth_str}, data=params)
        elif request_type == 'DELETE':
            result = requests.delete(self.__url_api + method, headers={'Authorization': auth_str}, data=params)
        return result.text

    def __http_build_query(self, data):
        parents = list()
        pairs = dict()

        def renderKey(parents):
            depth, outStr = 0, ''
            for x in parents:
                s = "[%s]" if depth > 0 or isinstance(x, int) else "%s"
                outStr += s % str(x)
                depth += 1
            return outStr

        def r_urlencode(data):
            if isinstance(data, list) or isinstance(data, tuple):
                for i in range(len(data)):
                    parents.append(i)
                    r_urlencode(data[i])
                    parents.pop()
            elif isinstance(data, dict):
                for key, value in data.items():
                    parents.append(key)
                    r_urlencode(value)
                    parents.pop()
            else:
                pairs[renderKey(parents)] = str(data)

            return pairs
        return urlencode(r_urlencode(data))

    def __get_auth_string_for_header(self, method, params_string):
        """
        :param method: API method, including version number
        :param params: Query params dict
        :return: auth header
        """
        data = method + params_string + md5(params_string.encode('utf8')).hexdigest()
        hmac_h = hmac.new(self.secret.encode('utf8'), data.encode('utf8'), sha1)
        if sys.version_info.major > 2:
            bts = bytes(hmac_h.hexdigest(), 'utf8')
        else:
            bts = bytes(hmac_h.hexdigest()).encode('utf8')
        auth = self.key + ':' + base64.b64encode(bts).decode()
        return auth

def send_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        print(f"Failed to send message. Error: {response.text}")

z_api = ZadarmaAPI(key=ZADARMA_API_KEY, secret=ZADARMA_API_SECRET)

# Global call cooldown tracking
last_call_time = None
call_lock = asyncio.Lock()

async def make_call_if_allowed(bypass_cooldown=False):
    """Make a call only if 15 minutes have passed since the last call, or if cooldown is bypassed"""
    global last_call_time

    async with call_lock:
        now = datetime.now()

        # Check if we should make a call
        if bypass_cooldown:
            # Bypass cooldown - make the call immediately
            z_api.call('/v1/request/callback/', {'from': f'+{FROM_NUMBER}', 'to': f'+{TO_NUMBER}', 'predicted': 'true'}, 'GET')
            last_call_time = now
            print(f"[CALL] Made phone call at {now} (cooldown bypassed)")
            return True
        elif last_call_time is None or (now - last_call_time) >= timedelta(minutes=CALL_COOLDOWN_MINUTES):
            # Make the call
            z_api.call('/v1/request/callback/', {'from': f'+{FROM_NUMBER}', 'to': f'+{TO_NUMBER}', 'predicted': 'true'}, 'GET')
            last_call_time = now
            print(f"[CALL] Made phone call at {now}")
            return True
        else:
            time_since_last = (now - last_call_time).total_seconds() / 60
            print(f"[CALL] Skipped call - last call was {time_since_last:.1f} minutes ago (cooldown: {CALL_COOLDOWN_MINUTES} min)")
            return False

async def monitor_channel(client, channel_username):
    """Monitor a single channel for new messages"""
    print(f"Starting monitoring for channel: {channel_username}")

    # Get channel-specific filters if any
    channel_filter = CHANNEL_FILTERS.get(channel_username, None)
    if channel_filter:
        print(f"[{channel_username}] Channel has filters: {channel_filter}")

    while True:
        keep_looping = True
        async for message in client.iter_messages(channel_username, limit=1):
            last_message_id = message.id

        print(f"[{channel_username}] Starting new loop, last message id: {last_message_id}, {datetime.now()}")
        while keep_looping:
            # Get all new messages since last check (no limit)
            new_messages = []
            async for message in client.iter_messages(channel_username, min_id=int(last_message_id)):
                new_messages.append(message)

            # Process messages in chronological order (oldest first)
            new_messages.reverse()

            found_matching_message = False
            should_bypass_cooldown = False

            for message in new_messages:
                # Update last_message_id to track progress
                last_message_id = max(last_message_id, message.id)

                message_text = message.text if message.text else ""

                # If this channel has filters, check if message matches
                if channel_filter:
                    matches_filter = any(filter_text in message_text for filter_text in channel_filter)
                    if not matches_filter:
                        print(f"[{channel_username}] Message does not match filter, ignoring: {message_text[:50]}...")
                        continue  # Skip this message, don't process it

                print(f"[{channel_username}] New message: {message}")
                send_message(f"[{channel_username}] {message.text}")

                # Check if message contains any bypass keyword to bypass cooldown
                if any(keyword in message_text for keyword in BYPASS_KEYWORDS):
                    print(f"[{channel_username}] Message contains bypass keyword")
                    should_bypass_cooldown = True

                found_matching_message = True

            # Make only ONE phone call for the entire batch
            if found_matching_message:
                await make_call_if_allowed(bypass_cooldown=should_bypass_cooldown)

            # Always continue monitoring - cooldown is enforced by make_call_if_allowed
            print(f"[{channel_username}] Sleeping for 30 seconds, {datetime.now()}")
            await asyncio.sleep(30)

async def main():
    async with TelegramClient('session_name3', TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        print("Connected!")
        print(f"Monitoring {len(CHANNEL_USERNAMES)} channel(s): {', '.join(CHANNEL_USERNAMES)}")

        # Create tasks for each channel
        tasks = [monitor_channel(client, channel) for channel in CHANNEL_USERNAMES]

        # Run all channel monitors concurrently
        await asyncio.gather(*tasks)

# Properly start the event loop
asyncio.run(main())
