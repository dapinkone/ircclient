#!/usr/bin/python
"""
Irc client. lets take it slow.
Planned milestones:
1. connect to server, respond to ping so as not to timeout.
2. take input to be sent to the server
3. reasonable formatting for output of data from socket
4. SSL/SASL support
5. addition of ncurse or similar gui, to graphically separate input and output
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
ircsock = socket.socket(socket.AF_I_Inet, socket.SOCK_STREAM)
server = "chat.freenode.net"
channel = "#nobodyhome"
username = "simpleclient"
port = 6667 #TODO add handling for cmdline args, handling of SASL port

ircsock.connect((server, port))
# TODO: write generalized function for ircsock.send("...\n")
ircsock.send("USER {} {} {} {}\n".format(*[username]*4))
ircsock.send("NICK {}\n".format(username))
