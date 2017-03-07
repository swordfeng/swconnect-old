
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

class ChannelGroup:
    groups = weakref.WeakValueDictionary()
    def getGroup(gid):
        if gid in ChannelGroup.groups:
            return ChannelGroup.groups[gid]
        return None
    def __init__(self, gid):
        self.channels = set()
        self.gid = gid
        ChannelGroup.groups[gid] = self
        self.modifier = lambda m: m
    def addChannel(self, channel):
        if channel not in self.channels:
            self.channels.add(channel)
            channel.addHandler(f'channelgroup-{self.gid}', self.onMessage)
    def removeChannel(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)
            channel.removeHandler(f'channelgroup-{self.gid}')
    def setMessageModifier(self, modifier):
        self.modifier = modifier
    def onMessage(self, message):
        message = self.modifier(message)
        if message == None:
            return
        for channel in self.channels:
            if channel != message.channel:
                channel.sendMessage(message)

class Bot:
    def __init__(self, bid):
        self.bid = bid
        self.handlers = {}
    def addHandler(self, name, handler):
        self.handlers[name] = handler
    def removeHandler(self, name):
        del self.handlers[name]
    def onMessage(self, message):
        for hname in self.handlers:
            self.handlers[hname](message)
    def sendMessage(self, channel, message):
        raise NotImplementedError('should be overriden by subclass')

