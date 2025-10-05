# Quick SSH Command Tool with UTF-8 Support
# Usage: .\quick-ssh-utf8.ps1 "command to execute"

param(
    [Parameter(Mandatory=$true)]
    [string]$Command,
    [int]$Timeout = 10
)

# Set UTF-8 encoding first
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = Get-Location }
$ServerKey = Join-Path $ScriptDir "server_key"
$ServerHost = "ubuntu@43.142.176.53"

Write-Host ""
Write-Host "执行SSH命令 (${Timeout}秒超时)..." -ForegroundColor Cyan
Write-Host "命令: $Command" -ForegroundColor Gray
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
        Write-Host "警告: 命令超时 (${Timeout}秒)，正在终止..." -ForegroundColor Yellow
        Stop-Job $job
        Remove-Job $job
        exit 2
    }
    
    # Get job result
    $result = Receive-Job $job
    $jobState = $job.State
    Remove-Job $job
    
    if ($jobState -eq "Completed") {
        Write-Host "✅ 命令执行成功" -ForegroundColor Green
        Write-Host ""
        if ($result) {
            Write-Host "输出:" -ForegroundColor Cyan
            $result | ForEach-Object { Write-Host $_ }
        }
        exit 0
    } else {
        Write-Host "❌ 命令执行失败 (状态: $jobState)" -ForegroundColor Red
        Write-Host ""
        if ($result) {
            Write-Host "输出:" -ForegroundColor Yellow
            $result | ForEach-Object { Write-Host $_ }
        }
        exit 1
    }
    
} catch {
    Write-Host "❌ 异常: $_" -ForegroundColor Red
    exit 1
}
