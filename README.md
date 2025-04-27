# LSTNR - Reverse Shell Session Manager

```
██╗     ███████╗████████╗███╗   ██╗██████╗ 
██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
███████╗███████║   ██║   ██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control - v0.7
    - MADE FOR REVERSE SHELL MANAGEMENT
```

**LSTNR** is a command line tool designed to manage multiple reverse shell sessions efficiently. It provides an interactive interface with logging, session handling, and real-time command execution.

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP, HTB and THM labs. #Hobbies

# UPDATES
This script no longer needs `rlwrap` to keep the command history. Commmand logging is no longer active. Tab completion has been added to help with menu, and session commands.

# Download LSTNR

```
git clone github.com/bwithe/LSNTR

cd lstnr
```

# USAGE

1. Start LSTNR
    - `python3 lstnr.py -p <PORT_TO_LISTEN>`
```
Menu commands:
    list          - List sessions
    select <id>   - Connect to a session by its ID
    die           - Terminate all sessions
    exit          - Terminate all sessions and exit LSTNR
Session commands:
    <any command> - Execute command on client
    background    - Return to main menu
    die           - Terminate current session
```
2. Have CLIENT connect to LSTNR
    - LSTNR comes with CLIENT scripts:
    - You will have to modify each script `IP` and `PORT` to connect to LSTNR
        - python3
        - powershell
        - sh 

# Screenshot examples:

- Starting the listener `python3 lstnr.py -p <port>`

- To get a list of commands, type `?` or `help`

- List any active sessions with `list`

- Background a session with `background` or `CTRL+C`

- Kill an individual session `die`

- To kill all sessions, type `die` at the main menu `LSTNR>`

- To kill `LSTNR>` and all connections, type `exit`

- LSTNR WILL NOT CLOSE WITH `CTRL+C`

# TROUBLESHOOTING
- If a session hangs, background the session with `CTRL+C` and then reconnect.
- If commands stop working all together, reconnect to the session and run `die`, then re-run the reverse shell from the client machine.
- If you are having issues please feel free to reach out
