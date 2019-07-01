"""
Todo:
* Watch user joins and set 5 minutes timer on when can they post links to websites,
emails, contacts and groups.
"""
import asyncio
import logging
import re
import socks
import sys
import ujson

import aiohttp
import uvloop

from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins

from project import settings

# Configure logging just in case we may need it.
logging.basicConfig(level=logging.INFO)
logging.getLogger("asyncio").setLevel(logging.ERROR)


# async def main():
#     async with aiohttp.ClientSession() as session:
#         html = await nigthwatch(session, "http://python.org")
#         print(html)


class Bot:
    def __init__(self):
        self.admins = {}
        self.client = None
        self.groups = {}
        self.headers = {}
        self.session = None
        self.token = ""

    async def start(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(settings.REQUESTS_TIMEOUT)
        )
        # Log into django (then proceed) or tell if django is down (then quit).
        async with self.session:
            response = await self.login()
            try:
                key = response["key"]
                self.token = key
                logging.info(f"Logged in into Django, got token: {key}")
                self.headers["Authorization"] = f"token {key}"
            except ValueError:
                logging.fatal("Django is unavailable or invalid credentials provided")
                sys.exit(1)

            self.client = TelegramClient(
                settings.session,
                settings.API_ID,
                settings.API_HASH,
                proxy=(socks.SOCKS5, settings.TOR_HOST, settings.TOR_PORT),
            )

            await bot.run_bot()

    async def login(self):
        async with self.session.post(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}/auth/login/",
            json={
                "username": settings.DJANGO_USER,
                "email": settings.DJANGO_EMAIL,
                "password": settings.DJANGO_PASSWORD,
            },
        ) as response:
            return await response.json()

    # async def logout(self):
    #     """
    #     Currently not used.
    #     """
    #     async with self.session.post(
    #         f"http://{settings.REST_HOST}:{settings.REST_PORT}/auth/logout/", json={}
    #     ) as response:
    #         return await response.json()

    async def nightwatch(self, message, uid, gid):
        async with self.session.post(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}/nightwatch/",
            data={"message": message, "uid": uid, "gid": gid},
            headers=self.headers,
        ) as response:
            return await response.json()

    async def warn_profile(self, uid, gid, amount):
        async with self.session.put(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}"
            f"/profile/{uid}/{gid}/warning/",
            data={"warning": int(amount)},
            headers=self.headers,
        ) as response:
            return await response.json()

    async def get_profile(self, uid, gid):
        async with self.session.get(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}/profile/{uid}/{gid}",
            headers=self.headers
        ) as response:
            return await response.json()

    async def run_bot(self):
        async with self.client:
            # Show username we are logged in as.
            # The account needs to have a username set up.
            me = await self.client.get_me()
            logging.info(f"Username: {me.username}, ID: {me.id}")

            # Fill in admins
            async for group in self.client.iter_dialogs():
                if group.pinned:
                    async for admin in self.client.iter_participants(
                        group, filter=ChannelParticipantsAdmins
                    ):
                        if self.admins.get(admin.id) is None:
                            self.admins[admin.id] = [group.id]
                        else:
                            self.admins[admin.id].append(group.id)

            logging.info("Got administrators for pinned groups")

            @self.client.on(events.NewMessage)
            async def message_handler(event):
                message = event.raw_text
                uid = event.sender_id
                gid = event.chat_id
                chat_entity = await event.get_chat()
                logging.info(event)
                sender_is_admin = gid in self.admins.get(event.sender_id, [])
                sender_is_me = event.sender_id == me

                # Reply with \o to o/
                if (
                    sender_is_admin
                    and event.mentioned
                    and "o/" in event.raw_text
                    and not sender_is_me
                ):
                    await event.reply("\\o")

                # Warn user whom admin is replying to with a message that
                # contains "✨ warn" in it with 1 if no digits in the message or only
                # positive digits in the message, -1 if negative digit in the message
                # (i.e. remove one level of warning)
                elif (
                    sender_is_admin
                    and "✨ warn" in event.raw_text
                    and event.is_reply
                    and event.reply_to_msg_id != me.id
                ):
                    amount = await self.get_warn_amount(event.raw_text)
                    reply_to = await event.get_reply_message()
                    uid = reply_to.from_id
                    profile = await self.get_profile(uid, gid)
                    threat = profile.get("warnings")

                    await self.warn_profile(uid, gid, amount)
                    await self.client.send_message(
                        entity=gid,
                        message=f"✨ Your threat level changed, it's {threat} now",
                        # This one is important:
                        # We want to warn a person that the message an administrator
                        # have replied to is the cause for the warning.
                        reply_to=await event.get_reply_message(),
                    )

                # Go check nightwatch for user with given text
                elif not sender_is_admin and not sender_is_me:
                    response = await self.nightwatch(message, uid, gid)
                    first_message = response.get("first_message", False)
                    is_malicious = response.get("is_malicious", False)
                    message_has_friend_codes = response.get("is_friend_code", False)
                    user_has_n_warnings = response.get("warnings", 0)
                    grace_expired = (
                        float(response.get("grace_diff", 0)) < settings.GRACE
                    )

                    # User starts with spam in the group
                    # Spam determined like this:
                    # Any message that contains link and was written within 5 minutes *
                    # * of joining the group  -> Spam
                    # * of the first message (inclusive) -> Spam
                    if (
                        first_message
                        and is_malicious
                        or not grace_expired
                        and is_malicious
                    ):
                        await self.client.send_message(
                            entity=gid,
                            message="✨ Explellispamus! (You should get banned!)",
                        )

            @self.client.on(events.ChatAction)
            async def action_handler(event):
                pass

            await self.client.run_until_disconnected()

    async def get_warn_amount(self, text):
        digit = re.search(re.compile(r"[-+]?\d+"), text)
        if digit is None:
            return 1
        else:
            return 1 if int(digit.group()) >= 0 else -1


uvloop.install()
loop = asyncio.get_event_loop()
bot = Bot()
loop.run_until_complete(bot.start())
