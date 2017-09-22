#!/usr/bin/python
"""
Irc client. lets take it slow.
Planned milestones:
DONE: 1. connect to server, respond to ping so as not to timeout.
DONE: 2. take  input to be sent to the server
3. reasonable formatting for output of data from socket
4. SSL/SASL support
5. addition of ncurse or similar gui, to graphically separate input and output
DONE: 5.1 converted to asyncio.
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
import asyncio
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_asyncio_eventloop
# pep8 pls ;_;
import sys
# from termcolor import colored, cprint  # for pretty colors # ;_; broken?

loop = asyncio.get_event_loop()
loop.set_debug(True) # does this even do something?

# the only non-async stuff in the whole program. #FIXME ?
authdata = open('./authdata.txt', 'r')
password = authdata.readline()
authdata.close()


class ircagent:
    def __init__(self, server, port, init_channel, username):
        self.server = server
        self.init_channel = init_channel
        self.username = username
        self.port = port

    # is this a second eventloop? for prompt-toolkit?
    eventloop = create_asyncio_eventloop()

    cli = CommandLineInterface(
        application=create_prompt_application('Prompt: '),
        eventloop=eventloop)

    sys.stdout = cli.stdout_proxy()  # is this a good idea?

    async def startagent(self):
        self.sockreader, self.sockwriter = await asyncio.open_connection(
            self.server, self.port, loop=loop)
        print("Socket connected.\n{}".format(repr(self.sockreader)))
        asyncio.ensure_future(self.interactive_shell())
        asyncio.ensure_future(self.socket_data_handler(loop))

    async def interactive_shell(self):  # the gui thread?
        # jonothanslenders refers to `interactive_shell`? better solution?
        # credit to him @ python-prompt-toolkit for this part
        asyncio.Task.current_task().name = 'SHELL'  # e.e
        while True:
            try:
                result = await self.cli.run_async()  # it takes input! :D
                if result is not None:  # if user enters '', do nothin
                    await self.encode_send(result.text)

            except (EOFError, KeyboardInterrupt):
                return
            for x in asyncio.Task.all_tasks(loop=loop):
                try:
                    # This is neat, and possibly a sin? use later.
                    pass  # print(x.name)
                except:
                    pass

            await asyncio.sleep(0)

    async def encode_send(self, msg):
        self.sockwriter.write(bytes(msg + "\r\n", "UTF-8"))
        print("> " + msg)

    async def socket_data_handler(self, loop):
        await self.encode_send("USER {} {} {} {}".format(*[self.username] * 4))
        await self.encode_send("NICK {}".format(self.username))
        await self.encode_send("JOIN {}".format(self.init_channel))
        await asyncio.sleep(0)

        while True:
            data = await self.sockreader.readline()
            msg = str(data, "UTF-8").strip()
            print('>' + msg)
            if 'PING' in msg[:4]:
                await self.encode_send("PONG{}".format(msg[4:]))
            if ('NickServ@services'in msg)\
               and ('This nickname is registered' in msg):
                await self.encode_send("privmsg nickserv :identify " +
                                       self.username + " " + password)
                # TODO ^^ fix password/authdata to be async and in-class
            if self.sockreader.at_eof():
                return

            if '!quit' in msg:
                await self.encode_send('quit')
                break
            await asyncio.sleep(0)
        self.sockwriter.close()


async def main(loop):
    agent = ircagent('irc.freenode.net', 6667, '#nobodyhome', 'simplecli')
    await agent.startagent()

asyncio.ensure_future(main(loop))
loop.run_forever()
