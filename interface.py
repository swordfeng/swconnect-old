
import weakref

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
    channels = weakref.WeakValueDictionary()
    def getChannel(cid):
        if cid in Channel.channels:
            return Channel.channels[cid]
        return None
    def __init__(self, cid):
        self.handlers = {}
        self.cid = cid
        Channel.channels[cid] = self
    def addHandler(self, name, callback):
        self.handlers[name] = callback
    def removeHandler(self, name):
        del self.handlers[name]
    def onMessage(self, message):
        for hname in self.handlers:
            self.handlers[hname](message)
    def sendMessage(self, message):
        raise NotImplementedError('should be overriden by subclass')

class Bot(Channel):
    def __init__(self, bid):
        super().__init__(f'bot-{bid}')
        self.bid = bid
