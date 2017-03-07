
from telegram import *
from interface import ChannelGroup
import asyncio
import aiohttp
import json

import config

def messageMod(message):
    if message.text != None and message.user != None and message.user.username != None:
        message.setText(f'[{message.user.username}] {message.text}')
    return message

async def main():
    group = ChannelGroup('telegram')
    group.setMessageModifier(messageMod)
    session = aiohttp.ClientSession()
    telegramBot = TelegramBot(config.telegramToken, session)
    telegramBot.addHandler('joingroup', lambda message: group.addChannel(message.channel))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
