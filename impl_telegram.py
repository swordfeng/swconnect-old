
import asyncio
import json
from interface import *
from util import printerr

class TelegramBot(Bot):
    def __init__(self, token, httpSession):
        super().__init__('telegram-{}'.format(token[:token.find(':')]))
        self.botid = int(token[:token.find(':')])
        self.session = httpSession
        self.channels = {}
        self.url = f'https://api.telegram.org/bot{token}/'
        self.updateId = 0 # must be read from config
        self.daemon = asyncio.Task(self.runDaemon())
        self.daemon.add_done_callback(lambda r: printerr(self.daemon.exception()))
    def sendChannelMessage(self, channel, message):
        asyncio.ensure_future(self.request('sendMessage', {
                'chat_id': channel.channelId,
                'text': message.text
            }))
    def getChannel(self, channelId):
        if channelId not in self.channels:
            self.channels[channelId] = TelegramChannel(self, channelId)
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
                if message == None:
                    continue
                if message.user != None and message.user.userId == self.botid:
                    continue # this message is sent by us
                self.onMessage(message)
                message.channel.onMessage(message)

class TelegramUser(User):
    def __init__(self, userId):
        super().__init__()
        self.userId = userId

class TelegramChannel(Channel):
    def __init__(self, bot, channelId):
        super().__init__(f'{bot.bid}-{channelId}')
        self.bot = bot
        self.channelId = channelId
    def sendMessage(self, message):
        self.bot.sendChannelMessage(self, message)
