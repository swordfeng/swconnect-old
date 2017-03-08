
from interface import *
import sleekxmpp
import asyncio
from util import printerr

class XMPPBot(Bot):
    def __init__(self, jid, password, loop=asyncio.get_event_loop()):
        super().__init__(f'xmpp-{jid}')
        self.channels = {}
        self.jid = jid
        self.loop = loop
        self.client = sleekxmpp.ClientXMPP(jid, password)
        self.client.register_plugin('xep_0030') # Service Discovery
        self.client.register_plugin('xep_0045') # Multi-User Chat
        self.client.register_plugin('xep_0199') # XMPP Ping
        self.client.add_event_handler("session_start", self.onSessionStart)
        self.client.add_event_handler("message", self.onEventMessage)
        if not self.client.connect():
            raise Exception('XMPP connect error')
        self.client.process()

    def getChannel(self, chattype, chatfrom):
        cid = f'xmpp-{self.jid}-{chattype}-{chatfrom}'
        channel = Channel.getChannel(cid)
        if channel == None:
            channel = XMPPChannel(self, chattype, chatfrom)
        return channel

    def onSessionStart(self, event):
        self.client.send_presence()
        self.client.get_roster()

    def sendChannelMessage(self, channel, message):
        self.client.send_message(mto=channel.chatfrom, mtype=channel.chattype, mbody=message.text)

    def onEventMessage(self, msg):
        if msg['type'] == 'chat':
            channel = self.getChannel('chat', str(msg['from']))
            message = Message(channel)
            message.setText(msg['body'])
            message.setUser(XMPPUser(msg['from']))
            self.loop.call_soon_threadsafe(self.onMessage, message)
            self.loop.call_soon_threadsafe(message.channel.onMessage, message)

class XMPPChannel(Channel):
    def __init__(self, bot, chattype, chatfrom):
        super().__init__(f'xmpp-{bot.jid}-{chattype}-{chatfrom}')
        self.bot = bot
        self.chattype = chattype
        self.chatfrom = chatfrom
    def sendMessage(self, message):
        self.bot.sendChannelMessage(self, message)

class XMPPUser(User):
    def __init__(self, chatfrom):
        super().__init__()
        self.setUserName(chatfrom.user)
