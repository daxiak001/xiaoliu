# Complete Encoding Fix for PowerShell and SSH
# Solves all Chinese character display issues

param(
    [switch]$Permanent
)

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Complete Encoding Fix Tool" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Fix PowerShell console encoding
Write-Host "[Step 1] Fixing PowerShell console encoding..." -ForegroundColor Yellow
try {
    # Set code page to UTF-8
    $null = chcp 65001
    
    # Set .NET console encoding
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    
    # Set PowerShell output encoding
    $global:OutputEncoding = [System.Text.Encoding]::UTF8
    
    Write-Host "  OK Console encoding: UTF-8 (65001)" -ForegroundColor Green
} catch {
    Write-Host "  WARN Failed: $_" -ForegroundColor Yellow
}

# Step 2: Test Chinese display
Write-Host ""
Write-Host "[Step 2] Testing Chinese character display..." -ForegroundColor Yellow
$testChinese = "测试中文：你好世界！小柳云端系统"
Write-Host "  Display test: $testChinese" -ForegroundColor White

# Step 3: Create permanent fix if requested
if ($Permanent) {
    Write-Host ""
    Write-Host "[Step 3] Creating permanent fix..." -ForegroundColor Yellow
    
    $profilePath = $PROFILE.CurrentUserAllHosts
    $profileDir = Split-Path $profilePath
    
    if (-not (Test-Path $profileDir)) {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    }
    
    $encodingFix = @"

# Auto-fix encoding for Chinese characters
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
`$OutputEncoding = [System.Text.Encoding]::UTF8
"@
    
    if (Test-Path $profilePath) {
        $currentProfile = Get-Content $profilePath -Raw
        if ($currentProfile -notmatch "chcp 65001") {
            Add-Content -Path $profilePath -Value $encodingFix
            Write-Host "  OK Added encoding fix to PowerShell profile" -ForegroundColor Green
        } else {
            Write-Host "  INFO Encoding fix already exists in profile" -ForegroundColor Cyan
        }
    } else {
        Set-Content -Path $profilePath -Value $encodingFix
        Write-Host "  OK Created PowerShell profile with encoding fix" -ForegroundColor Green
    }
    
    Write-Host "  Profile location: $profilePath" -ForegroundColor Gray
}

# Step 4: Show current settings
Write-Host ""
Write-Host "[Step 4] Current encoding settings:" -ForegroundColor Yellow
Write-Host "  Code Page: $(chcp)" -ForegroundColor White
Write-Host "  Console Output: $([Console]::OutputEncoding.EncodingName)" -ForegroundColor White
Write-Host "  PowerShell Output: $($OutputEncoding.EncodingName)" -ForegroundColor White

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Encoding Fix Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

if (-not $Permanent) {
    Write-Host "Note: This fix applies to current session only." -ForegroundColor Yellow
    Write-Host "Run with -Permanent flag to make it permanent:" -ForegroundColor Yellow
    Write-Host "  .\encoding-fix-complete.ps1 -Permanent" -ForegroundColor Cyan
    Write-Host ""
}

# Step 5: Create helper batch file for easy use
$batchContent = @"
@echo off
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; `$OutputEncoding=[System.Text.Encoding]::UTF8; %*"
"@

Set-Content -Path "run-with-utf8.bat" -Value $batchContent -Encoding ASCII
Write-Host "Created helper batch file: run-with-utf8.bat" -ForegroundColor Cyan
Write-Host "Usage: run-with-utf8.bat your-command" -ForegroundColor Gray
Write-Host ""
