# LSTNR – Reverse Shell Session Manager

**LSTNR** is a command-line tool designed to manage multiple reverse shell sessions efficiently. It provides an interactive interface with logging, session handling, and real-time command execution.

---
## Features

- Accepts multiple reverse shell connections
- Interactive shell per session
- Command history and colored output
- Background session handling
- Session listing and management
- Timestamped session logging

---
## Usage

### Start the Listener

```bash
python3 lstnr.py -p <port>
```

Replace `<port>` with the port number you want to listen on.

Example:
```bash
python3 lstnr.py -p 4444
```

---
## Commands

Once the listener is running, use these commands:

| Command      | Description                                |
|--------------|--------------------------------------------|
| `help` / `?` | Show available commands                    |
| `ls`         | List active sessions                      |
| `cs <id>`    | Connect to a specific session             |
| `bs`         | Background the current session            |
| `die`        | Terminate all sessions                    |
| `exit`       | Exit the current session or shutdown tool |

---
## Logs

Session logs are saved in the `logs-lstnr/` directory with a timestamped filename.

---
## Notes

- Make sure your reverse shells are configured to connect to the correct IP and port.
- This tool is for **educational or authorized testing** only. Do not use it on systems you don't own or have explicit permission to test.


