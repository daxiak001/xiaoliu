# Quick SCP Upload Tool V2 - Never Hang, Always Works
# Usage: .\quick-scp-v2.ps1 -SourceFile "local_file" -TargetPath "remote_path"

param(
    [Parameter(Mandatory=$true)]
    [string]$SourceFile,
    [Parameter(Mandatory=$true)]
    [string]$TargetPath,
    [int]$Timeout = 30
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = Get-Location }
$ServerKey = Join-Path $ScriptDir "server_key"
$ServerHost = "ubuntu@43.142.176.53"

Write-Host ""
Write-Host "Uploading file (${Timeout}s timeout)..." -ForegroundColor Cyan
Write-Host ""

# Check source file
if (-not (Test-Path $SourceFile)) {
    Write-Host "ERROR Source file not found: $SourceFile" -ForegroundColor Red
    exit 1
}

$fileInfo = Get-Item $SourceFile
$fileSize = [math]::Round($fileInfo.Length / 1KB, 2)

Write-Host "Source: $($fileInfo.Name)" -ForegroundColor White
Write-Host "Size: ${fileSize} KB" -ForegroundColor Gray
Write-Host "Target: ${ServerHost}:${TargetPath}" -ForegroundColor Gray
Write-Host ""

# Build SCP command
$scpArgs = @(
    "-i", $ServerKey,
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=10",
    $SourceFile,
    "${ServerHost}:${TargetPath}"
)

try {
    Write-Host "Uploading..." -ForegroundColor Yellow
    
    # Use native scp command with timeout via job
    $job = Start-Job -ScriptBlock {
        param($scpArgs)
        & scp $scpArgs 2>&1
    } -ArgumentList (,$scpArgs)
    
    # Wait for job with timeout
    $completed = Wait-Job $job -Timeout $Timeout
    
    if ($null -eq $completed) {
        Write-Host ""
        Write-Host "WARN Upload timeout (${Timeout}s), stopping job..." -ForegroundColor Yellow
        Stop-Job $job
        Remove-Job $job
        exit 2
    }
    
    # Get job result
    $result = Receive-Job $job
    $jobState = $job.State
    Remove-Job $job
    
    if ($jobState -eq "Completed") {
        Write-Host ""
        Write-Host "SUCCESS Upload completed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "File saved to: ${ServerHost}:${TargetPath}" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host ""
        Write-Host "FAIL Upload failed (state: $jobState)" -ForegroundColor Red
        if ($result) {
            Write-Host ""
            Write-Host "Output:" -ForegroundColor Yellow
            $result | ForEach-Object { Write-Host $_ }
        }
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR Upload exception: $_" -ForegroundColor Red
    exit 1
}
