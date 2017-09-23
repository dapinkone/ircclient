Category Tags: General, GUI, Commands, Network, Files/

Planned Features/Bugs:
DONE: 1. connect to server, respond to ping so as not to timeout.
DONE: 2. take  input to be sent to the server
DONE: 5.1 converted to asyncio.

reasonable formatting for output of data from socket
- NETWORK  SSL/SASL support
- NETWORK  support for multiple server connections, /connect command or similar
- GENERAL  proper commandline argument parsing
- GENERAL  DOCUMENTATION PLS
- GENERAL  Tests? Surely I can write tests for this somehow?
- COMMANDS support for /join, /part, /quit like most IRC clients have
- GUI      addition of ncurse or similar gui, to graphically separate
           input and output(better option than prompt-toolkit?)
- GUI	   proper parsing of user input, rather than input->socket
- GUI	   status line - showing which channels are currently joined, nick, etc
- GUI	   window switching(a la irssi /show, /1, /2, etc)
- GUI	   vertical split, horizontal split, pane-based status bars
- GUI	   color code/hilight active pane or window?
- FILES	   /scripts/ dir for autoloading py extensions, ability to load/reload
  	   formatting/command data for faster development
- FILES	   authdata needs to be stored better, and read asyncronously
