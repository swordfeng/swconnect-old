
from impl_telegram import *
from impl_irc import *
from impl_xmpp import *
import asyncio
import aiohttp
from connect import connectHandler
import config

session = aiohttp.ClientSession()
telegramBot = TelegramBot(config.telegramToken, session)
telegramBot.addHandler('connect', connectHandler)

ircBot = IRCBot('chat.freenode.net', 7000, 'swconnect', password=config.ircPassword, channels=['#archlinux-cn-offtopic'])
ircBot.addHandler('connect', connectHandler)

xmppBot = XMPPBot('swconnect@xmpp.jp', config.xmppPassword)
xmppBot.addHandler('connect', connectHandler)

loop = asyncio.get_event_loop()
loop.run_forever()
