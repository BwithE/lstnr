# LSTNR - Reverse Shell Session Manager

```
██╗     ███████╗████████╗███╗   ██╗██████╗ 
██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
███████╗███████║   ██║   ██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control
```

**LSTNR** is a command line tool designed to manage multiple reverse shell sessions efficiently. It provides an interactive interface with session handling, and real-time command execution.

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP, HTB and THM labs. #Hobbies

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
2. Generate Callbacks
```
LSTNR> payload 
payload> options 

Current Payload Options:

  LHOST     : 127.0.0.1
  LPORT     : 4444
  PAYLOAD   : py

payload> set lhost 127.0.0.1
[+] Set lhost to 127.0.0.1
payload> set lport 22
[+] Set lport to 22
payload> set payload sh
[+] Set payload to sh
payload> options 

Current Payload Options:

  LHOST     : 127.0.0.1
  LPORT     : 22
  PAYLOAD   : sh

payload> generate 
[+] Payload generated and saved as 127_0_0_1_22.sh
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
╔════╦═════════════════╦═════════════════╦═════════╦════════════════╦════════════╦════════╗
║ ID ║ IP              ║ HOSTNAME        ║ USER    ║ OS             ║ VERSION    ║ ARCH   ║
╠════╬═════════════════╬═════════════════╬═════════╬════════════════╬════════════╬════════╣
║ 1  ║ 192.168.193.131 ║ ubuntu          ║ clyde   ║ ubuntu         ║ 6.8.0      ║ x86_64 ║
║ 2  ║ 192.168.193.131 ║ ubuntu          ║ root    ║ ubuntu         ║ 6.8.0      ║ x86_64 ║
║ 3  ║ 192.168.193.129 ║ DESKTOP-P5KACDB ║ jimothy ║ Windows 10 Pro ║ 10.0.19045 ║ 64-bit ║
║ 4  ║ 192.168.193.129 ║ DESKTOP-P5KACDB ║ SYSTEM  ║ Windows 10 Pro ║ 10.0.19045 ║ 64-bit ║
╚════╩═════════════════╩═════════════════╩═════════╩════════════════╩════════════╩════════╝
```

To connect to a session, `select <ID>`
```
LSTNR> select 4
[*] Connected to session 4
SYSTEM@DESKTOP-P5KACDB> whoami
nt authority\system
```

Background a session with `background` or `CTRL+C`
```
SYSTEM@DESKTOP-P5KACDB> background 
[*] Backgrounding session.
LSTNR>
```

Kill an individual session `die`
```
clyde@ubuntu> die
[*] Sending 'die' to session 1
```

To kill all sessions, type `die` at the main menu `LSTNR>`
```
LSTNR> die
[*] Sending 'die' command to all clients!
```

LSTNR WILL NOT CLOSE WITH `CTRL+C`
```
LSTNR> 
Type 'exit' to stop LSTNR

LSTNR>
```

To kill `LSTNR>` and all connections, type `exit`
```
LSTNR> exit 
[*] Sending 'die' command to all clients!
[*] Exiting LSTNR.
```

# TROUBLESHOOTING
- If a session hangs, background the session with `CTRL+C` and then reconnect.
- If commands stop working all together, reconnect to the session and run `die`, then re-run the reverse shell from the client machine.
- If you are having issues please feel free to reach out
