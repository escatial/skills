@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

REM AutoGLM Browser Agent -- Hot Update
REM
REM Usage:
REM   update.bat              Check and update
REM   update.bat --check      Check only
REM   update.bat --force      Force update

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for %%I in ("%SCRIPT_DIR%\..") do set "BASE_DIR=%%~fI"
set "VERSION_FILE=%BASE_DIR%\.update_version"
set "MANIFEST_URL_FILE=%BASE_DIR%\.update_manifest_url"
set "CONFIG_FILE=%USERPROFILE%\.openclaw-autoclaw\config.json"

set "MANIFEST_URL="
if defined UPDATE_MANIFEST_URL (
    set "MANIFEST_URL=%UPDATE_MANIFEST_URL%"
) else if exist "%MANIFEST_URL_FILE%" (
    set /p MANIFEST_URL=<"%MANIFEST_URL_FILE%"
)

if "%MANIFEST_URL%"=="" (
    echo   Manifest URL not found, skipping update check
    exit /b 0
)

set "ARG=%~1"
if "%ARG%"=="" set "ARG=update"

if "%ARG%"=="--check" goto :do_check
if "%ARG%"=="-c" goto :do_check
if "%ARG%"=="check" goto :do_check
if "%ARG%"=="--force" goto :do_update_force
if "%ARG%"=="-f" goto :do_update_force
if "%ARG%"=="force" goto :do_update_force
if "%ARG%"=="update" goto :do_update
if "%ARG%"=="-h" goto :show_help
if "%ARG%"=="--help" goto :show_help

echo Unknown: %ARG%. Run %~nx0 --help
exit /b 1

:do_check
echo.
echo === Check for Updates ===

set "TEMP_MANIFEST=%TEMP%\autoglm_manifest.json"
curl -sS --max-time 10 -o "%TEMP_MANIFEST%" "%MANIFEST_URL%" 2>nul
if %ERRORLEVEL% neq 0 (
    echo   [X] Cannot connect to update server
    exit /b 1
)

for /f "delims=" %%V in ('python -c "import json; print(json.load(open(r'%TEMP_MANIFEST%', encoding='utf-8'))['version'])" 2^>nul') do set "REMOTE_VERSION=%%V"
if not defined REMOTE_VERSION (
    echo   [X] Failed to parse manifest
    exit /b 1
)

set "LOCAL_VERSION=unknown"
if exist "%VERSION_FILE%" (
    set /p LOCAL_VERSION=<"%VERSION_FILE%"
)

echo   Local version:  %LOCAL_VERSION%
echo   Remote version: %REMOTE_VERSION%

if "%REMOTE_VERSION%" GTR "%LOCAL_VERSION%" (
    echo   [!] New version available: %REMOTE_VERSION%
    exit /b 0
) else (
    echo   [OK] Already up to date
    exit /b 1
)

:do_update_force
call :do_update_impl true
goto :eof

:do_update
call :do_update_impl false
goto :eof

:do_update_impl
set "FORCE=%~1"

echo.
echo === Hot Update ===

set "TEMP_MANIFEST=%TEMP%\autoglm_manifest.json"
curl -sS --max-time 10 -o "%TEMP_MANIFEST%" "%MANIFEST_URL%" 2>nul
if %ERRORLEVEL% neq 0 (
    echo   [X] Cannot connect to update server
    exit /b 1
)

for /f "delims=" %%V in ('python -c "import json; print(json.load(open(r'%TEMP_MANIFEST%', encoding='utf-8'))['version'])" 2^>nul') do set "REMOTE_VERSION=%%V"
if not defined REMOTE_VERSION (
    echo   [X] Failed to parse manifest
    exit /b 1
)

set "LOCAL_VERSION=unknown"
if exist "%VERSION_FILE%" (
    set /p LOCAL_VERSION=<"%VERSION_FILE%"
)

echo   Local version:  %LOCAL_VERSION%
echo   Remote version: %REMOTE_VERSION%

if "%FORCE%"=="false" (
    if not "%REMOTE_VERSION%" GTR "%LOCAL_VERSION%" (
        echo   [OK] Already up to date
        goto :eof
    )
)

echo   Platform: windows_x86_64

