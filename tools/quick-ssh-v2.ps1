# Quick SSH Command Tool V2 - Never Hang, Always Works
# Usage: .\quick-ssh-v2.ps1 "command to execute"

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    [int]$Timeout = 10
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = Get-Location }
$ServerKey = Join-Path $ScriptDir "server_key"
$ServerHost = "ubuntu@43.142.176.53"

Write-Host ""
Write-Host "Executing SSH command (${Timeout}s timeout)..." -ForegroundColor Cyan
Write-Host "Command: $Command" -ForegroundColor Gray
Write-Host ""

# Build SSH command with all non-interactive options
$sshArgs = @(
    "-i", $ServerKey,
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=$Timeout",
    "-o", "ServerAliveInterval=5",
    "-o", "ServerAliveCountMax=2",
    $ServerHost,
    $Command
)

try {
    # Use native ssh command with timeout via job
    $job = Start-Job -ScriptBlock {
        param($sshArgs)
        & ssh $sshArgs 2>&1
    } -ArgumentList (,$sshArgs)
    
    # Wait for job with timeout
    $completed = Wait-Job $job -Timeout $Timeout
    
    if ($null -eq $completed) {
        Write-Host "WARN Command timeout (${Timeout}s), stopping job..." -ForegroundColor Yellow
        Stop-Job $job
        Remove-Job $job
        exit 2
    }
    
    # Get job result
    $result = Receive-Job $job
    $jobState = $job.State
    Remove-Job $job
    
    if ($jobState -eq "Completed") {
        Write-Host "SUCCESS Command executed" -ForegroundColor Green
        Write-Host ""
        if ($result) {
            Write-Host "Output:" -ForegroundColor Cyan
            $result | ForEach-Object { Write-Host $_ }
        }
        exit 0
    } else {
        Write-Host "FAIL Command failed (state: $jobState)" -ForegroundColor Red
        Write-Host ""
        if ($result) {
            Write-Host "Output:" -ForegroundColor Yellow
            $result | ForEach-Object { Write-Host $_ }
        }
        exit 1
    }
    
} catch {
    Write-Host "ERROR Exception: $_" -ForegroundColor Red
    exit 1
}
