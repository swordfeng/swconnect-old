
import asyncio
import json
from interface import *

class TelegramBot(Bot):
    def __init__(self, token, httpSession):
        self.session = httpSession
        self.channels = {}
        self.handlers = {}
        self.url = f'https://api.telegram.org/bot{token}/'
        self.updateId = 0 # must be read from config
        #self.channelGroup = ChannelGroup('telegram') # test
        self.daemon = asyncio.Task(self.runDaemon())
        self.daemon.add_done_callback(lambda r: print(self.daemon.exception()))
    def getChannel(self, channelId):
        if channelId not in self.channels:
            self.channels[channelId] = TelegramChannel(self, channelId)
            #self.channelGroup.addChannel(self.channels[channelId]) # test
        return self.channels[channelId]
    def makeMessage(self, update):
        if 'message' in update:
            m = update['message']
            channel = self.getChannel(m['chat']['id'])
            message = Message(channel)
            if 'from' in m:
                u = m['from']
                user = TelegramUser(u['id'])
                user.setUserName(u['first_name'])
                message.setUser(user)
            if 'text' in m:
                message.setText(m['text'])
            if 'photo' in m:
                pass
            return message
        return None
    def addHandler(self, name, handler):
        self.handlers[name] = handler
    def removeHandler(self, name):
        del self.handlers[name]
    def sendMessage(self, channel, message):
        asyncio.ensure_future(self.request('sendMessage', {
                'chat_id': channel.channelId,
                'text': message.text
            }))
    def onMessage(self, message):
        for hname in self.handlers:
            self.handlers[hname](message)
    async def request(self, method, params={}):
        async with self.session.post(self.url + method,
                                     data=json.dumps(params),
                                     headers={'content-type': 'application/json'}
                                    ) as resp:
            return await resp.json()
    async def runDaemon(self):
        while True:
            updates = await self.request('getUpdates', {'offset': self.updateId, 'timeout': 15})
            for update in updates['result']:
                if update['update_id'] >= self.updateId:
                    self.updateId = update['update_id'] + 1
                message = self.makeMessage(update)
                if message != None:
                    self.onMessage(message)
                    message.channel.onMessage(message)

class TelegramUser(User):
    def __init__(self, userId):
        super().__init__()
        self.userId = userId

class TelegramChannel(Channel):
    def __init__(self, bot, channelId):
        super().__init__()
        self.bot = bot
        self.channelId = channelId
    def sendMessage(self, message):
        self.bot.sendMessage(self, message)
