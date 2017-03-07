
from interface import *
import irc.client
import irc.connection
import ssl
import threading
import asyncio

class IRCBot(Bot):
    def __init__(self, server, port, nick, channels=[], enable_ssl=False, loop=asyncio.get_event_loop()):
        super().__init__(f'irc-{server}:{port}-{nick}')
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
        self.client.process_forever()
    def handler(self, connection, event):
        print('recv')
        self.loop.call_soon_threadsafe(self.onEvent, event)
    def onEvent(self, event):
        print(event)

bot = IRCBot('chat.freenode.net', 7000, 'swconnect', channels=['#archlinux-cn-offtopic'], enable_ssl=True)
loop = asyncio.get_event_loop()
loop.run_forever()
