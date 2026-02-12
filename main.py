from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata, CurrencyItem, Item
from highrise.webapi import WebAPI
from flask import Flask
from threading import Thread
from highrise.__main__ import *
from typing import Union, cast, Literal
import time
import random
from importlib import import_module
import json
import asyncio
import os
import requests
from datetime import datetime, timedelta
from emotes import emote_list

class Mybot(BaseBot):
    def __init__(self):
        super().__init__()
        self.user_balances = {}

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("Bot is online!")

    async def on_chat(self, user: User, message: str) -> None:
        if message.lower() == "!ping":
            await self.highrise.chat(f"Pong! Hello {user.username}")

class WebServer():
    def __init__(self):
        self.app = Flask(__name__)
        @self.app.route('/')
        def index() -> str:
            return "Blackjack Casino Bot is running!"
    def run(self) -> None:
        self.app.run(host='0.0.0.0', port=5000)
    def keep_alive(self):
        t = Thread(target=self.run)
        t.start()


class RunBot():
    room_id = os.getenv("HIGHRISE_ROOM_ID", "672f16c63fe53a88e79e6f23")
    bot_token = os.getenv("HIGHRISE_BOT_TOKEN", "307a8df5b9a0905c6a64ea91f9741acc95f0e2b38d3d7aab249f09aa171f99c3")
    bot_file = "main"
    bot_class = "Mybot"

    def __init__(self) -> None:
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 999999  # Infinite retries
        self.reconnect_delay = 5

    def run_loop(self) -> None:
        """Main bot loop with auto-recovery and reconnection handling"""
        while True:
            try:
                self.reconnect_attempts = 0
                print("[BOT] Starting bot connection...")
                # Use a fresh bot instance on each connection attempt to reset state
                bot_instance = getattr(import_module(self.bot_file), self.bot_class)()
                definitions = [BotDefinition(bot_instance, self.room_id, self.bot_token)]  # type: ignore
                arun(main(definitions))  # type: ignore
            except Exception as e:
                self.reconnect_attempts += 1
                import traceback
                print(f"[BOT] Connection lost (attempt {self.reconnect_attempts}):")
                print(f"[BOT] Error: {e}")
                traceback.print_exc()

                # Reset counter to avoid overflow after 1000 attempts
                if self.reconnect_attempts > 1000:
                    self.reconnect_attempts = 1

                # Progressive backoff: start at 5s, max 30s
                delay = min(self.reconnect_delay * (2 ** min(self.reconnect_attempts - 1, 3)), 30)
                print(f"[BOT] Reconnecting in {delay}s...")
                time.sleep(delay)
            except KeyboardInterrupt:
                print("[BOT] Bot stopped by user")
                break


if __name__ == "__main__":
    WebServer().keep_alive()
    RunBot().run_loop()
