
import asyncio
import aiohttp
import json

loop = asyncio.get_event_loop()

class Message:
    def __init__(self, channel):
        self.channel = channel
        self.user = None
        self.text = None
        self.pic = None
    def setText(self, text):
        self.text = text
    def setUser(self, user):
        self.user = user

class User:
    def __init__(self):
        self.username = None
    def setUserName(self, username):
        self.username = username

class Channel:
    def __init__(self):
        self.handlers = {}
    def addHandler(self, name, callback):
        self.handlers[name] = callback
    def removeHandler(self, name):
        del self.handlers[name]
    def onMessage(self, message):
        for hname in self.handlers:
            self.handlers[hname](message)
    def sendMessage(self, message):
        raise NotImplementedError('should be overriden by subclass')

class ChannelGroup:
    def __init__(self, groupid):
        self.channels = set()
        self.groupid = groupid
    def addChannel(self, channel):
        self.channels.add(channel)
        channel.addHandler(f'channelgroup-{self.groupid}', self.onMessage)
    def removeChannel(self, channel):
        self.channels.remove(channel)
        channel.removeHandler(f'channelgroup-{self.groupid}')
    def onMessage(self, message):
        for channel in self.channels:
            if channel != message.channel:
                channel.sendMessage(message)

class Bot:
    pass

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

async def main():
    session = aiohttp.ClientSession()
    telegramBot = TelegramBot('378635461:AAE59IbHlf3u7va9r2e9xEi8sYdeuLk7NLI', session)

loop.run_until_complete(main())
loop.run_forever()
