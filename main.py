import math
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('TG_BOT_TOKEN')
string_session = os.getenv('PSTRING_SESSION')
MAINCHANNEL_ID = os.getenv('MAINCHANNEL_ID').split(',')


bot = Client(
    "bot_session",
    api_id=api_id, api_hash=api_hash, bot_token=bot_token
)

BUTTONS = {}


@bot.on_message(filters.command('find'))
async def search(_, message):
    print("funciona")
    if not (query := message.text.removeprefix("/find").strip()):
        return

    btn = []

    async with Client("client_session", api_id=api_id, api_hash=api_hash, session_string=string_session) as client:
        for id in MAINCHANNEL_ID:
            async for msg in client.search_messages(int(id), query=query):
        	    name = ""
        	    if msg.document: name = msg.document.file_name
        	    elif msg.media: name = msg.caption
        	    else: name = msg.text
        	    btn.append(
         	    [InlineKeyboardButton(text=f"{name}", url=f"{msg.link}")]
          	)

    if not btn:
        return

    if len(btn) < 10:
        btn.append(
            [InlineKeyboardButton(text="📃 Pages 1/1", callback_data="pages")]
        )
        await message.reply_text(
            f"<b> Here is the result for {query}</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return

    ident = f"{message.chat.id}-{message.id}"

    global BUTTONS
    BUTTONS[ident] = {
        "total": len(btn),
        "buttons": btn
    }

    first = btn[0:10]
    first.append(
        [InlineKeyboardButton(text="NEXT ⏩", callback_data=f"pagination_{ident}_next_0")]
    )
    first.append(
        [InlineKeyboardButton(text=f"📃 Pages 1/{math.ceil(len(btn)/10)}", callback_data="pages")]
    )
    await message.reply_text(
        f"<b> Here is the result for {query}</b>",
        reply_markup=InlineKeyboardMarkup(first)
    )


@bot.on_callback_query(filters.regex('pagination_.+'))
async def answer(client, callback_query):
    _, ident, keyword, page = callback_query.data.split("_")
    total = BUTTONS[ident]['total']
    await callback_query.answer()

    page_to_go = int(page)

    if keyword == 'next':
        page_to_go += 1
    if keyword == 'back':
        page_to_go -= 1

    current_index = page_to_go * 10

    data = BUTTONS[ident]['buttons'][current_index:current_index + 10]

    buttons = data
    if page_to_go != 0:
        buttons.append(
            [InlineKeyboardButton(text="⏪ BACK", callback_data=f"pagination_{ident}_back_{page_to_go}")]
        )
    if page_to_go*10+10 < total:
        buttons.append(
            [InlineKeyboardButton(text="NEXT ⏩", callback_data=f"pagination_{ident}_next_{page_to_go}")]
        )

    buttons.append(
        [InlineKeyboardButton(f"📃 Pages {page_to_go+1}/{math.ceil(total/10)}", callback_data="pages")]
    )

    await callback_query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


bot.run()
