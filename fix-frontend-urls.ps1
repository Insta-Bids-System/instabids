# PowerShell script to fix all hardcoded URLs in frontend
# This replaces http://localhost:8008 with relative URLs

$webSrcPath = "C:\Users\Not John Or Justin\Documents\instabids\web\src"

Write-Host "Starting URL fix in frontend components..." -ForegroundColor Green

# Get all TypeScript/TSX files
$files = Get-ChildItem -Path $webSrcPath -Include *.ts,*.tsx -Recurse

$totalFiles = $files.Count
$fixedCount = 0

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    
    # Replace http://localhost:8008 with empty string (relative URL)
    $content = $content -replace 'http://localhost:8008', ''
    
    # Replace ws://localhost:8008 with empty string (will be handled by buildWsUrl)
    $content = $content -replace 'ws://localhost:8008', ''
    
    # Replace fetch("http://localhost:8008 with fetch("
    $content = $content -replace 'fetch\("http://localhost:8008', 'fetch("'
    
    # Replace fetch(`http://localhost:8008 with fetch(`
    $content = $content -replace 'fetch\(`http://localhost:8008', 'fetch(`'
    
    if ($content -ne $originalContent) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        Write-Host "Fixed: $($file.Name)" -ForegroundColor Yellow
        $fixedCount++
    }
}

Write-Host "`nSummary:" -ForegroundColor Green
Write-Host "Total files scanned: $totalFiles" -ForegroundColor Cyan
Write-Host "Files fixed: $fixedCount" -ForegroundColor Cyan
Write-Host "URL fix complete!" -ForegroundColor Green