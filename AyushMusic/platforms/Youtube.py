import os
import aiohttp
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist
import aiohttp

DOWNLOAD_DIR = "downloads"

API_URL = os.environ.get("SHRUTI_API_URL", "https://api.shrutibots.site")
API_KEY = os.environ.get("SHRUTI_API_KEY", "ShrutiBotsBj3bsZPzdxPMfjFvnRxg")


def extract_video_id(link: str) -> str:
    try:
        if "youtube.com/watch?v=" in link:
            return link.split("v=")[1].split("&")[0]

        elif "youtu.be/" in link:
            return link.split("youtu.be/")[1].split("?")[0]

        return link.strip()

    except Exception:
        return None


class YouTubeAPI:
    def __init__(self):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # ---------------- AUDIO DOWNLOAD ----------------
    async def download_song(self, link: str) -> Union[str, None]:
        video_id = extract_video_id(link)

        if not video_id:
            return None

        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_URL}/download",
                    params={
                        "url": video_id,
                        "type": "audio",
                        "api_key": API_KEY,
                    },
                    timeout=aiohttp.ClientTimeout(total=300),
                ) as resp:

                    if resp.status != 200:
                        print("Audio API failed:", await resp.text())
                        return None

                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(131072):
                            f.write(chunk)

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return file_path

            return None

        except Exception as e:
            print("Audio error:", e)
            return None

    # ---------------- VIDEO DOWNLOAD ----------------
    async def download_video(self, link: str) -> Union[str, None]:
        video_id = extract_video_id(link)

        if not video_id:
            return None

        file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{API_URL}/download",
                    params={
                        "url": video_id,
                        "type": "video",
                        "api_key": API_KEY,
                    },
                    timeout=aiohttp.ClientTimeout(total=600),
                ) as resp:

                    if resp.status != 200:
                        print("Video API failed:", await resp.text())
                        return None

                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(131072):
                            f.write(chunk)

            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                return file_path

            return None

        except Exception as e:
            print("Video error:", e)
            return None

    # ---------------- SAFE WRAPPER ----------------
    async def get_audio(self, link: str):
        return await self.download_song(link)

    async def get_video(self, link: str):
        return await self.download_video(link)


# INSTANCE (IMPORTANT FOR IMPORT)
YouTube = YouTubeAPI()
