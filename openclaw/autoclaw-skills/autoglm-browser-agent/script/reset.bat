@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM AutoGLM Browser Agent -- Management / Reset / Cleanup
REM
REM Usage:
REM   reset.bat              Interactive menu
REM   reset.bat status       Check status
REM   reset.bat kill-relay   Stop relay
REM   reset.bat kill-mcp     Stop mcp_server
REM   reset.bat kill-all     Stop relay + mcp_server
REM   reset.bat unreg        Unregister MCP Server
REM   reset.bat clean-state  Clean state files
REM   reset.bat full-reset   Full reset

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for %%I in ("%SCRIPT_DIR%\..") do set "BASE_DIR=%%~fI"

set "STATE_DIR=%USERPROFILE%\.openclaw-autoclaw"
set "MCPORTER=%BASE_DIR%\dependency\mcporter.exe"
set "LOG_DIR=%BASE_DIR%\mcp_output"
set "RELAY_CHROME_PORT=62030"
set "RELAY_MCP_PORT=62031"

if "%~1"=="" goto :do_menu
if "%~1"=="status" goto :do_status
if "%~1"=="kill-relay" goto :do_kill_relay
if "%~1"=="kill-mcp" goto :do_kill_mcp
if "%~1"=="kill-all" goto :do_kill_all
if "%~1"=="unreg" goto :do_unreg
if "%~1"=="clean-session" goto :do_clean_session
if "%~1"=="clean-results" goto :do_clean_results
if "%~1"=="clean-logs" goto :do_clean_logs
if "%~1"=="clean-auth" goto :do_clean_auth
if "%~1"=="clean-state" goto :do_clean_state
if "%~1"=="full-reset" goto :do_full_reset
if "%~1"=="-h" goto :do_help
if "%~1"=="--help" goto :do_help
echo Unknown command: %~1
echo Run %~nx0 --help for available commands
exit /b 1

REM == Status =========================================================

:do_status
echo.
echo === Process Status ===

REM Relay
netstat -ano 2>nul | findstr "LISTENING" | findstr ":%RELAY_MCP_PORT% " >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] Relay Daemon running ^(chrome=%RELAY_CHROME_PORT%, mcp=%RELAY_MCP_PORT%^)
) else (
    echo   [X] Relay Daemon not running
)

REM MCP Server
tasklist /fi "imagename eq mcp_server.exe" 2>nul | findstr /i "mcp_server" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [OK] MCP Server processes running
) else (
    echo   [X] MCP Server: no running processes
)

echo.
echo === MCP Registration ===

if exist "%MCPORTER%" (
    "%MCPORTER%" list 2>&1 | findstr /i /c:"browser-agent" /c:"autoglm" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [OK] MCP Server registered
    ) else (
        echo   [X] No browser-agent registration detected
    )
) else (
    echo   [!] mcporter not available
)

echo.
echo === State Files ===

if exist "%STATE_DIR%\session_pool.json" (
    echo   session_pool.json: exists
) else (
    echo   session_pool.json: not found
)

if exist "%STATE_DIR%\active_port" (
    echo   active_port: exists
) else (
    echo   active_port: not found
)

if exist "%STATE_DIR%\config.json" (
    echo   config.json: exists
) else (
    echo   config.json: not found
)

if exist "%STATE_DIR%\request-headers.json" (
    echo   request-headers.json: exists ^(token cache^)
) else (
    echo   request-headers.json: not found
)

if exist "%STATE_DIR%\.gateway-token" (
    echo   .gateway-token: exists
) else (
    echo   .gateway-token: not found
)

echo.
goto :eof

REM == Kill Relay =====================================================

:do_kill_relay
echo.
echo === Stop Relay Daemon ===

tasklist /fi "imagename eq relay.exe" 2>nul | findstr /i "relay.exe" >nul 2>&1
if !errorlevel! equ 0 (
    taskkill /f /im relay.exe >nul 2>&1
    echo   [OK] Relay processes terminated
) else (
    echo   Relay: no processes found
)
goto :eof

REM == Kill MCP =======================================================

:do_kill_mcp
echo.
echo === Stop MCP Server ===

tasklist /fi "imagename eq mcp_server.exe" 2>nul | findstr /i "mcp_server.exe" >nul 2>&1
if !errorlevel! equ 0 (
    taskkill /f /im mcp_server.exe >nul 2>&1
    echo   [OK] MCP Server processes terminated
) else (
    echo   MCP Server: no processes found
)
goto :eof

REM == Kill All =======================================================

:do_kill_all
call :do_kill_mcp
call :do_kill_relay
goto :eof

REM == Unreg ==========================================================

:do_unreg
echo.
echo === Unregister MCP Server ===

if not exist "%MCPORTER%" (
    echo   [!] mcporter not available
    goto :eof
)

REM Try common names
for %%N in (autoglm-browser-agent browser-agent-full) do (
    "%MCPORTER%" config remove %%N >nul 2>&1
    if !errorlevel! equ 0 (
        echo   [OK] Unregistered: %%N
    )
)

"%MCPORTER%" list 2>&1 | findstr /i /c:"browser-agent" /c:"autoglm" >nul 2>&1
if !errorlevel! equ 0 (
    echo   [!] Registration still detected, please check manually
) else (
    echo   [OK] No browser-agent registrations
)
goto :eof

