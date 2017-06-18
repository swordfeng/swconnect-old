
from impl_telegram import *
from impl_irc import *
from impl_xmpp import *
import asyncio
from connect import connectHandler
import config
import signal

telegramBot = TelegramBot(config.telegramToken)
telegramBot.addHandler('connect', connectHandler)


ircBot = IRCBot('chat.freenode.net', 7000, 'swconnect', password=config.ircPassword, channels=['#archlinux-cn-offtopic'])
ircBot.addHandler('connect', connectHandler)

xmppBot = XMPPBot('swconnect@xmpp.jp', config.xmppPassword)
xmppBot.addHandler('connect', connectHandler)

loop = asyncio.get_event_loop()

def exitHandler(signum, frame):
    telegramBot.stop()
    xmppBot.stop()
    ircBot.stop()
    loop.stop()

signal.signal(signal.SIGINT, exitHandler)

print('ready, now run the loop')
loop.run_forever()

print('exit')
