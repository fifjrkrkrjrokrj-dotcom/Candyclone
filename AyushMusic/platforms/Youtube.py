import asyncio
import os
import re
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
import aiohttp

API_URL = os.environ.get(
    "SHRUTI_API_URL",
    "https://api.shrutibots.site"
)

API_KEY = os.environ.get(
    "SHRUTI_API_KEY",
    "ShrutiBotsBj3bsZPzdxPMfjFvnRxg"
)

DOWNLOAD_DIR = "downloads"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


def extract_video_id(link: str) -> str:
    try:
        # normal youtube link
        if "youtube.com/watch?v=" in link:
            return link.split("v=")[1].split("&")[0]

        # short youtube link
        elif "youtu.be/" in link:
            return link.split("youtu.be/")[1].split("?")[0]

        # already video id
        return link.strip()

    except Exception:
        return None


async def download_song(link: str) -> str:
    video_id = extract_video_id(link)

    print("AUDIO VIDEO ID =", video_id)

    if not video_id or len(video_id) < 3:
        print("INVALID VIDEO ID")
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp3"
    )

    # cached file
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        print("USING CACHED AUDIO")
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/download",
                params={
                    "url": video_id,
                    "type": "audio",
                    "api_key": API_KEY
                },
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:

                print("AUDIO API STATUS =", resp.status)

                if resp.status != 200:
                    text = await resp.text()
                    print("AUDIO API ERROR =", text[:500])
                    return None

                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print("AUDIO DOWNLOAD SUCCESS =", file_path)
            return file_path

        print("AUDIO FILE EMPTY")
        return None

    except Exception as e:
        print("AUDIO DOWNLOAD EXCEPTION =", e)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        return None


async def download_video(link: str) -> str:
    video_id = extract_video_id(link)

    print("VIDEO VIDEO ID =", video_id)

    if not video_id or len(video_id) < 3:
        print("INVALID VIDEO ID")
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    file_path = os.path.join(
        DOWNLOAD_DIR,
        f"{video_id}.mp4"
    )

    # cached file
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        print("USING CACHED VIDEO")
        return file_path

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_URL}/download",
                params={
                    "url": video_id,
                    "type": "video",
                    "api_key": API_KEY
                },
                timeout=aiohttp.ClientTimeout(total=600)
            ) as resp:

                print("VIDEO API STATUS =", resp.status)

                if resp.status != 200:
                    text = await resp.text()
                    print("VIDEO API ERROR =", text[:500])
                    return None

                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(131072):
                        f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print("VIDEO DOWNLOAD SUCCESS =", file_path)
            return file_path

        print("VIDEO FILE EMPTY")
        return None

    except Exception as e:
        print("VIDEO DOWNLOAD EXCEPTION =", e)

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

        return None
