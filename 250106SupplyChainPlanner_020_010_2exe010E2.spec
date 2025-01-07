#pyinstaller 250106SupplyChainPlanner_020_010_2exe010D2.spec


import sys
import os
import win32com
import pythoncom
import pywintypes

gen_py_folder = os.path.join(os.path.dirname(win32com.__file__), 'gen_py')

print("gen_py_folder",gen_py_folder)

if not os.path.exists(gen_py_folder):
    os.mkdir(gen_py_folder)

# win32com モジュールのディレクトリを取得
win32com_dir = os.path.dirname(win32com.__file__)

print("win32com_dir",win32com_dir)

# sys.path に追加
sys.path.append(win32com_dir)




import win32com.client

# gen_pyフォルダを初期化するためのCOMオブジェクトのインスタンス化
shell = win32com.client.Dispatch("WScript.Shell")










# pyinstaller 250106SupplyChainPlanner_020_010_2exe010E.spec

# .spec ファイルのトップに追加
from PyInstaller.utils.hooks import collect_submodules, copy_metadata

hiddenimports = collect_submodules('win32com') + ['pythoncom', 'pywintypes', 'win32com.gen_py', 'pywin32_system32']

datas = copy_metadata('pywin32') + [(r'C:\Users\ohsug\anaconda3\lib\site-packages\win32com\gen_py', 'win32com/gen_py')]

binaries = [(r'C:\Users\ohsug\anaconda3\lib\site-packages\pywin32_system32\pythoncom39.dll', '.')]

a = Analysis(['250106SupplyChainPlanner_020_010_2exe010.py'],
             pathex=[r'C:\Users\ohsug\@@@matplotlib_test\@github2501_exe2'],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[r'C:\Users\ohsug\hooks'],
             runtime_hooks=[r'C:\Users\ohsug\hooks\pyi_rth_win32comgenpy.py'],
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
