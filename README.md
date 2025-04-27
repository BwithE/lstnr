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

**LSTNR** is a command line tool designed to manage multiple reverse shell sessions efficiently. It provides an interactive interface with session handling, and real-time command execution.

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP, HTB and THM labs. #Hobbies

# UPDATES
This script no longer needs `rlwrap` to keep the command history. Commmand logging is no longer active. Tab completion has been added to help with the menu, and session commands.

# Download LSTNR

```
git clone https://github.com/bwithe/LSNTR

cd lstnr
```

# USAGE

1. Start LSTNR
    - `python3 lstnr.py -p <PORT_TO_LISTEN>`
2. Have CLIENT connect to LSTNR
    - LSTNR comes with CLIENT scripts:
    - You will have to modify each of the scripts `IP` and `PORT` to connect to LSTNR
        - `client.py`
            - Linux and MacOS 
        - `client.ps1`
            - Windows 
        - `client.sh`
            - Linux 
        - `client.c`
            - Windows
            - NEEDS TO BE COMPILED
```
x86_64-w64-mingw32-gcc client.c -o client.exe -lws2_32 -Os -s
```

# Screenshot examples:

- Starting the listener `python3 lstnr.py -p <port>`

<img width="599" alt="Screenshot 2025-04-26 at 9 58 00 PM" src="https://github.com/user-attachments/assets/fb41ade5-7371-4c31-b058-5109fac1a742" />

- To get a list of commands, type `?` or `help`

<img width="779" alt="Screenshot 2025-04-26 at 9 58 21 PM" src="https://github.com/user-attachments/assets/e0709b8b-49cd-4e8b-9540-ce5de8287b46" />

- List any active sessions with `list`

<img width="1197" alt="Screenshot 2025-04-26 at 9 59 31 PM" src="https://github.com/user-attachments/assets/d2126ae7-cb0c-4e3c-80e5-b69684b792a4" />

- To connect to a session, `select <ID>`

<img width="431" alt="Screenshot 2025-04-26 at 10 00 25 PM" src="https://github.com/user-attachments/assets/9df666a9-f1d1-47cd-8868-05807aa5abb9" />

- Background a session with `background` or `CTRL+C`

<img width="467" alt="Screenshot 2025-04-26 at 10 00 48 PM" src="https://github.com/user-attachments/assets/20f23480-e164-48b5-8a0a-4e1da345eee3" />

- Kill an individual session `die`

<img width="937" alt="Screenshot 2025-04-26 at 10 01 37 PM" src="https://github.com/user-attachments/assets/7543c237-695b-4ed9-9bd9-01618aa759bc" />

- To kill all sessions, type `die` at the main menu `LSTNR>`

<img width="947" alt="Screenshot 2025-04-26 at 10 02 13 PM" src="https://github.com/user-attachments/assets/97044274-0935-49d9-badd-2125c5d6406a" />

- LSTNR WILL NOT CLOSE WITH `CTRL+C`

<img width="374" alt="Screenshot 2025-04-26 at 10 02 33 PM" src="https://github.com/user-attachments/assets/f7c1e764-46da-4486-adfe-f8b92b16bf5a" />

- To kill `LSTNR>` and all connections, type `exit`

<img width="552" alt="Screenshot 2025-04-26 at 10 02 44 PM" src="https://github.com/user-attachments/assets/cd88251e-061a-49ab-bedc-cbac1a1ff463" />


# TROUBLESHOOTING
- If a session hangs, background the session with `CTRL+C` and then reconnect.
- If commands stop working all together, reconnect to the session and run `die`, then re-run the reverse shell from the client machine.
- If you are having issues please feel free to reach out
