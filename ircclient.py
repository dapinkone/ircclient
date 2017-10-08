#!/usr/bin/python
"""
Irc client implemented with python 3 + asyncio.
See TODO.org for TODOs, Readme.md for feature list and documentation

"""
# import os
import sys
import asyncio
import argparse
from concurrent.futures import ThreadPoolExecutor

from prompt_toolkit.interface import CommandLineInterface
# pep8 pls ;_;
from prompt_toolkit.shortcuts import create_prompt_application,\
    create_asyncio_eventloop

debugmode = False
loop = asyncio.get_event_loop()
loop.set_debug(debugmode)  # does this even do something?


class ircagent:
    def __init__(self, server, port, init_channel, nick, password=None):
        self.server       = server
        self.port         = port
        self.init_channel = init_channel
        self.nick         = nick
        self.password     = password

    async def startagent(self):
        # gui stuff to get the CLI prompt-toolkit started
        # is this a second eventloop? for prompt-toolkit?
        self.eventloop = create_asyncio_eventloop()

        self.cli = CommandLineInterface(
            application=create_prompt_application('Prompt: '),
            eventloop=self.eventloop)

        sys.stdout = self.cli.stdout_proxy()  # is this a good idea?

        # setting up the sockstream objects
        self.sockreader, self.sockwriter = await asyncio.open_connection(
            self.server, self.port, loop=loop)

        if self.sockreader:
            print("Socket connected.")

        # adding everything to the loop proper
        asyncio.ensure_future(self.interactive_shell())
        asyncio.ensure_future(self.socket_data_handler())

    async def interactive_shell(self):  # the gui thread?
        # jonothanslenders refers to `interactive_shell`? better solution?
        # credit to him @ python-prompt-toolkit for this part
        while True:
            try:
                result = await self.cli.run_async()  # it takes input! :D
                await self.encode_send(result.text)
            except (EOFError):
                break
            await asyncio.sleep(0)

    async def encode_send(self, msg):
        self.sockwriter.write(bytes(msg + "\r\n", "UTF-8"))
        if debugmode:
            print("> " + msg)

    # if these are always called within async main, so i need to pass loop?
    async def socket_data_handler(self):
        await self.encode_send("USER {} {} {} {}".format(*[self.nick] * 4))
        await self.encode_send("NICK {}".format(self.nick))
        await self.encode_send("JOIN {}".format(self.init_channel))
        await asyncio.sleep(0)

        while True:
            data = await self.sockreader.readline()
            msg = str(data, "UTF-8").strip()

            if 'PING' in msg[:4]:
                await self.encode_send("PONG{}".format(msg[4:]))
                continue  # nothing else to see here. move on.

            # auto-identify with nickserv
            if msg.startswith(':NickServ!NickServ@services. NOTICE'):
                if 'This nickname is registered' in msg:
                    if self.password:
                        # Prebuild our string. PEP8!
                        fmt_str = 'PRIVMSG NickServ :identify {} {}'

                        # Authenticate
                        await self.encode_send(
                            fmt_str.format(self.nick, self.password)
                        )

            if self.sockreader.at_eof():
                return

            if debugmode:
                print('<' + msg)
                # allows us to kill from socket side in case of gui issues
                if '!quit' in msg:
                    await self.encode_send('quit')
                    break
            else:  # not in debug mode; regular output.
                pieces = msg.split()
                action = pieces[1]  # (PRIVMSG|NOTICE|MODE|...)
                if action in "PRIVMSG NOTICE":
                    # :user!realname@host PRIVMSG target :messages of stuff
                    sender_nick   = pieces[0][1:].split('!')[0]
                    sender_target = pieces[2]
                    sender_msg    = ' '.join(pieces[3:])[1:]
                    print(f"{sender_target} <{sender_nick}> {sender_msg}")
                elif action in "JOIN PART":  # code duplication ;_;
                    sender_nick, sender_info = pieces[0][1:].split('!')
                    sender_target = pieces[2]
                    sender_msg = ' '.join(pieces[3:])[1:]

                    print(f"-!- {sender_nick} [{sender_info}]has " +
                          f"{action.lower()}ed {sender_target}", end="")
                    if action is "PART":
                        print(f"[{sender_msg}]", end="")
                    print("-!-")
                else:  # if i haven't written a rule for it yet, just print msg
                    print(msg)

            await asyncio.sleep(0)
        self.sockwriter.close()


async def report(loop):
    # this coroutine is going to monitor the tasks on the loop
    # and report the running tasks periodically
    # for debug purposes, and gracefully close the program
    # when that seems reasonable.
    while True:
        running_tasks = [t for t in asyncio.Task.all_tasks(loop=loop)
                         if not t.done()]
        if(len(running_tasks) == 1):  # we're solo? job's done.
            print("Job's done. Quiting.")
            # closing the loop at next "free" moment

            loop.stop()
            # we're done, so return to close the kill the coroutine
            return
        if debugmode:
            task_names = [k._coro.__name__ for k in running_tasks]
            print("REPORT:" + repr(task_names))
        await asyncio.sleep(3)


async def aioOpenFile(filename, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    with open(filename, 'rb') as data:
        io_pool = ThreadPoolExecutor()
        obj = await loop.run_in_executor(io_pool, data.read)
        return(obj)


async def main(loop):
    # do some commandline argument processing.
    # i feel this section is rather verbose, and may be due for a refactor.
    argparser = argparse.ArgumentParser(description='Connect to IRC.')
    argparser.add_argument("server", nargs='?',
                           help="The address of the server to connect to")
    # boolean flag for if debug mode is desired
    argparser.add_argument("--debug", help="Turn on debug mode",
                           action="store_true")
    argparser.add_argument("-p", "--port", help="specify port to be used",
                           type=int)
    argparser.add_argument("-c", "--chan", help="specify channels to join")
    argparser.add_argument("-n", "--nick", help="nick used on connection")
    argparser.add_argument("-a", "--auth", help="password for nickserv")

    try:
        authdata = await aioOpenFile('./authdata.txt', 'r')
    except FileNotFoundError:
        authdata = None

    # sensible defaults for if we provide no commandline arguments.
    argparser.set_defaults(
        server = 'Irc.Freenode.net',
        port   = 6667,
        chan   = '#nobodyhome',
        nick   = 'SimpleCli',
        auth   = authdata,
    )

    args = argparser.parse_args()

    if args.debug:
        global debugmode  # globals are bad form; how is this commonly done?
        debugmode = True
    # End of argument parsing.
    # start the ircagent/client object
    agent = ircagent(
        args.server, args.port, args.chan, args.nick, password=args.auth
    )
    await agent.startagent()

if __name__ == "__main__":
    asyncio.ensure_future(report(loop))
    asyncio.ensure_future(main(loop))
    loop.run_forever()
