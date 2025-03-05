import select
import socket
import threading
import sys
import queue
import time
import os

# ANSI escape codes for colors
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
BLUE = "\033[94m"  # Blue for LSTNR$
ORANGE = "\033[38;5;214m"  # Orange for Session prompt

HOST = "0.0.0.0"
PORT = None  # Port will be set from command-line arguments

sessions = {}
session_id = 0
lock = threading.Lock()

notifications = queue.Queue()  # Queue to store new session messages

# Log file path with timestamp
LOG_FILE = f"{time.strftime('%Y-%m-%d_%H-%M-%S')}-sessions.log"

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

def print_commands():
    """Prints a formal list of available commands."""
    message = "\n[+] List of commands:\n"
    message += "   help | ?  - List this menu\n"
    message += "   ls        - List active sessions\n"
    message += "   cs <id>   - Connect to a specific session by ID\n"
    message += "   bs        - Background the current session\n"
    message += "   exit      - Terminate the current session or exit the program\n"
    print(message)
    log_to_file(message)  # Log the command list to the file

def handle_client(client_socket, addr, session_number):
    """Creates a fully interactive reverse shell with real-time output."""
    print(f"[+] Session {session_number} connected from {addr}")
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
                print(f"[*] Session {session_number} moved to background.")
                log_to_file(f"[*] Session {session_number} moved to background.")
                stop_event.set()
                return
            if command.lower() == "exit":
                print(f"[-] Terminating session {session_number}.")
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
        print(f"\n[*] Session {session_number} moved to background.")
        log_to_file(f"[*] Session {session_number} moved to background.")
        stop_event.set()
        recv_thread.join()
        return
    except BrokenPipeError:
        print(f"[-] Session {session_number} disconnected.")
        log_to_file(f"[-] Session {session_number} disconnected.")
        stop_event.set()
        recv_thread.join()
        return
    except Exception as e:
        print_error(str(e))

    print(f"[-] Session {session_number} disconnected.")
    log_to_file(f"[-] Session {session_number} disconnected.")  # Log session disconnection
    with lock:
        del sessions[session_number]

def session_manager():
    """Main menu that allows session management."""
    time.sleep(1)  # 🟢 Wait for 1 second before dropping into LSTNR$
    
    while True:
        try:
            while not notifications.empty():
                print(notifications.get())

            command = input(f"{BLUE}LSTNR$ {RESET}").strip()
            
            # Log the command input
            log_to_file(f"LSTNR$ {command}")
            
            if command == "":
                print_commands()
            elif command == "help":
                print_commands()
            elif command == "?":
                print_commands()
            elif command.lower() == "ls":
                while not notifications.empty():
                    print(notifications.get())

                print("\n+-----------------------+")
                print("| ID  | IP ADDRESS      |")
                print("+-----------------------+")
                session_list = ""
                for sid, session in sessions.items():
                    session_list += f"| {sid:<3} | {session['addr'][0]:<15} |\n"
                    print(f"| {sid:<3} | {session['addr'][0]:<15} |")
                print("+-----------------------+\n")
                
                # Log the session table into the file
                log_to_file("Session list displayed:")
                log_to_file("+-----------------------+")
                log_to_file("| ID  | IP ADDRESS      |")
                log_to_file("+-----------------------+")
                log_to_file(session_list)
                log_to_file("+-----------------------+\n")
                
            elif command.startswith("cs "):
                try:
                    sid = int(command.split()[1])
                    if sid in sessions:
                        handle_client(sessions[sid]['socket'], sessions[sid]['addr'], sid)
                    else:
                        print_error("Invalid session ID.")
                except:
                    print_error("Invalid command. Usage: cs <session_id>")
            elif command.lower() == "die":
                print("[-] Terminating all sessions...")
                log_to_file("[-] Terminating all sessions...")
                with lock:
                    for sid in list(sessions.keys()):
                        sessions[sid]["socket"].send(b"exit\n")
                        sessions[sid]["socket"].close()
                        del sessions[sid]
                print("[+] All sessions terminated.")
                log_to_file("[+] All sessions terminated.")
            elif command.lower() == "exit":
                print("Killing all sessions.")
                print("Shutting down LSTNR.")
                log_to_file("Killing all sessions. Shutting down LSTNR.")
                break
            else:
                print_error("Unknown command. Use 'ls', 'cs <id>', 'bs', 'exit', or 'die'.")
                print_commands()
        except KeyboardInterrupt:
            print("\n[*] Type 'exit' to close LSTNR.")
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
    print(""" 
    ██╗     ███████╗████████╗███╗   ██╗██████╗ 
    ██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
    ██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
    ██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
    ███████╗███████║   ██║   ██║ ╚████║██║  ██║
    ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control - v1.3
    - MADE FOR REVERSE SHELL MANAGEMENT
    """)
    print(f"[*] Listening on {HOST}:{PORT}")
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
        print_error("Usage: ./listener.py -p <port>")
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
        print("\n[-] Exiting... Closing all connections.")
        for sid in list(sessions.keys()):
            try:
                sessions[sid]["socket"].send(b"exit\n")
                sessions[sid]["socket"].close()
            except:
                pass
        sys.exit(0)
    except Exception as e:
        print_error(str(e))
