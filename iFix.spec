# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('logo.png', '.'), ('data\\ifix.db', 'data')],
    hiddenimports=['pages.dashboard', 'pages.vendas', 'pages.clientes', 'pages.tecnicos', 'pages.garantia', 'pages.laboratorio', 'pages.catalogo', 'component.sidebar', 'component.vizualizarcliente', 'component.ordemdeservi├ºo', 'component.novavenda', 'component.novocliente', 'component.novotecnico', 'component.notas'],
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
    name='iFix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='iFix',
)
