
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
        if channel not in self.channels:
            self.channels.add(channel)
            channel.addHandler(f'channelgroup-{self.groupid}', self.onMessage)
    def removeChannel(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)
            channel.removeHandler(f'channelgroup-{self.groupid}')
    def onMessage(self, message):
        for channel in self.channels:
            if channel != message.channel:
                channel.sendMessage(message)

class Bot:
    pass
