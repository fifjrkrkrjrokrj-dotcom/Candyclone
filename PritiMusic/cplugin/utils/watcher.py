from pyrogram import filters, Client
from pyrogram.types import Message

from AyushMusic import app
from AyushMusic.core.call import Aayu
# ✅ FIX: db import kiya taaki queue clear kar sakein
from AyushMusic.misc import db

welcome = 20
close = 30

@Client.on_message(filters.video_chat_started, group=welcome)
@Client.on_message(filters.video_chat_ended, group=close)
async def video_chat_events(_, message: Message):
    # Stream ko force stop karega
    await Aayu.stop_stream_force(message.chat.id)
    
    # ✅ FIX: Queue ko manually clear kar rahe hain taaki bot fresh start kare
    try:
        db[message.chat.id] = []
    except:
        pass