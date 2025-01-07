# pyinstaller 250106SupplyChainPlanner_020_010_2exe010C.spec


# .spec ファイルのトップに追加
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

hiddenimports = collect_submodules('win32com') + ['pythoncom', 'pywintypes', 'win32com.gen_py', 'pywin32_system32']

datas = copy_metadata('pywin32')


a = Analysis(['250106SupplyChainPlanner_020_010_2exe010.py'],
             pathex=[r'C:\Users\ohsug\@@@matplotlib_test\@github2501_exe2'],
             binaries=[],
             datas=datas,
             hiddenimports=hiddenimports,

             hookspath=[],
             runtime_hooks=[], 

             #hookspath=[r'C:\Users\ohsug\hooks'],
             #runtime_hooks=[r'C:\Users\ohsug\hooks\pyi_rth_win32comgenpy.py'],

             excludes=['PyQt5'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='250106SupplyChainPlanner_020_010_2exe010',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='250106SupplyChainPlanner_020_010_2exe010')


