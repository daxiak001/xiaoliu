# Fix Chinese Encoding Issues in PowerShell
# Usage: .\fix-encoding.ps1

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  PowerShell Encoding Fix Tool" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Set console to UTF-8
Write-Host "[Step 1] Setting console encoding to UTF-8..." -ForegroundColor Yellow
try {
    chcp 65001 | Out-Null
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
    Write-Host "  OK Console encoding set to UTF-8" -ForegroundColor Green
} catch {
    Write-Host "  WARN Failed to set encoding, but continuing..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[Step 2] Testing Chinese character display..." -ForegroundColor Yellow

# Test Chinese characters
$testString = "测试中文显示：你好世界！"
Write-Host "  Test string: $testString" -ForegroundColor White

Write-Host ""
Write-Host "[Step 3] Testing file operations..." -ForegroundColor Yellow

# Test file write/read with Chinese
$testFile = "encoding_test_中文.txt"
try {
    "测试中文文件内容" | Out-File -FilePath $testFile -Encoding UTF8
    $content = Get-Content $testFile -Encoding UTF8
    Write-Host "  Test file content: $content" -ForegroundColor White
    Remove-Item $testFile -ErrorAction SilentlyContinue
    Write-Host "  OK File operations work correctly" -ForegroundColor Green
} catch {
    Write-Host "  WARN File test failed: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Encoding Configuration Complete" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Current Settings:" -ForegroundColor Cyan
Write-Host "  Console Code Page: $(chcp)" -ForegroundColor White
Write-Host "  Output Encoding: $($OutputEncoding.EncodingName)" -ForegroundColor White
Write-Host ""
Write-Host "Note: This encoding will apply to current session only." -ForegroundColor Yellow
Write-Host "For permanent fix, add 'chcp 65001' to your PowerShell profile." -ForegroundColor Yellow
Write-Host ""
