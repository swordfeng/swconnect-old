
from telegram import *
from interface import ChannelGroup, Message
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
connectGroupCount = {}

def newConnectGroup(channel):
    global connectGroupId
    group = ChannelGroup(f'connect-{connectGroupId}')
    connectGroupId += 1
    group.addChannel(channel)
    connectChannels[channel.cid] = group.gid
    connectGroupCount[group.gid] = 1
    group.setMessageModifier(messageMod)
    return group
def joinConnectGroup(channel, gid):
    if not gid.startswith('connect-'):
        raise Exception('invalid group')
    group = ChannelGroup.getGroup(gid)
    if group == None:
        raise Exception('group not found')
    group.addChannel(channel)
    connectChannels[channel.cid] = group.gid
    connectGroupCount[group.gid] += 1
    return group
def leaveConnectGroup(channel):
    gid = connectChannels[channel.cid]
    group = ChannelGroup.getGroup(gid)
    group.removeChannel(channel)
    connectGroupCount[group.gid] -= 1
    if connectGroupCount[group.gid] == 0:
        del connectGroupCount[group.gid]

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
                rep.setText(str(connectChannels[message.channel.cid]))
            message.channel.sendMessage(rep)
        elif command == 'leavegroup':
            if message.channel.cid in connectChannels:
                leaveConnectGroup(channel)
                rep = Message(message.channel)
                rep.setText('success')
                message.channel.sendMessage(rep)
        elif command == 'newgroup':
            if message.channel.cid in connectChannels:
                leaveConnectGroup(channel)
            group = newConnectGroup(message.channel)
            rep = Message(message.channel)
            rep.setText(f'created {group.gid}')
            message.channel.sendMessage(rep)
        elif command.startswith('joingroup '):
            if message.channel.cid in connectChannels:
                leaveConnectGroup(channel)
            gid = command[10:].strip()
            try:
                group = joinConnectGroup(message.channel, gid)
                rep = Message(message.channel)
                rep.setText(f'joined {group.gid}')
                message.channel.sendMessage(rep)
            except BaseException:
                pass

async def main():
    session = aiohttp.ClientSession()
    telegramBot = TelegramBot(config.telegramToken, session)
    telegramBot.addHandler('connect', connectHandler)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.run_forever()
