
from telegram import *
from interface import ChannelGroup
import asyncio
import aiohttp
import json

async def main():
    group = ChannelGroup('telegram')
    session = aiohttp.ClientSession()
    telegramBot = TelegramBot('378635461:AAE59IbHlf3u7va9r2e9xEi8sYdeuLk7NLI', session)
    telegramBot.addHandler('joingroup', lambda message: group.addChannel(message.channel))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
