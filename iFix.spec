# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=[('logo.ico', '.'), ('logo.png', '.'), ('data\\ifix.db', 'data'), ('svg', 'svg')],
<<<<<<< HEAD
    hiddenimports=['data.database', 'pages.dashboard', 'pages.vendas', 'pages.clientes', 'pages.tecnicos', 'pages.garantia', 'pages.laboratorio', 'pages.catalogo', 'component.sidebar', 'component.base_dialog', 'component.svg_utils', 'component.vizualizarcliente', 'component.novocliente', 'component.novotecnico', 'component.novoproduto', 'component.novocelular', 'component.novavenda', 'component.novaentrega', 'component.novocancelamento', 'component.ordemdeservico', 'component.notas', 'component.whatsapp'],
=======
    hiddenimports=['pages.dashboard', 'pages.vendas', 'pages.clientes', 'pages.tecnicos', 'pages.garantia', 'pages.laboratorio', 'pages.catalogo', 'component.sidebar', 'component.vizualizarcliente', 'component.ordemdeservico', 'component.novavenda', 'component.novocliente', 'component.novotecnico', 'component.notas'],
>>>>>>> b6f2f56ac648032dd220690badbd92cfa8b1673a
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
