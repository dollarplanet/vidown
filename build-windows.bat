@echo off
REM Build script for Vidown Windows

setlocal enabledelayedexpansion

set APP_NAME=vidown
set DIST_DIR=dist

echo Building Vidown for Windows...

REM Clean previous build
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"

REM Create spec file
(
echo # -*- mode: python ; coding: utf-8 -*-
echo block_cipher = None
echo.
echo a = Analysis(
echo     ['main.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=['PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'yt_dlp'],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=None,
echo     noarchive=False,
echo )
echo.
echo pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
echo.
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     [],
echo     exclude_binaries=True,
echo     name='vidown',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo )
echo.
echo coll = COLLECT(
echo     exe,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     name='vidown',
echo )
echo.
echo import os
echo ffmpeg_dir = os.path.join('dist', 'vidown', 'ffmpeg')
echo os.makedirs(ffmpeg_dir, exist_ok=True)
echo print(f"Created ffmpeg folder: {ffmpeg_dir}")
) > "%APP_NAME%.spec"

REM Run PyInstaller
pyinstaller "%APP_NAME%.spec" --distpath "%DIST_DIR%" --workpath "%DIST_DIR%\build"

REM Create ffmpeg folder in dist
if not exist "%DIST_DIR%\vidown\ffmpeg" mkdir "%DIST_DIR%\vidown\ffmpeg"

echo Build complete: %DIST_DIR%\vidown\

endlocal