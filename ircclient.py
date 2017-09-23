#!/usr/bin/python
"""
Irc client implemented with python 3 + asyncio.

"""
import asyncio
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_prompt_application, create_asyncio_eventloop
# pep8 pls ;_;
import sys
# from termcolor import colored, cprint  # for pretty colors # ;_; broken?

debugmode = True

loop = asyncio.get_event_loop()
loop.set_debug(debugmode)  # does this even do something?

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

        print("Socket connected.\n{}".format(repr(self.sockreader)))

        # adding everything to the loop proper
        asyncio.ensure_future(self.interactive_shell())
        asyncio.ensure_future(self.socket_data_handler(loop))



    async def interactive_shell(self):  # the gui thread?
        # jonothanslenders refers to `interactive_shell`? better solution?
        # credit to him @ python-prompt-toolkit for this part
        asyncio.Task.current_task().name = 'SHELL'  # e.e
        while True:
            try:
                result = await self.cli.run_async()  # it takes input! :D
                await self.encode_send(result.text)
            except (EOFError):
                break
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
            print('<' + msg)
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

async def report(loop):
    # this coroutine is going to monitor the tasks on the loop
    # and report the running tasks periodically
    # for debug purposes, and so we can close gracefully
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

async def main(loop):
    agent = ircagent('irc.freenode.net', 6667, '#nobodyhome', 'simplecli')
    await agent.startagent()
asyncio.ensure_future(report(loop))
asyncio.ensure_future(main(loop))
loop.run_forever()
