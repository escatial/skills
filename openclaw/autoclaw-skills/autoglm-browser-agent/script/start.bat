@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM AutoGLM Browser Agent -- Start (Register MCP + Start Relay)
REM
REM Usage:
REM   start.bat              Register + start relay (idempotent)
REM   start.bat --status     Check status only

set "SCRIPT_DIR=%~dp0"
REM Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for %%I in ("%SCRIPT_DIR%\..") do set "BASE_DIR=%%~fI"

set "MCPORTER=%BASE_DIR%\dependency\mcporter.exe"
set "MCP_SERVER=%BASE_DIR%\dist\mcp_server.exe"
set "RELAY=%BASE_DIR%\dist\relay.exe"
set "LOG_DIR=%BASE_DIR%\mcp_output"
set "MCP_NAME=autoglm-browser-agent"

set "RELAY_CHROME_PORT=62030"
set "RELAY_MCP_PORT=62031"

if "%~1"=="--status" goto :do_status
if "%~1"=="-s" goto :do_status
if "%~1"=="status" goto :do_status
if "%~1"=="--help" goto :do_help
if "%~1"=="-h" goto :do_help
if "%~1"=="" goto :do_start
if "%~1"=="start" goto :do_start
echo Unknown argument: %~1
echo Usage: %~nx0 [--status]
exit /b 1

REM == Preflight ======================================================

:do_start
echo.
echo ========================================
echo   AutoGLM Browser Agent -- Start
echo ========================================

if not exist "%MCPORTER%" (
    echo   [X] mcporter not found: %MCPORTER%
    exit /b 1
)
if not exist "%MCP_SERVER%" (
    echo   [X] mcp_server not found: %MCP_SERVER%
    exit /b 1
)
if not exist "%RELAY%" (
    echo   [X] relay not found: %RELAY%
    exit /b 1
)

REM == Register MCP ===================================================

echo.
echo [1/2] Register MCP Server

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

"%MCPORTER%" config add %MCP_NAME% --command "%MCP_SERVER%" --arg --start_url --arg https://www.bing.com --arg --window_width --arg 1456 --arg --window_height --arg 819 --arg --resize_width --arg 1456 --arg --resize_height --arg 819 --arg --max_steps --arg 100 --arg --log_dir --arg "%LOG_DIR%" --arg --if_subagent >nul 2>&1

REM Verify
"%MCPORTER%" list %MCP_NAME% 2>&1 | findstr /i /c:"browser" /c:"autoglm" /c:"%MCP_NAME%" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] MCP Server registered: %MCP_NAME%
) else (
    echo   [!] Registration result uncertain, please verify manually
)

REM == Start Relay ====================================================

echo.
echo [2/2] Start Relay Daemon

REM Check if relay is already running
netstat -ano 2>nul | findstr "LISTENING" | findstr ":%RELAY_MCP_PORT% " >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] Relay already running ^(chrome=%RELAY_CHROME_PORT%, mcp=%RELAY_MCP_PORT%^)
    goto :start_done
)

start /b "" "%RELAY%"

REM Wait up to 5 seconds
set /a waited=0
:wait_loop
if !waited! geq 50 goto :wait_timeout
timeout /t 1 /nobreak >nul 2>&1
set /a waited+=10
netstat -ano 2>nul | findstr "LISTENING" | findstr ":%RELAY_MCP_PORT% " >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] Relay started ^(chrome=%RELAY_CHROME_PORT%, mcp=%RELAY_MCP_PORT%^)
    goto :start_done
)
goto :wait_loop

:wait_timeout
echo   [!] Relay started but port not ready yet

:start_done
echo.
echo   Startup complete
echo   Management: %SCRIPT_DIR%\reset.bat
echo   Status:     %~nx0 --status
goto :eof

REM == Status =========================================================

:do_status
echo.
echo === Service Status ===

REM MCP registration
if exist "%MCPORTER%" (
    "%MCPORTER%" list 2>&1 | findstr /i /c:"browser-agent" /c:"autoglm" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [OK] MCP registered
    ) else (
        echo   [X] MCP not registered
    )
) else (
    echo   [!] mcporter not available
)

REM Relay
netstat -ano 2>nul | findstr "LISTENING" | findstr ":%RELAY_MCP_PORT% " >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] Relay running ^(chrome=%RELAY_CHROME_PORT%, mcp=%RELAY_MCP_PORT%^)
) else (
    echo   [X] Relay not running
)

REM MCP Server processes
tasklist /fi "imagename eq mcp_server.exe" 2>nul | findstr /i "mcp_server" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] MCP Server processes running
) else (
    echo   MCP Server processes: 0 ^(started on demand, this is normal^)
)

echo.
goto :eof

REM == Help ===========================================================

:do_help
echo Usage: %~nx0 [--status]
echo.
echo   (no args)   Register MCP Server + Start Relay (idempotent)
echo   --status    Check status only
echo.
echo See also:
echo   reset.bat          Management / reset / cleanup tool
echo   reset.bat --help   View all management commands
goto :eof
