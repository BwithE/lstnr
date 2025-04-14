# LSTNR – Reverse Shell Session Manager

**LSTNR** is a command-line tool designed to manage multiple reverse shell sessions efficiently. It provides an interactive interface with logging, session handling, and real-time command execution.

<img width="560" alt="Screenshot 2025-04-13 at 9 25 47 PM" src="https://github.com/user-attachments/assets/8fbbebab-dc2a-4e11-b9f1-ce5081e421bb" />

---
# DISCLAIMER
Not intended for anything illegal. I started working on LSTNR while going through the OSCP labs, and it's since been fun using in HTB and THM labs.

---
# Menu Usage
- Type `help` to see a list of commands

<img width="841" alt="Screenshot 2025-04-13 at 9 26 11 PM" src="https://github.com/user-attachments/assets/9b05d1dd-0bac-4f58-bba9-1dc54b67c485" />

- Building reverse shells for powershell and bash

<img width="937" alt="Screenshot 2025-04-13 at 9 27 01 PM" src="https://github.com/user-attachments/assets/76996eee-dc55-4012-94c3-27aaa00a54b7" />

- After you've transfered and executed the payloads, list active sessions with `ls`

<img width="932" alt="Screenshot 2025-04-13 at 9 30 17 PM" src="https://github.com/user-attachments/assets/96a9133f-6a2d-489a-8a21-7ee6b0d35c3f" />

- To connect to a session, run `cs <ID>`
- To update the sessions table, run `whoami` and `hostname` within the shell $ before upgrading
  - It's best to run `whoami` and `hostname` in the first $shell you get before upgrading, it causes wonkiness when upgraded. 
- To background a session, use `CTRL+C` or `bs` 

<img width="939" alt="Screenshot 2025-04-13 at 9 31 05 PM" src="https://github.com/user-attachments/assets/9934929d-e470-4e10-8ac2-5f115f78c0bc" />

- To upgrade the `bash` shell, run `stable`
- From there, if you can elevate, do so
- To build a new shell if you obtain a new user, just run `payload linux`
- Then type `exit` until you get back to the shell you want

<img width="624" alt="Screenshot 2025-04-13 at 9 32 35 PM" src="https://github.com/user-attachments/assets/9059519f-8008-487c-9049-d5b20d898179" />

- Once you've compromised `root, system, or *admin*` accounts, they will be highlighted in red

<img width="772" alt="Screenshot 2025-04-13 at 9 34 14 PM" src="https://github.com/user-attachments/assets/d64abb88-017e-4cf4-9187-675fa216688c" />

- To kill sessions, type `die` within the individual session
- To kill all sessions, type `die` at the main `LSTNR` menu
- To kill all sessions and exit `LSTNR`, you must type `exit`
  - `CTRL+C` will not close `LSTNR`
 
<img width="293" alt="Screenshot 2025-04-13 at 9 34 29 PM" src="https://github.com/user-attachments/assets/94a4c7d2-5a47-491c-b179-ed6d2e1e0c94" />

---
# TROUBLESHOOTING
1. In linux, to update the sessions table, i recommend running `whoami` and `hostname` before upgrading to a TTY shell.
2. You may have issues running `whoami` and `hostname`. If the shell stops responding right after, DON'T PANIC! Just background the session and reconnect. This is an issue im working on.



