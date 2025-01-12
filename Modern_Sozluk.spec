# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['dictionary_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('images/*', 'images/')],
    hiddenimports=['PyQt5.sip', 'deep_translator', 'requests', 'urllib3', 'anyio', 'beautifulsoup4', 'certifi', 'chardet', 'charset-normalizer', 'docx', 'et_xmlfile', 'googletrans', 'h11', 'h2', 'hpack', 'hstspreload', 'httpcore', 'httpx', 'hyperframe', 'idna', 'lxml', 'openpyxl', 'pandas', 'pillow', 'python-dateutil', 'python-docx', 'pytz', 'rfc3986', 'six', 'sniffio', 'soupsieve', 'typing_extensions', 'tzdata', 'urllib3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('O', None, 'OPTION'), ('O', None, 'OPTION')],
    name='Modern_Sozluk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['images\\dictionary_icon.ico'],
)
