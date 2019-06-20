"""
Todo:
* Make all the lists persistent in the DB.
* Get replies from DB
* Count user warnings cumulatively, 1 regular, 2 is the last Chinese warning, RO user
for a day on the last one, and ban if there was already a RO issued earlier.
* Watch user joins and set 5 minutes timer on when can they post links to websites,
emails, contacts and groups.
"""
import asyncio
import logging
import re
import socks

import uvloop

from datetime import datetime, timedelta

from telethon import TelegramClient, events
from telethon.tl.types import ChannelParticipantsAdmins

from loony.project import settings

# Configure logging just in case we may need it.
logging.basicConfig(level=logging.INFO)
logging.getLogger("asyncio").setLevel(logging.ERROR)


class Server:
    api_id = settings.API_ID
    api_hash = settings.API_HASH
    group_id = settings.GROUP_ID
    # Gets filled to accept commands only from administrators
    admins = {}
    # Grace period in seconds.
    grace_period = 150
    # Grace timeout in minutes
    grace_timeout = 20
    # Dict of watched users, user makes it here when they join the group, and gets out
    # if they send links after 5 minutes grace period, otherwise user gets permanently
    # banned as it will be considered to be a spam.
    # Format is {sender_id: expiration_datetime}
    now = datetime.now()
    watched = {9130251: now}
    print(watched)
    # Dict of users that have not write anything to the channel after joining.
    # {sender_id: [bool]is_first_message}
    shy = {}
    # List of users that has active warnings on them.
    # Format is {sender_id: warnings_left}
    warned = {}
    # Anti-spam regular expression, matches websites, e-mails, group and profile links.
    # E.g., https:/www.google.com/, @a_group, mailmespammer@spammail.com госуслуги.рф
    regexp = re.compile(r"([-\w\d:%._+~#=]*\.[\w\d]{2,6})|(@[\w\d_]*)")

    def __init__(self):
        # Set us a client.
        self.cl = TelegramClient(
            settings.container.new_session("default"),
            self.api_id,
            self.api_hash,
            proxy=(socks.SOCKS5, "127.0.0.1", 9050),
        )

    async def is_admin_speaking(self, sender_id):
        """
        Check if the user that inflicts a command is in administrators of the group.
        """
        return sender_id in self.admins and sender_id != settings.SELF_ID

    async def is_right_chat(self, chat_id):
        """
        Check if the chat is the one that we are administrating.
        """
        return chat_id == self.group_id

    async def is_spam_message(self, text):
        """
        Check if said text has any matches for regular expressions.

        If at least one, the result is true.
        """
        return re.search(self.regexp, text) is not None

    async def is_first_message(self, sender_id):
        """
        Check if user's message is the firs one after joining the channel.
        """
        return sender_id in self.shy

    async def is_watched(self, sender_id):
        """
        Check if user with sender_id is in watchlist and the timer is not ran out yet.

        If the user is in watchlist and the timer went out already, poop the user out of
        the watchlist and return False. Otherwise, return True.
        """
        print(sender_id)
        print(self.watched.get(sender_id, None))
        print(self.watched.get(sender_id, datetime.now() - timedelta(minutes=self.grace_timeout)))
        that = self.watched.get(sender_id, datetime.now() - timedelta(minutes=self.grace_timeout)) + timedelta(seconds=self.grace_period)
        print(that)
        print(that < datetime.now())
        cant_post_links_now = (self.watched.get(sender_id, datetime.now() - timedelta(minutes=self.grace_timeout)) + timedelta(seconds=self.grace_period)) < datetime.now()
        # if not cant_post_links_now:
        #     self.watched.pop(sender_id, None)
        return sender_id in self.watched and cant_post_links_now

    async def run(self):
        async with self.cl:
            # Show username we are logged in as.
            # The account needs to have a username set up.
            logging.info((await self.cl.get_me()).username)

            # Get all the groups we are a part of.
            groups = {
                g.id: g.entity
                for g in await self.cl.get_dialogs()
                if g.id == settings.GROUP_ID
            }
            # "Select" the group we want to administrate and do maintenance in.
            group = groups[settings.GROUP_ID]

            # Get admin list for the group. Can fail on large groups, use with care.
            async for admin in self.cl.iter_participants(
                group, filter=ChannelParticipantsAdmins
            ):
                self.admins[
                    admin.id
                ] = f"{str(admin.first_name)} {str(admin.last_name)}"

            @self.cl.on(events.NewMessage)
            async def message_handler(event):
                """
                Reply to o/ if mentioned or replied to.
                """
                logging.info(
                    f"event.mentioned: {event.mentioned}\n"
                    f"right chat: {await self.is_right_chat(event.chat_id)}\n"
                    f"admin speaking: {await self.is_admin_speaking(event.from_id)}\n"
                    f"is spam msg: {await self.is_spam_message(event.raw_text)}\n"
                    f"is being watched: {await self.is_watched(event.from_id)}\n"
                    f"is first message: {await self.is_first_message(event.from_id)}\n"
                    f"shy list: {self.shy}\n"
                    f"watch list: {self.watched}\n"
                    f"sender: {event.from_id}"
                )
                if (
                    await self.is_right_chat(event.chat_id)
                    # Excludes self, i.e. we don't want to react to our own commands.
                    and await self.is_admin_speaking(event.from_id)
                    # Notice that event.mentioned is True if the account was directly
                    # mentioned or replied to.
                    and event.mentioned is True
                    and "o/" in event.raw_text
                ):
                    await event.reply("\\o")
                elif (
                    await self.is_right_chat(event.chat_id)
                    and await self.is_admin_speaking(event.from_id)
                    # We don't want admins to give us warning by our own hands.
                    and not event.mentioned
                    # No non-reply warnings.
                    and event.is_reply
                    and "✨ warning" in event.raw_text
                ):
                    await self.cl.send_message(
                        entity=group,
                        message=f"✨ You have been warned!",
                        # This one is important:
                        # We want to warn a person that the message an administrator
                        # have replied to is the cause for the warning.
                        reply_to=await event.get_reply_message(),
                    )
                elif (
                    await self.is_right_chat(event.chat_id)
                    and await self.is_spam_message(event.raw_text)
                    and (
                        await self.is_first_message(event.from_id)
                        or await self.is_watched(event.from_id)
                    )
                ):
                    await event.reply("✨ Expellispamus!")

            @self.cl.on(events.ChatAction)
            async def action_handler(event):
                """
                Parse user joins and set a timer for them.
                """
                if (
                    await self.is_right_chat(event.chat_id)
                    and (event.user_joined or event.user_added)
                    and event.user_id not in self.admins
                ):
                    self.watched[event.user_id] = datetime.now()
                    self.shy[event.user_id] = True
                    logging.info(self.watched)
                elif await self.is_right_chat(event.chat_id) and (
                    event.user_kicked or event.user_left
                ):
                    self.watched.pop(event.user_id, None)
                    self.shy.pop(event.user_id, None)
                    logging.info(self.watched)

            await self.cl.run_until_disconnected()


uvloop.install()
server = Server()
loop = asyncio.get_event_loop()
loop.run_until_complete(server.run())
