# -*- mode: python ; coding: utf-8 -*-

datas = [('assets', 'assets')]
binaries = []
hiddenimports = [
    'automata',
    'automata.fa',
    'automata.fa.dfa',
    'automata.fa.fa',
    'automata.pda',
    'automata.pda.pda',
    'automata.pda.dpda',
    'automata.pda.configuration',
    'automata.pda.stack',
    'automata.base',
    'automata.base.automaton',
    'automata.base.exceptions',
    'automata.base.utils',
    'cached_method',
    'typing_extensions',
    'pygame',
    'numpy',
    'PIL',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'sympy',
        'manim',
        'manimpango',
        'pygraphviz',
        'coloraide',
        'IPython',
        'tkinter',
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Memotest_FTI',
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
    icon=['assets/icon.ico'],
)