set "TEMP_DLLIST=%TEMP%\autoglm_dllist.txt"
python -c "import json; m=json.load(open(r'%TEMP_MANIFEST%', encoding='utf-8')); [print(f'{k}|{v[\"url\"]}|{v[\"hash\"]}') for k,v in m.get('files',{}).items()]; [print(f'{k}|{v[\"url\"]}|{v[\"hash\"]}') for k,v in m.get('platforms',{}).get('windows_x86_64',{}).items()]" > "%TEMP_DLLIST%" 2>nul

set "UPDATED=0"
set "FAILED=0"

for /f "usebackq tokens=1,2,3 delims=|" %%A in ("%TEMP_DLLIST%") do (
    call :download_file "%%A" "%%B" "%%C"
)

echo %REMOTE_VERSION%> "%VERSION_FILE%"

call :update_config "update_version" "%REMOTE_VERSION%"
call :remove_config_key "update_skipped"

echo.
if %FAILED% equ 0 (
    echo   [OK] Update complete: %UPDATED% file(s) updated (version %REMOTE_VERSION%)
) else (
    echo   [!] Update complete: %UPDATED% updated, %FAILED% failed
)

del /f /q "%TEMP_MANIFEST%" 2>nul
del /f /q "%TEMP_DLLIST%" 2>nul
goto :eof

:download_file
set "FILE_KEY=%~1"
set "URL=%~2"
set "REMOTE_HASH=%~3"

if "%FILE_KEY%"=="" goto :eof

set "TARGET=%BASE_DIR%\%FILE_KEY:/=\%"
for %%D in ("%TARGET%") do (
    if not exist "%%~dpD" mkdir "%%~dpD"
)

if exist "%TARGET%" (
    for /f "delims=" %%H in ('certutil -hashfile "%TARGET%" SHA256 2^>nul ^| findstr /r "^[0-9a-f]"') do set "LOCAL_HASH=%%H"
    set "LOCAL_HASH=!LOCAL_HASH: =!"
    if "!LOCAL_HASH!"=="%REMOTE_HASH%" (
        echo   %FILE_KEY% (unchanged)
        goto :eof
    )
)

set "TIMEOUT=30"
echo %FILE_KEY%| findstr /b "dist/" >nul && set "TIMEOUT=300"

curl -sS --max-time %TIMEOUT% -o "%TARGET%" "%URL%" 2>nul
if %ERRORLEVEL% neq 0 (
    echo   [X] %FILE_KEY% (download failed)
    set /a FAILED+=1
    goto :eof
)

for /f "delims=" %%H in ('certutil -hashfile "%TARGET%" SHA256 2^>nul ^| findstr /r "^[0-9a-f]"') do set "DL_HASH=%%H"
set "DL_HASH=!DL_HASH: =!"
if "!DL_HASH!"=="%REMOTE_HASH%" (
    echo   [OK] %FILE_KEY% (updated)
    set /a UPDATED+=1
) else (
    echo   [!] %FILE_KEY% (hash mismatch, skipped)
    set /a FAILED+=1
)
goto :eof

:update_config
set "CFG_KEY=%~1"
set "CFG_VAL=%~2"
if not exist "%USERPROFILE%\.openclaw-autoclaw" mkdir "%USERPROFILE%\.openclaw-autoclaw"
if exist "%CONFIG_FILE%" (
    python -c "import json; f=r'%CONFIG_FILE%'; c=json.load(open(f,encoding='utf-8')); c['%CFG_KEY%']='%CFG_VAL%'; json.dump(c,open(f,'w',encoding='utf-8'),indent=2,ensure_ascii=False)" 2>nul
) else (
    echo {"%CFG_KEY%": "%CFG_VAL%"} > "%CONFIG_FILE%"
)
goto :eof

:remove_config_key
set "CFG_KEY=%~1"
if exist "%CONFIG_FILE%" (
    python -c "import json; f=r'%CONFIG_FILE%'; c=json.load(open(f,encoding='utf-8')); c.pop('%CFG_KEY%',None); json.dump(c,open(f,'w',encoding='utf-8'),indent=2,ensure_ascii=False)" 2>nul
)
goto :eof

:show_help
echo Usage: %~nx0 [--check^|--force]
echo.
echo   (no args)    Check and update if new version available
echo   --check      Check only, do not update
echo   --force      Force update (ignore version check)
goto :eof
