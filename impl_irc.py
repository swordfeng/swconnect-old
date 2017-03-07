
from interface import *
import irc.client
import irc.connection
import ssl
import threading
import asyncio
from util import printerr

class IRCBot(Bot):
    def __init__(self, server, port, nick, channels=[], enable_ssl=True, loop=asyncio.get_event_loop()):
        super().__init__(f'irc-{server}:{port}-{nick}')
        self.channels = {}
        self.client = irc.client.Reactor()
        self.server = self.client.server()
        if enable_ssl:
            self.server.connect(server, port, nick, connect_factory=irc.connection.Factory(wrapper=ssl.wrap_socket))
        else:
            self.server.connect(server, port, nick)
        self.client.add_global_handler('pubmsg', self.handler)
        self.client.add_global_handler('privmsg', self.handler)
        for ch in channels:
            self.server.join(ch)
        self.loop = loop
        self.thread = threading.Thread(target=self.runThread)
        self.thread.start()
    def runThread(self):
        try:
            self.client.process_forever()
        except e:
            printerr(e)
    def handler(self, connection, event):
        self.loop.call_soon_threadsafe(self.onEvent, event)
    def getChannel(self, chatname):
        channel = Channel.getChannel(f'{self.bid}-{chatname}')
        if channel == None:
            channel = IRCChannel(self, chatname)
        return channel
    def makeMessage(self, event):
        user = IRCUser(event.source)
        if event.type == 'pubmsg':
            channel = self.getChannel(event.target)
        else:
            channel = self.getChannel(event.source)
        message = Message(channel)
        message.setText(event.arguments[0])
        message.setUser(user)
        return message
    def onEvent(self, event):
        message = self.makeMessage(event)
        if message != None:
            self.onMessage(message)
            message.channel.onMessage(message)
    def sendMessage(self, channel, message):
        # if channel.chatname.startswith('#'):
        if message.text != None:
            self.server.privmsg(channel.chatname, message.text)

class IRCUser(User):
    def __init__(self, name):
        super().__init__()
        self.setUserName(name[:name.find('!')])
        self.target = name

class IRCChannel(Channel):
    def __init__(self, bot, chatname):
        super().__init__(f'{bot.bid}-{chatname}')
        self.bot = bot
        self.chatname = chatname
    def sendMessage(self, message):
        self.bot.sendMessage(self, message)
