import os
import aiohttp
import asyncio
import pathlib

import telethon
from telethon import events
from telethon.tl.custom import Button
from telethon.tl.types import DocumentAttributeFilename

from .ConfigApi import ConfigApi
from Utils.DebugPrinter import DPrint
from .Downloader import get_extension, FileDownloaderFromMessage, get_bare_filename


dprint = DPrint('BOT')
SERVER_URL = "http://localhost:8080"

async def render_via_server(obj_path: str) -> str:
    async with aiohttp.ClientSession() as session:
        # 1) отправляем рендер
        async with session.post(f"{SERVER_URL}/render", json={"obj_path": obj_path}) as resp:
            data = await resp.json()
            job_id = data["job_id"]

        # 2) ждём готовности
        while True:
            await asyncio.sleep(2)
            async with session.get(f"{SERVER_URL}/status/{job_id}") as resp:
                status_data = await resp.json()
                if status_data["status"] == "finished":
                    break
                if status_data["status"] == "failed":
                    raise RuntimeError(status_data.get("error"))

        # 3) скачиваем mp4
        async with session.get(f"{SERVER_URL}/result/{job_id}") as resp:
            if resp.status != 200:
                raise RuntimeError(f"Failed to download result: {resp.status}")
            filename = obj_path.split("/")[-1].split(".")[0]
            out_path = f"./Videos/{filename+'_'+job_id}.mp4"
            os.makedirs("./Videos", exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(await resp.read())
        return out_path

class Client(telethon.TelegramClient):
    def __init__(self, config: ConfigApi):
        self.config = config
        super().__init__('AeoUserBot', config.api_key, config.api_hash)

    async def _login(self):
        if not await self.is_user_authorized():
            await self.send_code_request(phone=self.config.phone)
            try:
                await self.sign_in(phone=self.config.phone, code=input('Enter the code: '))
            except telethon.errors.SessionPasswordNeededError:
                await self.sign_in(password=input('Enter your password: '))

    async def run(self):
        dprint("Bot is connecting...")
        await self.connect()

        dprint("Bot is logining...")
        # await self._login()
        await self.start(bot_token=self.config.bot_token)

        dprint("Bot is waiting for messages...")
        await self.run_until_disconnected()

        dprint("Bot is disconnecting...")
        await self.disconnect()

class Logic:
    def __init__(self):
        self.client = Client(ConfigApi('src/Config/credentials.json'))
        self.client.add_event_handler(self.model_message_handler)
        self.client.add_event_handler(self.button_handler)
        self.client.add_event_handler(self.inline_button_handler)

    async def run(self):
        await self.client.run()


    @events.register(events.NewMessage(incoming=True))
    async def model_message_handler(self, event: telethon.events.NewMessage.Event):
        who = event.message.peer_id
        file = event.message.media
        if file:
            file_name = list(filter(lambda att: isinstance(att, DocumentAttributeFilename), file.document.attributes))
            if file_name:
                file_name = file_name[0].file_name
            else:
                return
            get_extension(file_name)
            if not (file_name.endswith('.obj') or file_name.endswith('.stl')):
                return



            file_downloader = FileDownloaderFromMessage(self.client, event.message, file_name, 20, dprint)
            await file_downloader.init()
            full_file_name = await file_downloader.run()

            video_path = await render_via_server(full_file_name)
            await self.client.send_file(who, file=video_path)
        dprint(f"Received from '{who}',\n"
               f"Message: {event.raw_text}\n,"
               f"File: {file}")
    @events.register(events.NewMessage(incoming=True, pattern='^/start$'))
    async def message_handler(self, event: telethon.events.NewMessage.Event):
        who = event.message.peer_id
        file = event.message.media

        dprint(f"Received from '{who}',\n"
               f"Message: {event.raw_text}\n,"
               f"File: {file}")

        # await event.message.reply("Hello! I've accepted your message.")
        await self.client.send_message(who, message="Thanks for awaking the worst evil in the world! MUHAHAHA!")

        text_buttons = [
            [Button.text("Start Anon Chat", single_use=True)],
            [
                Button.text("Get Help", single_use=True),
                Button.text("Set Nickname", single_use=True)
            ]
        ]
        inline_buttons = [
            [Button.inline("Start Anon Chat")],
            [
                Button.inline("Get Help"),
                Button.inline("Set Nickname")
            ]
        ]
        await self.client.send_message(who, message="Choose an action (text buttons):", buttons=text_buttons)
        await self.client.send_message(who, message="Choose an action (inline buttons):", buttons=inline_buttons)

    @events.register(events.NewMessage(incoming=True, pattern='Start Anon Chat|Get Help|Set Nickname'))
    async def button_handler(self, event: telethon.events.NewMessage.Event):
        who = event.message.peer_id
        text = event.raw_text

        if text == "Start Anon Chat":
            await self.client.send_message(who, "Starting anonymous chat... Please wait for a match.")
        elif text == "Get Help":
            help_text = """Available commands:
            /start - Start the bot
            /help - Show this help message
            /stop - Stop current action"""
            await self.client.send_message(who, help_text)
        elif text == "Set Nickname":
            await self.client.send_message(who, "Please enter your desired nickname:")

    @events.register(events.CallbackQuery)
    async def inline_button_handler(self, event: telethon.events.CallbackQuery.Event):
        who = event.sender_id
        data = event.data.decode('utf-8')

        if data == "Start Anon Chat":
            await event.respond("Starting anonymous chat... Please wait for a match.")
        elif data == "Get Help":
            help_text = """Available commands:
            /start - Start the bot
            /help - Show this help message
            /stop - Stop current action"""
            await event.respond(help_text)
        elif data == "Set Nickname":
            await event.respond("Please enter your desired nickname:")
        await event.answer()

