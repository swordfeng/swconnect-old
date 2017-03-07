
from interface import *

class GroupChannel(Channel):
    def __init__(self, gid):
        super().__init__(f'group-{gid}')
        self.channels = set()
        #self.gid = gid
    def addChannel(self, channel):
        if channel not in self.channels:
            self.channels.add(channel)
            channel.addHandler(self.cid, self.onMessage)
    def removeChannel(self, channel):
        if channel in self.channels:
            self.channels.remove(channel)
            channel.removeHandler(self.cid)
    def sendMessage(self, message):
        for channel in self.channels:
            if channel != message.channel:
                channel.sendMessage(message)

class ConnectedChannel(GroupChannel):
    def __init__(self, gid):
        super().__init__(gid)
        self.modifier = lambda m: m
        self.addHandler('connect', self.sendModifiedMessage)
    def setMessageModifier(self, modifier):
        self.modifier = modifier
    def sendModifiedMessage(self, message):
        message = self.modifier(message)
        if message != None:
            self.sendMessage(message)
