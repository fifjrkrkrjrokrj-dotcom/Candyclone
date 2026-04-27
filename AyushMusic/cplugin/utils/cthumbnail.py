import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from unidecode import unidecode
from py_yt import VideosSearch
from AyushMusic import app
from config import YOUTUBE_IMG_URL
from AyushMusic.utils.database import clonebotdb


def changeImageSize(maxWidth, maxHeight, image):
    ratio = max(maxWidth / image.size[0], maxHeight / image.size[1])
    return image.resize(
        (int(image.size[0] * ratio), int(image.size[1] * ratio)),
        Image.LANCZOS
    )


def clear(text):
    words = text.split(" ")
    title = ""
    for i in words:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


def get_random_fallback_img():
    if YOUTUBE_IMG_URL:
        if isinstance(YOUTUBE_IMG_URL, list):
            return random.choice(YOUTUBE_IMG_URL)
        return YOUTUBE_IMG_URL
    return "https://i.ibb.co/kVJsVLVg/file-4010.jpg"


async def get_thumb(videoid, user_id, client):
    # ---------- FIXED BRAND ----------
    bot_name = "MUSIC STREAM"

    try:
        me = await client.get_me()
        bot_id = me.id
    except:
        bot_id = 0

    # ---------- CACHE ----------
    filename = f"cache/{videoid}_{bot_id}.png"
    if os.path.isfile(filename):
        return filename

    # ---------- FETCH YOUTUBE DATA ----------
    url = f"https://www.youtube.com/watch?v={videoid}"

    try:
        results = VideosSearch(url, limit=1)
        data = (await results.next())["result"][0]

        try:
            title = re.sub(r"\W+", " ", data["title"]).title()
        except:
            title = "Unsupported Title"

        duration = data.get("duration", "Unknown")
        views = data.get("viewCount", {}).get("short", "Unknown Views")
        channel = data.get("channel", {}).get("name", "Unknown Channel")
        thumbnail = data["thumbnails"][0]["url"].split("?")[0]

        # ---------- DOWNLOAD ----------
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", "wb") as f:
                        await f.write(await resp.read())

        # ---------- IMAGE PROCESS ----------
        youtube = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")

        bg = changeImageSize(1280, 720, youtube)
        bg = bg.filter(ImageFilter.GaussianBlur(22))
        bg = ImageEnhance.Brightness(bg).enhance(0.40)

        draw = ImageDraw.Draw(bg)

        # ---------- NEON COLORS ----------
        neon_colors = [
            ("#ff004f", "#ff2f7d"),
            ("#ff00c8", "#ff4ddb"),
            ("#00ff99", "#4dffc3"),
            ("#00aaff", "#4dc3ff"),
            ("#ffd000", "#ffe066"),
        ]
        glow_color, border_color = random.choice(neon_colors)

        # ---------- CENTER THUMB ----------
        thumb_w, thumb_h = 840, 460
        yt_thumb = youtube.resize((thumb_w, thumb_h))

        mask = Image.new("L", (thumb_w, thumb_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, thumb_w, thumb_h), radius=25, fill=255
        )
        yt_thumb.putalpha(mask)

        x = (1280 - thumb_w) // 2
        y = 150

        # ---------- GLOW ----------
        glow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.rounded_rectangle(
            (x - 25, y - 25, x + thumb_w + 25, y + thumb_h + 25),
            radius=35,
            fill=glow_color,
        )
        glow = glow.filter(ImageFilter.GaussianBlur(35))
        bg.alpha_composite(glow)

        # ---------- BORDER ----------
        border = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(border)
        bdraw.rounded_rectangle(
            (x - 6, y - 6, x + thumb_w + 6, y + thumb_h + 6),
            radius=30,
            outline=border_color,
            width=6,
        )
        bg.alpha_composite(border)

        bg.paste(yt_thumb, (x, y), yt_thumb)

        # ---------- FONTS ----------
        try:
            title_font = ImageFont.truetype("AyushMusic/assets/font.ttf", 42)
            info_font = ImageFont.truetype("AyushMusic/assets/font2.ttf", 28)
            watermark_font = ImageFont.truetype("AyushMusic/assets/font2.ttf", 24)
        except:
            title_font = ImageFont.load_default()
            info_font = ImageFont.load_default()
            watermark_font = ImageFont.load_default()

        # ---------- TITLE ----------
        title_text = clear(title)
        title_w = draw.textlength(title_text, font=title_font)

        draw.text(
            (1280 - title_w - 40, 40),
            title_text,
            font=title_font,
            fill="white",
            stroke_width=2,
            stroke_fill=border_color,
        )

        # ---------- INFO ----------
        info_text = f"{channel} | {views} | {duration}"
        info_w = draw.textlength(info_text, font=info_font)

        draw.text(
            ((1280 - info_w) // 2, y + thumb_h + 40),
            info_text,
            font=info_font,
            fill=border_color,
        )

        # ---------- WATERMARK ----------
        draw.text(
            (30, 30),
            "MUSIC STREAM",
            font=watermark_font,
            fill=border_color,
        )

        draw.text(
            (30, 670),
            "MUSIC STREAM",
            font=watermark_font,
            fill="white",
        )

        # ---------- CLEANUP ----------
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        bg.save(filename)
        return filename

    except Exception as e:
        print(f"Thumb Error: {e}")
        return get_random_fallback_img()
