#!/usr/bin/python
"""
Irc client. lets take it slow.
Planned milestones:
DONE: 1. connect to server, respond to ping so as not to timeout.
2. take input to be sent to the server
3. reasonable formatting for output of data from socket
4. SSL/SASL support
5. addition of ncurse or similar gui, to graphically separate input and output
   requires asyncio?
6. support for /join, /part, /quit like most IRC clients have
7. proper parsing of user input, rather than input->socket
8. status line - showing which channels are currently joined, nick, etc
9. window switching(/show #bots, switches to display #bots, hides other data,
   temporarily
10. vertical split, horizontal split, pane-based status bars
    (color code/hilight active pane?)
11. /load script.py, and /scripts/ directory for autoloading python extensions
12. think of more stuff to add.
"""
import asyncio # required for semi-simultaneous handling of io
import sys

async def wait_for_data(loop):
    server = "chat.freenode.net"
    init_channel = "#nobodyhome"
    username = "simplecli"
    port = 6667 # TODO add handling for cmdline args, handling of SASL port?
    authdata = open('./authdata.txt', 'r')
    password = authdata.readline()
    authdata.close()

    sockreader, sockwriter = await asyncio.open_connection(
        server, port, loop=loop)
    print("Socket connected.\n{}".format(repr(sockreader)))

    def encode_send(msg):
        sockwriter.write(bytes(msg + "\r\n", "UTF-8"))
        print("> " + msg)
    async def parse_input(msg):
        print(msg)
        if 'quit' in msg:
            encode_send('QUIT')
            quit()
    encode_send("USER {} {} {} {}".format(*[username]*4))
    encode_send("NICK {}".format(username))
    encode_send("JOIN {}".format(init_channel))

    while True:
        data = await sockreader.read(n=2048)
        msglist = str(data,"UTF-8").split('\r\n')
        for msg in msglist:
            print(msg)
            if 'PING' in msg[:4]:
                encode_send("PONG{}".format(msg[4:]))
            if ('NickServ@services'in msg)\
               and ('This nickname is registered' in msg):
                encode_send("privmsg nickserv :identify " +
                            username + " " + password)

            if '!quit' in msg:
                encode_send('quit')
                quit()
        await asyncio.sleep(0)
    sockwriter.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(wait_for_data(loop))
loop.close()
