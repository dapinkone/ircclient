#!/usr/bin/python
"""
Irc client. lets take it slow.
Planned milestones:
1. connect to server, respond to ping so as not to timeout.
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
import socket # there may be a more fully featured irc module. #research
ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "chat.freenode.net"
init_channel = "#nobodyhome"
username = "simpleclient"
port = 6667 # TODO add handling for cmdline args, handling of SASL port?

def encode_send(msg):
    ircsock.send(bytes(msg, "UTF-8"))

ircsock.connect((server, port))
# TODO: write generalized function for ircsock.send("...\n")
encode_send("USER {} {} {} {}\n".format(*[username]*4))
encode_send("NICK {}\n".format(username))

def join_channel(chan):
    encode_send("JOIN {}\n".format(chan))

join_channel(init_channel)
def pong():
    encode_send("PONG :words\n")
    print("PONG")

def privmsg(msg, target=init_channel):
    encode_send("PRIVMSG {} :{}\n".format(target, msg))

while True: #mainloop
    incoming_msg = str(ircsock.recv(2048), "UTF-8")
    msglist = incoming_msg.split('\n\r')
    for msg in msglist:
        msg.strip()
        if not msg: # if it's an empty line, move on.
            continue
        if 'PING' in msg: # should be more specific
            pong()
        print(msg)
