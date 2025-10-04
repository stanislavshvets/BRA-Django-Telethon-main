import os
import re
from datetime import timedelta
from typing import *

from telethon import TelegramClient
from telethon.tl.custom import Message
from tzlocal import get_localzone

from Utils.DebugPrinter import DPrint
from Utils.Utils import create_model_path


def get_bare_filename(filename):
    split = re.split(r'[/.]', filename)
    split.pop()
    return split[-1]


def get_extension(filename):
    split = filename.split('.')
    return split.pop()


class FileDownloaderFromMessage:
    def __init__(self,
                 client: TelegramClient,
                 msg: Message,
                 filename: str,
                 day_border_local_hour: int,
                 dprint: DPrint,
                 download_callback: Callable[[int, int], Awaitable[None]] = None
                 ):
        self.client = client
        self.msg: Message = msg
        self.day_border_local_hour = day_border_local_hour
        self.dprint = DPrint('DOWNLOADER', base=dprint)
        self.download_callback = download_callback
        self.path_full = None
        self.filename = filename
        self.filename_full = None
        self.filename_full_stub = None
        self.stub_extension = '.stub'

    async def cache_full_filenames(self):
        if self.path_full is None:
            user_info = await self.msg.get_sender()
            self.path_full = os.path.abspath(create_model_path(self.msg.date.astimezone(get_localzone()),
                                                               user_info.username,
                                                               user_info.first_name,
                                                               user_info.last_name,
                                                               self.day_border_local_hour))
        self.filename_full = self.path_full + self.filename
        self.filename_full_stub = os.path.abspath(self.path_full + self.filename + self.stub_extension)

    def is_stub_fully_downloaded(self):
        try:
            return self.msg.file.size == os.path.getsize(self.filename_full_stub)
        except OSError:
            return False

    async def download_file_by_parts(self):
        if self.is_stub_fully_downloaded():
            return

        file = self.filename_full_stub
        received_bytes = 0
        total_bytes = self.msg.file.size

        try:
            received_bytes = os.path.getsize(file)
        except OSError:
            pass

        if os.path.exists(self.filename_full):
            return

        try:
            with open(file, 'ab') as file_parts:
                async for chunk in self.client.iter_download(self.msg.media, offset=received_bytes):
                    wrote = file_parts.write(chunk)
                    received_bytes += wrote
                    if self.download_callback is not None:
                        await self.download_callback(received_bytes, total_bytes)
        except Exception as e:
            self.dprint.error(f'An error occurred: {e}')
            raise

    def try_rename_completed_file(self):
        if not os.path.exists(self.filename_full_stub) or not self.is_stub_fully_downloaded():
            return

        rename_from = self.filename_full_stub
        rename_to = self.filename_full
        os.rename(rename_from, rename_to)

    async def init(self):
        await self.cache_full_filenames()

    async def run(self) -> str:
        if not os.path.exists(self.filename_full):
            await self.download_file_by_parts()
            self.try_rename_completed_file()
        else:
            self.dprint.rare(f'Already downloaded')

        return self.filename_full
