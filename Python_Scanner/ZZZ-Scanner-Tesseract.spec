# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\samsaq\\Documents\\GitHub\\ZZZ-Drive-Disk-Scanner\\Python_Scanner\\orchestrator.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\samsaq\\Documents\\GitHub\\ZZZ-Drive-Disk-Scanner\\Python_Scanner\\Target_Images', 'Target_Images/')],
    hiddenimports=['PyTessBaseAPI'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZZZ-Scanner-Tesseract',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\samsaq\\Documents\\GitHub\\ZZZ-Drive-Disk-Scanner\\ZZZ-Frontend\\renderer\\public\\images\\ZZZ-Scanner-Icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZZZ-Scanner-Tesseract',
)
