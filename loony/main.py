import asyncio
import logging

# import re
import socks
import sys
import ujson

import aiohttp
import uvloop

from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChatBannedRights


from project import settings

# Configure logging just in case we may need it.
logging.basicConfig(level=logging.INFO)
logging.getLogger("asyncio").setLevel(logging.ERROR)


class Bot:
    def __init__(self):
        self.admins: dict = {}
        self.client: TelegramClient = TelegramClient(
            settings.session,
            settings.API_ID,
            settings.API_HASH,
            proxy=(socks.SOCKS5, settings.TOR_HOST, settings.TOR_PORT),
        )
        self.groups: dict = {}
        self.headers: dict = {}
        self.session = None
        self.token: str = ""
        self.friend_codes_channel = settings.FRIEND_CODES_CHANNEL

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
    #     Currently unused.
    #     """
    #     async with self.session.post(
    #         f"http://{settings.REST_HOST}:{settings.REST_PORT}/auth/logout/", json={}
    #     ) as response:
    #         return await response.json()

    async def nightwatch(self, uid, gid, message):
        async with self.session.post(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}/nightwatch/",
            data={"message": message, "uid": uid, "gid": gid},
            headers=self.headers,
        ) as response:
            return await response.json()

    async def warn_profile(self, uid, gid):
        async with self.session.put(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}"
            f"/profile/{uid}/{gid}/warning/",
            data={},
            headers=self.headers,
        ) as response:
            return await response.json()

    async def pardon_profile(self, uid, gid):
        async with self.session.put(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}"
            f"/profile/{uid}/{gid}/pardon/",
            data={},
            headers=self.headers,
        ) as response:
            return await response.json()

    async def create_profile(self, uid, gid):
        async with self.session.post(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}/profile/",
            data={"uid": uid, "gid": gid},
            headers=self.headers,
        ) as response:
            return await response.json()

    async def get_or_create_profile(self, uid, gid):
        async with self.session.get(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}/profile/{uid}/{gid}/",
            headers=self.headers,
        ) as response:
            return await response.json()

    async def destroy_profile(self, uid, gid):
        async with self.session.delete(
            f"http://{settings.REST_HOST}:{settings.REST_PORT}/profile/{uid}/{gid}/",
            headers=self.headers,
        ) as response:
            return await response.json()

    # async def get_amount(self, text):
    #     """
    #     Currently unused.
    #     """
    #     match = re.search(re.compile(r"[-+]?\d+\b"), text)
    #     if match is None:
    #         return 1
    #     return int(match.group())

    async def run_bot(self):
        async with self.client:
            # Show username we are logged in as.
            # The account needs to have a username set up.
            me = await self.client.get_me()
            logging.info(f"Username: {me.username}, ID: {me.id}")

            # Fill in admins
            async for group in self.client.iter_dialogs():
                if group.pinned:
                    logging.info(f"Pinned: {group.title} - {group.id}")
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
                await self.client.send_read_acknowledge(event.id)
                message = event.raw_text
                uid = event.sender_id
                gid = event.chat_id
                sender_is_admin = gid in self.admins.get(event.sender_id, [])
                sender_is_me = event.sender_id == me

                # Reply with \o to o/
                if (
                    sender_is_admin
                    and event.mentioned
                    and "o/" in message
                    and not sender_is_me
                ):
                    await event.reply("\\o")

                # Warn user whom admin is replying to with a message that
                # contains "✨ warn" in it with 1 if no digits in the message or only
                # positive digits in the message, -1 if negative digit in the message
                # (i.e. remove one level of warning)
                elif (
                    sender_is_admin
                    and "!warn" in message
                    and event.is_reply
                    and event.reply_to_msg_id != me.id
                ):
                    reply_to = await event.get_reply_message()
                    uid = reply_to.from_id
                    await self.get_or_create_profile(uid, gid)
                    result = await self.warn_profile(uid, gid)
                    threat = result.get("warnings")
                    own_message = await self.client.send_message(
                        entity=gid,
                        message=f"✨ Moneo! Your threat level is {threat} now. "
                        f"Please, behave.",
                        # This one is important:
                        # We want to warn a person that the message an administrator
                        # have replied to is the cause for the warning.
                        reply_to=reply_to,
                    )
                    # Delete the message
                    await event.delete()
                    # Wait for settings.CLEAR_MESSAGES_IN
                    await asyncio.sleep(settings.CLEAR_MESSAGES_IN)
                    # And delete own message too
                    await own_message.delete()

                # Pardon user whom admin is replying to with a message that
                # contains "✨ pardon" in it with 1 if no digits in the message or only
                # positive digits in the message, -1 if negative digit in the message
                # (i.e. remove one level of warning)
                elif (
                    sender_is_admin
                    and "!pardon" in message
                    and event.is_reply
                    and event.reply_to_msg_id != me.id
                ):
                    reply_to = await event.get_reply_message()
                    uid = reply_to.from_id
                    await self.get_or_create_profile(uid, gid)
                    result = await self.pardon_profile(uid, gid)
                    threat = result.get("warnings")
                    own_message = await self.client.send_message(
                        entity=gid,
                        message=f"✨ Ignosco! Your threat level is {threat} now.",
                        # This one is important:
                        # We want to warn a person that the message an administrator
                        # have replied to is the cause for the warning.
                        reply_to=reply_to,
                    )
                    # Delete the message
                    await event.delete()
                    # Wait for settings.CLEAR_MESSAGES_IN
                    await asyncio.sleep(settings.CLEAR_MESSAGES_IN)
                    # And delete own message too
                    await own_message.delete()

                # Ban user whom admin is replying to with a message that
                # contains "✨ ban" in it.
                elif (
                    sender_is_admin
                    and "!ban" in message
                    and event.is_reply
                    and event.reply_to_msg_id != me.id
                ):
                    reply_to = await event.get_reply_message()
                    uid = reply_to.from_id

                    own_message = await self.client.send_message(
                        entity=gid, message=f"✨ Exilium!", reply_to=reply_to
                    )
                    # Restrict user
                    await self.client(
                        EditBannedRequest(
                            gid,
                            uid,
                            ChatBannedRights(until_date=None, view_messages=True),
                        )
                    )
                    # Delete the message admin replied to
                    await reply_to.delete()
                    # And admin message too
                    await event.delete()
                    # Wait for settings.CLEAR_MESSAGES_IN
                    await asyncio.sleep(settings.CLEAR_MESSAGES_IN)
                    # And delete own message too
                    await own_message.delete()

                # Go check nightwatch for user with given text
                elif (
                    not sender_is_admin
                    and not sender_is_me
                    and gid != self.friend_codes_channel
                    and uid is not None
                ):
                    response = await self.nightwatch(uid, gid, message)
                    first_message = response.get("first_message", False)
                    is_malicious = response.get("is_malicious", False)
                    message_has_friend_codes = response.get("is_friend_code", False)
                    # FixMe: Currently unused
                    # user_has_n_warnings = response.get("warnings", 0)
                    grace_expired = (
                        float(response.get("grace_diff", 0)) > settings.GRACE
                    )

                    # User starts with spam in the group
                    # Spam determined like this:
                    # Any message that contains link and was written within
                    # settings.GRACE minutes *
                    # * of joining the group  -> Spam
                    # * of the first message (inclusive) -> Spam
                    if (
                        first_message
                        and is_malicious
                        or not grace_expired
                        and is_malicious
                    ):
                        own_message = await self.client.send_message(
                            entity=gid, message="✨ Exilispamus!"
                        )
                        # Restrict offender and delete all the messages from them
                        # Restrict user
                        await self.client(
                            EditBannedRequest(
                                gid,
                                uid,
                                ChatBannedRights(until_date=None, view_messages=True),
                            )
                        )
                        # Delete all the messages from this user.
                        for message in await self.client.get_messages(
                            gid, limit=10, from_user=uid
                        ):
                            await message.delete()
                        # Wait for settings.CLEAR_MESSAGES_IN
                        await asyncio.sleep(settings.CLEAR_MESSAGES_IN)
                        # And delete own message too
                        await own_message.delete()

                    # Relocate friend codes to friend codes channel
                    elif (
                        message_has_friend_codes
                        and gid != self.friend_codes_channel
                        and uid != me.id
                    ):
                        await event.forward_to(
                            entity=self.friend_codes_channel, silent=True
                        )
                        own_message = await event.reply(
                            message="✨ Ordina amicus! "
                            "Your code has been relocated to @HogwartsMainHall."
                        )
                        # Delete the message
                        await event.delete()
                        # Remove messages in settings.CLEAR_MESSAGES_IN seconds
                        await asyncio.sleep(settings.CLEAR_MESSAGES_IN)
                        # And delete own message too
                        await own_message.delete()

            @self.client.on(events.ChatAction)
            async def action_handler(event):
                # uid = event.user_id
                # gid = event.chat_id
                if event.user_joined:
                    logging.info("User joined")
                    # await self.create_profile(uid, gid)
                elif event.user_added:
                    logging.info("User was added")
                    # await self.create_profile(uid, gid)
                elif event.user_kicked:
                    logging.info("User was kicked")
                    await event.delete()
                    # await self.destroy_profile(uid, gid)
                elif event.user_left:
                    logging.info("User left")
                    # await self.destroy_profile(uid, gid)

            await self.client.run_until_disconnected()


uvloop.install()
loop = asyncio.get_event_loop()
bot = Bot()
loop.run_until_complete(bot.start())
