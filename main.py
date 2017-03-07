
from impl_telegram import *
from impl_irc import *
from impl_xmpp import *
from interface import Message
from group import ConnectedChannel
import asyncio
import aiohttp
import json

import config

def messageMod(message):
    if message.text != None and message.user != None and message.user.username != None:
        if message.text.startswith('swconnect:'):
            return None
        message.setText(f'[{message.user.username}] {message.text}')
    return message

connectChannels = {}
connectGroupId = 0

def newConnectGroup(channel):
    global connectGroupId
    group = ConnectedChannel(str(connectGroupId))
    connectGroupId += 1
    group.addChannel(channel)
    connectChannels[channel.cid] = group.cid
    group.setMessageModifier(messageMod)
    return group
def joinConnectGroup(channel, gcid):
    if not gcid.startswith('group-'):
        raise Exception('invalid group')
    group = Channel.getChannel(gcid)
    if group == None:
        raise Exception('group not found')
    group.addChannel(channel)
    connectChannels[channel.cid] = group.cid
    return group
def leaveConnectGroup(channel):
    gcid = connectChannels[channel.cid]
    group = Channel.getChannel(gcid)
    group.removeChannel(channel)

def connectHandler(message):
    if message.text == None:
        return
    prefix = 'swconnect:'
    if message.text.startswith(prefix):
        command = message.text[len(prefix):].strip()
        if command == 'channel':
            rep = Message(message.channel)
            rep.setText(message.channel.cid)
            message.channel.sendMessage(rep)
        elif command == 'group':
            rep = Message(message.channel)
            if message.channel.cid not in connectChannels:
                rep.setText('undefined')
            else:
                rep.setText(connectChannels[message.channel.cid])
            message.channel.sendMessage(rep)
        elif command == 'leavegroup':
            if message.channel.cid in connectChannels:
                leaveConnectGroup(message.channel)
                rep = Message(message.channel)
                rep.setText('success')
                message.channel.sendMessage(rep)
        elif command == 'newgroup':
            if message.channel.cid in connectChannels:
                leaveConnectGroup(message.channel)
            group = newConnectGroup(message.channel)
            rep = Message(message.channel)
            rep.setText(f'created {group.cid}')
            message.channel.sendMessage(rep)
        elif command.startswith('joingroup '):
            if message.channel.cid in connectChannels:
                leaveConnectGroup(message.channel)
            gcid = command[10:].strip()
            try:
                group = joinConnectGroup(message.channel, gcid)
                rep = Message(message.channel)
                rep.setText(f'joined {group.cid}')
                message.channel.sendMessage(rep)
            except BaseException:
                pass

session = aiohttp.ClientSession()
telegramBot = TelegramBot(config.telegramToken, session)
telegramBot.addHandler('connect', connectHandler)

ircBot = IRCBot('chat.freenode.net', 7000, 'swconnect', channels=['#archlinux-cn-offtopic'])
ircBot.addHandler('connect', connectHandler)

xmppBot = XMPPBot('swconnect@xmpp.jp', config.xmppPassword)
xmppBot.addHandler('connect', connectHandler)

loop = asyncio.get_event_loop()
loop.run_forever()
