# LSTNR
Python script that receives reverse shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI).

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
    - `ls` : lists connected clients
    - `cs <ID>` : connects to that session
    - `exit` : will terminate all sessions and stop the script
- SESSION COMMANDS
    - `CTRL+C` or `bs` : backgrounds the active session
    - `exit` or `die` : while in a session will terminate it

2. Have CLIENT connect to LSTNR
    - You can use any of the methods found on https://www.revshells.com
        - Windows: `Powershell #3 (Base64)`
        - Linux: `Bash -i`
        - MacOS: `python3`

# Screenshot examples:

- Starting the listener

<img width="546" alt="Screenshot 2025-03-01 at 9 10 31 PM" src="https://github.com/user-attachments/assets/9c82b662-63dd-4902-8dfd-8df2580c6e5a" />

- Press any key to get a list of commands

<img width="727" alt="Screenshot 2025-03-01 at 9 10 50 PM" src="https://github.com/user-attachments/assets/8cc03545-8282-4bbc-8ac3-c59c23b4a273" />

- List any active sessions

<img width="337" alt="Screenshot 2025-03-01 at 9 10 41 PM" src="https://github.com/user-attachments/assets/aeb6c1ee-34c7-4261-b070-55e42f9e7855" />

- When a session is established

<img width="818" alt="Screenshot 2025-03-01 at 9 12 06 PM" src="https://github.com/user-attachments/assets/98584501-4b73-4c79-9dad-fc06193625ab" />

- Connecting to a session

<img width="610" alt="Screenshot 2025-03-01 at 9 12 18 PM" src="https://github.com/user-attachments/assets/db85499a-2322-49d2-846f-0eac1c68d904" />

- Running a command

<img width="365" alt="Screenshot 2025-03-01 at 9 14 21 PM" src="https://github.com/user-attachments/assets/54bc1a94-6d3e-4bc9-b5dd-88d54fa9d54c" />

- Background a session with `bs`

<img width="386" alt="Screenshot 2025-03-01 at 9 13 11 PM" src="https://github.com/user-attachments/assets/2dc51949-cee1-454c-9db7-ad147579f800" />

- Background a session with `CTRL+C`

<img width="397" alt="Screenshot 2025-03-01 at 9 12 54 PM" src="https://github.com/user-attachments/assets/eb14dbfd-cd2f-4b86-ad16-b4fcd3d84bc6" />

- Once you've received other connections, `ls` will always verify

<img width="813" alt="Screenshot 2025-03-01 at 9 13 44 PM" src="https://github.com/user-attachments/assets/72777f84-5597-4211-ad29-a43689594ff2" />

- Example of a Windows machine connected

<img width="712" alt="Screenshot 2025-03-01 at 9 17 08 PM" src="https://github.com/user-attachments/assets/7fa0601d-7cf3-410f-b6ec-308509788fe0" />

- To kill all sessions, type `exit` at the main menu `lstnr$`

<img width="269" alt="Screenshot 2025-03-01 at 9 17 29 PM" src="https://github.com/user-attachments/assets/0fcd92b1-c16b-43f6-80c7-cfb19ac42e7b" />

# RECOMMENDED TIPS
- If you plan on running a command with a long exepected output, such as a `linPEAS.sh` or `winPEAS.exe`; run them in the background and write to a file, and pull the file.
    - This helps if you are also having issues

# TROUBLESHOOTING
- If a shell hangs, background the session with `CTRL+C` and then reconnect.
    - If commands stop working, re-run the reverse shell.
- If you are having issues please feel free to reach out
