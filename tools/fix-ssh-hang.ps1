# SSH Connection Fix Tool - No Hang Version
# 2025-10-05

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) { $ScriptDir = Get-Location }
$ServerKey = Join-Path $ScriptDir "server_key"
$ServerHost = "ubuntu@43.142.176.53"

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  SSH Connection Fix Tool" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check key file
if (-not (Test-Path $ServerKey)) {
    Write-Host "[ERROR] Key file not found: $ServerKey" -ForegroundColor Red
    exit 1
}

Write-Host "[Step 1] Fixing key permissions..." -ForegroundColor Yellow

# Fix Windows key permissions (SSH requires strict permissions)
try {
    # Disable inheritance and remove all permissions
    icacls $ServerKey /inheritance:r | Out-Null
    # Grant full control to current user only
    icacls $ServerKey /grant:r "$($env:USERNAME):(F)" | Out-Null
    Write-Host "  OK Key permissions fixed" -ForegroundColor Green
} catch {
    Write-Host "  WARN Permission fix failed, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[Step 2] Testing SSH connection (5 sec timeout)..." -ForegroundColor Yellow

# Create temp files
$outputFile = New-TemporaryFile
$errorFile = New-TemporaryFile

try {
    # Use Start-Process with timeout control
    $process = Start-Process -FilePath "ssh" `
        -ArgumentList @(
            "-i", $ServerKey,
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            "-o", "ServerAliveInterval=5",
            "-o", "ServerAliveCountMax=2",
            $ServerHost,
            "echo 'SSH connection successful'"
        ) `
        -NoNewWindow `
        -Wait `
        -PassThru `
        -RedirectStandardOutput $outputFile `
        -RedirectStandardError $errorFile
    
    $output = Get-Content $outputFile -Raw -ErrorAction SilentlyContinue
    $error_output = Get-Content $errorFile -Raw -ErrorAction SilentlyContinue
    
    if ($process.ExitCode -eq 0 -and $output -match "successful") {
        Write-Host "  OK SSH connection test passed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "[Step 3] Testing file upload..." -ForegroundColor Yellow
        
        # Create test file
        $testFile = "ssh_test_file.txt"
        "SSH Test $(Get-Date)" | Out-File -FilePath $testFile -Encoding UTF8
        
        # Test SCP upload
        $scpProcess = Start-Process -FilePath "scp" `
            -ArgumentList @(
                "-i", $ServerKey,
                "-o", "BatchMode=yes",
                "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=5",
                $testFile,
                "${ServerHost}:/tmp/"
            ) `
            -NoNewWindow `
            -Wait `
            -PassThru `
            -RedirectStandardError $errorFile
        
        if ($scpProcess.ExitCode -eq 0) {
            Write-Host "  OK File upload test passed!" -ForegroundColor Green
            
            # Cleanup
            Remove-Item $testFile -ErrorAction SilentlyContinue
            Remove-Item $outputFile, $errorFile -ErrorAction SilentlyContinue
            
            Write-Host ""
            Write-Host "=========================================" -ForegroundColor Green
            Write-Host "  SUCCESS SSH connection fully fixed!" -ForegroundColor Green
            Write-Host "=========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "You can now use SSH and SCP commands normally." -ForegroundColor Cyan
            exit 0
        } else {
            $scpError = Get-Content $errorFile -Raw -ErrorAction SilentlyContinue
            Write-Host "  FAIL File upload failed" -ForegroundColor Red
            Write-Host "  Error: $scpError" -ForegroundColor Red
        }
    } else {
        Write-Host "  FAIL SSH connection failed" -ForegroundColor Red
        if ($error_output) {
            Write-Host "  Error: $error_output" -ForegroundColor Red
        }
    }
    
    # Cleanup
    Remove-Item $outputFile, $errorFile -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "  FAIL Connection test exception: $_" -ForegroundColor Red
    Remove-Item $outputFile, $errorFile -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host "  Diagnostic Suggestions" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Check network connection" -ForegroundColor White
Write-Host "2. Verify server IP: 43.142.176.53" -ForegroundColor White
Write-Host "3. Validate key file" -ForegroundColor White
Write-Host "4. Check firewall (port 22)" -ForegroundColor White
Write-Host ""

exit 1
