@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
REM autoclaw - Browser automation single entry point (Windows)
REM
REM Two modes:
REM   autoclaw task="..."                           -> agent mode (default)
REM   autoclaw --mode=cli bilibili hot --limit=10   -> cli mode
REM
REM Handles: relay startup + MCP registration + task execution

set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for %%i in ("%SCRIPT_DIR%\..") do set "BASE_DIR=%%~fi"

set "MCPORTER=%BASE_DIR%\dependency\mcporter.exe"
set "MCP_SERVER=%BASE_DIR%\dist\mcp_server.exe"
set "RELAY=%BASE_DIR%\dist\relay.exe"
set "LOG_DIR=%BASE_DIR%\mcp_output"
set "MCP_NAME=autoglm-browser-agent"

set "RELAY_CHROME_PORT=62030"
set "RELAY_MCP_PORT=62031"

REM -- Parse --mode argument
set "_MODE=agent"
set "_REMAINING="
set "_FIRST=1"
for %%a in (%*) do (
    if "%%a"=="--mode=cli" (
        set "_MODE=cli"
    ) else if "%%a"=="--mode=agent" (
        set "_MODE=agent"
    ) else (
        if defined _FIRST (
            set "_REMAINING=%%a"
            set "_FIRST="
        ) else (
            set "_REMAINING=!_REMAINING! %%a"
        )
    )
)

REM -- CLI mode
if "%_MODE%"=="cli" (
    netstat -ano 2>nul | findstr ":%RELAY_MCP_PORT% " | findstr "LISTENING" >nul 2>&1
    if errorlevel 1 (
        if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
        start /b "" "%RELAY%" %RELAY_CHROME_PORT% %RELAY_MCP_PORT% >>"%LOG_DIR%\relay.log" 2>&1
        for /l %%i in (1,1,10) do (
            timeout /t 1 /nobreak >nul 2>&1
            netstat -ano 2>nul | findstr ":%RELAY_MCP_PORT% " | findstr "LISTENING" >nul 2>&1 && goto :cli_relay_ready
        )
    )
    :cli_relay_ready
    python "%SCRIPT_DIR%\cli_main.py" !_REMAINING! --relay-port=%RELAY_MCP_PORT%
    goto :eof
)

REM -- Agent mode

REM 1. Ensure relay running
netstat -ano 2>nul | findstr ":%RELAY_MCP_PORT% " | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
    start /b "" "%RELAY%" %RELAY_CHROME_PORT% %RELAY_MCP_PORT% >>"%LOG_DIR%\relay.log" 2>&1
    for /l %%i in (1,1,10) do (
        timeout /t 1 /nobreak >nul 2>&1
        netstat -ano 2>nul | findstr ":%RELAY_MCP_PORT% " | findstr "LISTENING" >nul 2>&1 && goto :relay_ready
    )
)
:relay_ready

REM 2. Ensure MCP registered (idempotent)
"%MCPORTER%" config add %MCP_NAME% --command "%MCP_SERVER%" --arg --start_url --arg https://www.bing.com --arg --window_width --arg 1456 --arg --window_height --arg 819 --arg --resize_width --arg 1456 --arg --resize_height --arg 819 --arg --max_steps --arg 100 --arg --log_dir --arg "%LOG_DIR%" --arg --if_subagent >nul 2>&1

REM 3. Execute browser task (default --timeout 7200000)
echo %* | findstr /C:"--timeout" >nul 2>&1
if errorlevel 1 (
    "%MCPORTER%" call "%MCP_NAME%.browser_subagent" %* --timeout 7200000
) else (
    "%MCPORTER%" call "%MCP_NAME%.browser_subagent" %*
)
