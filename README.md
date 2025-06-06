# LSTNR - Reverse Shell Session Manager

```
██╗     ███████╗████████╗███╗   ██╗██████╗ 
██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
███████╗███████║   ██║   ██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
```

**LSTNR** is a command line tool designed to manage multiple reverse shell sessions efficiently. It provides an interactive interface with session handling, and real time command execution.

# DISCLAIMER
!! This is only for testing purposes, not intended for anything illegal.!!

 I was testing out ways to manage multiple connections while doing OFFSEC, HTB and THM labs. 

# Download LSTNR

```
git clone https://github.com/bwithe/LSNTR

cd lstnr
```

# USAGE

1. Start LSTNR
    - `python3 lstnr.py -p <PORT_TO_LISTEN>`
```
LSTNR> help 

Menu commands:
    list                - List sessions
    select <id>         - Connect to a session by its ID
    payload             - Payload generation menu
    kill <id>           - Terminate specific session
    exit                - Terminate all sessions and exit LSTNR
Session commands:
    <any command>       - Execute command on client
    background          - Return to main menu
    die                 - Terminate current session
Payload Menu Commands:
    set name <name>     - Custom name for reverse shell
    set lhost <ip>      - Set the LSTNR IP address
    set lport <port>    - Set the LSTNR listening port
    set payload <type>  - Set payload type (EX: py, sh, ps1, exe)
    options             - Show current payload configuration
    generate            - Generate the payload with current settings
    back                - Return to the main menu
    help                - Show this help menu

```
2. Generate Callbacks
```
LSTNR> payload 
payload> options 
╔═════════╦═══════════╗
║ Setting ║ Value     ║
╠═════════╬═══════════╣
║ name    ║ Default   ║
║ lhost   ║ 127.0.0.1 ║
║ lport   ║ 80        ║
║ payload ║ sh        ║
╚═════════╩═══════════╝
payload> set name payload
[*] Set name to 'payload'
payload> set lhost 192.168.0.1
[*] Set lhost to '192.168.0.1'
payload> set lport 21
[*] Set lport to '21'
payload> set payload exe
[*] Set payload to 'exe'
payload> options 
╔═════════╦═════════════╗
║ Setting ║ Value       ║
╠═════════╬═════════════╣
║ name    ║ payload     ║
║ lhost   ║ 192.168.0.1 ║
║ lport   ║ 21          ║
║ payload ║ exe         ║
╚═════════╩═════════════╝
payload> generate 
[+] Payload generated: payload.cs
[+] EXE payload compiled successfully as 'payload.exe'
```

3. Execute callbacks on the client to establish a connection to LSTNR

# USAGE EXAMPLES:

Starting the listener 
```
python3 lstnr.py -p <port>
```

To get a list of commands, type `?` or `help`
```
LSTNR> help 

Menu commands:
    list                - List sessions
    select <id>         - Connect to a session by its ID
    payload             - Payload generation menu
    die                 - Terminate all sessions
    exit                - Terminate all sessions and exit LSTNR
Session commands:
    <any command>       - Execute command on client
    background          - Return to main menu
    die                 - Terminate current session
Payload Menu Commands:
    set lhost <ip>      - Set the LSTNR IP address
    set lport <port>    - Set the LSTNR listening port
    set payload <type>  - Set payload type (EX: py, sh, ps1)
    options             - Show current payload configuration
    generate            - Generate the payload with current settings
    back                - Return to the main menu
    help                - Show this help menu

```

List any active sessions with `list`
```
LSTNR> list 
╔════╦═════════════════╦═════════════════╦═════════╗
║ ID ║ IP              ║ HOSTNAME        ║ USER    ║
╠════╬═════════════════╬═════════════════╬═════════╣
║ 1  ║ 192.168.193.131 ║ ubuntu          ║ clyde   ║
║ 2  ║ 192.168.193.131 ║ ubuntu          ║ root    ║
║ 3  ║ 192.168.193.129 ║ DESKTOP-P5KACDB ║ jimothy ║
║ 4  ║ 192.168.193.129 ║ DESKTOP-P5KACDB ║ SYSTEM  ║ 
╚════╩═════════════════╩═════════════════╩═════════╝
```

To connect to a session, `select <ID>`
```
LSTNR> select 4
[*] Connected to session 4
```

Background a session with `background` or `CTRL+C`
```
background 
[*] Backgrounding session.
LSTNR>
```

Kill an individual session `die`
```
die
[*] Sending 'die' to session 1
```

To kill individual sessions
```
LSTNR> kill 1
[*] Client 1 terminated.
```

LSTNR WILL NOT CLOSE WITH `CTRL+C`
```
LSTNR> 
[*] Use 'background' to leave a session.

[*] Use 'exit' to shut down the LSTNR cleanly.
```

To kill `LSTNR>` and all connections, type `exit`
```
LSTNR> exit 
```

# TROUBLESHOOTING
- If a session hangs, press 'CTRL+C' then type 'background'. Reconnect to the session.
- If commands stop working all together, reconnect to the session and run `die`, then re-run the reverse shell from the client machine.