REM == Clean Session ==================================================

:do_clean_session
echo.
echo === Clean Session Pool ===

if exist "%STATE_DIR%\session_pool.json" (
    echo {"busy": null, "sessions": []} > "%STATE_DIR%\session_pool.json"
    echo   [OK] session_pool.json reset
) else (
    echo   session_pool.json not found, skipping
)

if exist "%STATE_DIR%\active_port" (
    del /f "%STATE_DIR%\active_port" >nul 2>&1
    echo   [OK] active_port removed
) else (
    echo   active_port not found
)
goto :eof

REM == Clean Results ==================================================

:do_clean_results
echo.
echo === Clean Browser Result Files ===

set "count=0"
for %%F in ("%STATE_DIR%\browser_result_*") do set /a count+=1
if !count! gtr 0 (
    del /f "%STATE_DIR%\browser_result_*" >nul 2>&1
    echo   [OK] Deleted !count! browser_result file^(s^)
) else (
    echo   No browser_result files
)
goto :eof

REM == Clean Logs =====================================================

:do_clean_logs
echo.
echo === Clean Logs ===

set "cleaned=0"
for %%D in ("%BASE_DIR%\mcp_output" "%STATE_DIR%\mcp_output" "%STATE_DIR%\logs") do (
    if exist "%%~D" (
        rd /s /q "%%~D" >nul 2>&1
        mkdir "%%~D" >nul 2>&1
        echo   [OK] %%~D cleared
        set "cleaned=1"
    )
)
if !cleaned! equ 0 echo   No log directories found
goto :eof

REM == Clean Auth =====================================================

:do_clean_auth
echo.
echo === Clean Auth Cache ===

if exist "%STATE_DIR%\request-headers.json" (
    del /f "%STATE_DIR%\request-headers.json" >nul 2>&1
    echo   [OK] request-headers.json removed
) else (
    echo   request-headers.json not found
)

if exist "%STATE_DIR%\.gateway-token" (
    del /f "%STATE_DIR%\.gateway-token" >nul 2>&1
    echo   [OK] .gateway-token removed
) else (
    echo   .gateway-token not found
)
goto :eof

REM == Clean State ====================================================

:do_clean_state
echo.
echo === Clean All State ===
echo   Will clean: session pool + browser results + logs + auth cache
echo.
call :do_clean_session
call :do_clean_results
call :do_clean_logs
call :do_clean_auth
echo   [OK] All state cleaned
goto :eof

REM == Full Reset =====================================================

:do_full_reset
echo.
echo === Full Reset ===
echo   Will execute: kill processes - unregister MCP - clean all state
echo.
call :do_kill_mcp
call :do_kill_relay
call :do_unreg
call :do_clean_state
echo.
echo === Reset Complete ===
echo   [OK] All components stopped, registrations cleared, state cleaned
echo   To restart, run: start.bat
goto :eof

REM == Menu ===========================================================

:do_menu
echo.
echo ========================================
echo   AutoGLM Browser Agent -- Management
echo ========================================
echo.
echo   1) Status Check          (status)
echo   2) Stop Relay            (kill-relay)
echo   3) Stop MCP Server       (kill-mcp)
echo   4) Stop All Processes    (kill-all)
echo   5) Unregister MCP        (unreg)
echo   -- Cleanup --
echo   6) Clean Session Pool    (clean-session)
echo   7) Clean Browser Results (clean-results)
echo   8) Clean Logs            (clean-logs)
echo   9) Clean Auth Cache      (clean-auth)
echo   a) Clean All State       (clean-state)
echo   -- Combined --
echo   f) Full Reset            (full-reset)
echo   0) Exit
echo.
set /p "choice=Select [0-9/a/f]: "
if "!choice!"=="1" goto :do_status
if "!choice!"=="2" goto :do_kill_relay
if "!choice!"=="3" goto :do_kill_mcp
if "!choice!"=="4" goto :do_kill_all
if "!choice!"=="5" goto :do_unreg
if "!choice!"=="6" goto :do_clean_session
if "!choice!"=="7" goto :do_clean_results
if "!choice!"=="8" goto :do_clean_logs
if "!choice!"=="9" goto :do_clean_auth
if /i "!choice!"=="a" goto :do_clean_state
if /i "!choice!"=="f" goto :do_full_reset
if "!choice!"=="0" exit /b 0
echo Invalid selection
exit /b 1

REM == Help ===========================================================

:do_help
echo Usage: %~nx0 [command]
echo.
echo Commands:
echo   status         Status check
echo   kill-relay     Stop Relay Daemon
echo   kill-mcp       Stop MCP Server processes
echo   kill-all       Stop all processes
echo   unreg          Unregister MCP Server
echo   clean-session  Clean Session Pool + active_port
echo   clean-results  Clean browser_result files
echo   clean-logs     Clean all logs
echo   clean-auth     Clean auth cache (token / gateway)
echo   clean-state    Clean all state (above four combined)
echo   full-reset     Full reset (kill + unregister + clean)
echo.
echo   No arguments shows interactive menu
goto :eof
