# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

yt_modules = collect_submodules('yt_dlp')

tkinter_modules = [
    'tkinter',
    'tkinter.__init__',
    'tkinter._fix',
    'tkinter.colorchooser',
    'tkinter.commondialog',
    'tkinter.dialog',
    'tkinter.dnd',
    'tkinter.filedialog',
    'tkinter.font',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'tkinter.simpledialog',
    'tkinter.tix',
    'tkinter.ttk',
    'tkinter.tksimplebeg',
]

try:
    import tkinter
    tk_modules = collect_submodules('tkinter')
    for mod in tk_modules:
        if mod not in tkinter_modules:
            tkinter_modules.append(mod)
except Exception:
    pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('vidown.png', '.'),
        ('vidown.desktop', '.'),
    ] + collect_data_files('yt_dlp'),
    hiddenimports=yt_modules + tkinter_modules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='vidown',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='vidown.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='vidown',
)