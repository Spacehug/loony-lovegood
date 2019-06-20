"""
Todo:
* 
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

api_id = settings.API_ID
api_hash = settings.API_HASH
# Gets filled to accept commands only from administrators
admins = {}
# Grace period in seconds.
grace_period = 150
# Grace timeout in minutes
grace_timeout = 20
# List of watched users, user makes it here when they join the group, and gets out if
# they send links after 5 minutes grace period, otherwise user gets permanently banned
# as it will be considered to be a spam.
# Format is {sender_id: expiration_datetime}
watched = {}
# List of
# Format is {sender_id: warnings_left}
warned = {}
# Anti-spam regular expression, matches websites, e-mails, group and profile links.
# E.g., https:/www.google.com/, @a_group, mailmespammer@spammail.com госуслуги.рф
regexp = re.compile(r"([-\w\d:%._+~#=]*\.[\w\d]{2,6})|(@[\w\d_]*)")


def is_admin_speaking(sender_id):
    """
    Check if the user that inflicts a command is in administrators of the group.
    """
    return sender_id in admins and sender_id != settings.SELF_ID


def is_right_chat(chat_id):
    """
    Check if the chat is the one that we are administrating.
    """
    return chat_id == settings.GROUP_ID


def is_spam_message(text):
    """
    Check if said text has any matches for regular expressions.

    If at least one, the result is true.
    """
    return re.search(regexp, text) is not None


def is_watched(sender_id):
    """
    Check if the user with sender_id ID is in watchlist and the timer is not yet out.

    If the user is in watchlist and the timer went out already, poop the user out of
    the watchlist and return False.
    Otherwise, return True.
    """
    cant_post_links_now = (
        watched.get(sender_id, datetime.now() - timedelta(minutes=grace_timeout))
        + timedelta(seconds=grace_period)
        <= datetime.now()
    )
    if not cant_post_links_now:
        watched.pop(sender_id, None)
    return sender_id in watched and cant_post_links_now


async def main():
    # Set us a client.
    cl = TelegramClient(
        settings.container.new_session("default"),
        api_id,
        api_hash,
        proxy=(socks.SOCKS5, "127.0.0.1", 9050),
    )
    async with cl:
        # Show username we are logged as. The account needs to have a username set up.
        logging.info((await cl.get_me()).username)

        # Get all the groups we are a part of.
        groups = {
            g.id: g.entity for g in await cl.get_dialogs() if g.id == settings.GROUP_ID
        }
        # "Select" the group we want to administrate and do maintenance in.
        group = groups[settings.GROUP_ID]

        # Get admin list for the group. Can fail on large groups, use with care.
        async for admin in cl.iter_participants(
            group, filter=ChannelParticipantsAdmins
        ):
            admins[admin.id] = f"{str(admin.first_name)} {str(admin.last_name)}"

        @cl.on(events.NewMessage)
        async def message_handler(event):
            """
            Reply to o/ if mentioned or replied to.
            """
            global warned
            if (
                is_right_chat(event.chat_id)
                # Excludes self, i.e. we don't want to react to our own commands.
                and is_admin_speaking(event.from_id)
                # Notice that event.mentioned is True if the account was directly
                # mentioned or replied to.
                and event.mentioned is True
                and "o/" in event.raw_text
            ):
                await event.reply("\\o")
            elif (
                is_right_chat(event.chat_id)
                and is_admin_speaking(event.from_id)
                # We don't want admins to give us warning by our own hands.
                and not event.mentioned
                # No non-reply warnings.
                and event.is_reply
                and "✨ warning" in event.raw_text
            ):
                await cl.send_message(
                    entity=group,
                    message=f"✨ You have been warned!",
                    # This one is important: we want to warn a person that the message
                    # an administrator have replied to is the cause for the warning.
                    reply_to=await event.get_reply_message(),
                )
            elif (
                is_right_chat(event.chat_id)
                and is_spam_message(event.raw_text)
                and is_watched(event.from_id)
            ):
                await event.reply("Expellispamus!")

        @cl.on(events.ChatAction)
        async def chat_action_handler(event):
            """
            Parse user joins and set a timer for them.
            """
            global watched
            if (
                is_right_chat(event.chat_id)
                and (event.user_joined or event.user_added)
                and event.user_id not in admins
            ):
                watched[event.user_id] = datetime.now()
            elif is_right_chat(event.chat_id) and (
                event.user_kicked or event.user_left
            ):
                watched.pop(event.user_id, None)

        await cl.run_until_disconnected()


uvloop.install()
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
