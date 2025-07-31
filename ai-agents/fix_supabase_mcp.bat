@echo off
echo Fixing Supabase MCP Configuration...
echo.

REM Create backup of current config
copy "%APPDATA%\Claude\claude_desktop_config.json" "%APPDATA%\Claude\claude_desktop_config_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json"

REM Create temporary updated config
echo Creating updated configuration...

REM Use PowerShell to update the JSON
powershell -ExecutionPolicy Bypass -Command "$configPath = Join-Path $env:APPDATA 'Claude\claude_desktop_config.json'; $config = Get-Content $configPath | ConvertFrom-Json; if ($config.mcpServers.supabase) { $config.mcpServers.supabase.args = @('/c', 'npx', '-y', '@supabase/mcp-server-supabase@latest', '--project-ref=dukeqfbvzszyegnamvmd'); $config | ConvertTo-Json -Depth 10 | Set-Content $configPath; Write-Host 'Supabase MCP configuration updated successfully!'; Write-Host 'Removed --read-only flag to enable full database access.' } else { Write-Host 'Supabase MCP server not found in configuration!' }"

echo.
echo Configuration updated! Please restart Claude for changes to take effect.
echo.
pause