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
import logging
from termcolor import colored, cprint  # for pretty colors.


loop = asyncio.get_event_loop()
loop.set_debug(True)

# the only non-async stuff in the whole program. #FIXME ?
authdata = open('./authdata.txt', 'r')
password = authdata.readline()
authdata.close()


async def main(loop):
    server = "chat.freenode.net"
    init_channel = "#nobodyhome"
    username = "simplecli"
    port = 6667  # TODO add handling for cmdline args, handling of SASL port?

    # is this a second eventloop? for prompt-toolkit?
    eventloop = create_asyncio_eventloop()

    cli = CommandLineInterface(
        application=create_prompt_application('Prompt: '),
        eventloop=eventloop)

    sys.stdout = cli.stdout_proxy()  # is this a good idea?

    sockreader, sockwriter = await asyncio.open_connection(
        server, port, loop=loop)
    print("Socket connected.\n{}".format(repr(sockreader)))

    async def interactive_shell():  # the gui thread?
        # jonothanslenders refers to `interactive_shell`? better solution?
        # credit to him @ python-prompt-toolkit for this part
        cprint("INPUT SHELL STARTED", "red")
        asyncio.Task.current_task().name = 'SHELL'  # e.e
        while True:
            # a bit hard to decipher, but this tests to see
            # if socket_data_handler's task(task 0) has run it's course
            if tasks[0].done():
                break
            try:
                result = await cli.run_async()  # it takes input! :D
                if result is not None:  # if user enters '', do nothin
                    await encode_send(result.text)

            except (EOFError, KeyboardInterrupt):
                return
            for x in asyncio.Task.all_tasks(loop=loop):
                try:
                    print(x.name)
                except:
                    pass

            await asyncio.sleep(0)

    async def encode_send(msg):
        sockwriter.write(bytes(msg + "\r\n", "UTF-8"))
        print("> " + msg)

    async def socket_data_handler(loop):
        await encode_send("USER {} {} {} {}".format(*[username] * 4))
        await encode_send("NICK {}".format(username))
        await encode_send("JOIN {}".format(init_channel))
        await asyncio.sleep(0)

        while True:
            data = await sockreader.readline()
            msg = str(data, "UTF-8").strip()
            print('>' + msg)
            if 'PING' in msg[:4]:
                await encode_send("PONG{}".format(msg[4:]))
            if ('NickServ@services'in msg)\
               and ('This nickname is registered' in msg):
                await encode_send("privmsg nickserv :identify " +
                                  username + " " + password)
            if sockreader.at_eof():
                return

            if '!quit' in msg:
                await encode_send('quit')
                break
            await asyncio.sleep(0)
        sockwriter.close()

    tasks = [
        asyncio.ensure_future(socket_data_handler(loop)),
        asyncio.ensure_future(interactive_shell())
    ]

asyncio.ensure_future(main(loop))
loop.run_forever()
