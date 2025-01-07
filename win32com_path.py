# win32com_path.py

import sys
import os
import win32com

# win32com モジュールのディレクトリを取得
win32com_dir = os.path.dirname(win32com.__file__)

print("win32com_dir", win32com_dir)


# sys.path に追加
sys.path.append(win32com_dir)

