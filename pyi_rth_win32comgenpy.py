# pyi_rth_win32comgenpy.py

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


