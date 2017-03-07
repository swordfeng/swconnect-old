
Requirements
===
aiohttp, aiodns for http clients (telegram bot api)  
irc for irc  
sleekxmpp, dnspython, pyasn1 for xmpp  

Implementation Note
===
Client protocol should inherit Bot, Channel, User classes defined in interface.py.  
All ids are like `{protocol}-{bot_identifier}-{channel_identifier}`  
Call `onMessage` on `Bot` and `Channel` when receive message, override `sendMessage` on them  
The `onMessage` should be called on the main thread, use `loop.call_soon_threadsafe` if multithreaded  
Tell me if you have anything uncertain  
