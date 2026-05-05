@echo off
REM Build script for Vidown Windows

setlocal enabledelayedexpansion

set APP_NAME=vidown
set DIST_DIR=dist

echo Building Vidown for Windows...

REM Clean previous build
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"

REM Run PyInstaller
pyinstaller "%APP_NAME%.spec" --distpath "%DIST_DIR%" --workpath "%DIST_DIR%\build"

REM Create ffmpeg folder in dist
if not exist "%DIST_DIR%\vidown\ffmpeg" mkdir "%DIST_DIR%\vidown\ffmpeg"

echo Build complete: %DIST_DIR%\vidown\

endlocal