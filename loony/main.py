"""
Todo:
* Get replies from DB
* Only admins can manage and issue commands.
* React to commands (that starts with !|.|Luna, or direct replies to her messages)
* React to private chats
* Count user warnings cumulatively, 1 regular, 2 is the last Chinese warning, RO user for a day on the last one,
and ban if there was already a RO issued earlier.
"""
import asyncio
import logging

import socks
import uvloop

from telethon import TelegramClient, events

from loony.project import settings

logging.basicConfig(level=logging.INFO)
logging.getLogger('asyncio').setLevel(logging.ERROR)


async def main():
    api_id = settings.API_ID
    api_hash = settings.API_HASH

    async with TelegramClient("anonymous", api_id, api_hash, proxy=(socks.SOCKS5, '127.0.0.1', 9050)) as client:
        logging.info((await client.get_me()).username)
        message = await client.send_message('me', 'Hi!')
        await asyncio.sleep(5)
        await message.delete()
        # @client.on(events.NewMessage(pattern='(?i)hi|hello'))
        # async def handler(event):
        #     await event.reply('hey')
        await client.run_until_disconnected()


uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
