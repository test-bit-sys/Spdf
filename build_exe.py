"""
Build script for Spdf using PyInstaller.
Packages the Python application into a standalone Windows executable.
"""

import sys
import os
import subprocess
import shutil

def build():
    print("=" * 60)
    print("Building Spdf Standalone Windows Executable")
    print("=" * 60)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    assets_dir = os.path.join(base_dir, "assets")
    icon_path = os.path.join(assets_dir, "app_icon.ico")

    # Command line arguments for PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name=Spdf",
        f"--icon={icon_path}",
        f"--add-data={assets_dir};assets",
        "--hidden-import=PySide6.QtSvg",
        "--hidden-import=PySide6.QtPrintSupport",
        "--hidden-import=fitz",
        "--hidden-import=PIL",
        os.path.join(base_dir, "main.py")
    ]

    print(f"Executing: {' '.join(cmd)}\n")
    ret = subprocess.call(cmd, cwd=base_dir)

    if ret == 0:
        exe_path = os.path.join(base_dir, "dist", "Spdf", "Spdf.exe")
        if not os.path.exists(exe_path):
            exe_path = os.path.join(base_dir, "dist", "Spdf.exe")
        print("\n" + "=" * 60)
        print(f"BUILD SUCCESSFUL!")
        print(f"Executable location: {exe_path}")
        print("=" * 60)
    else:
        print("\nBUILD FAILED with return code:", ret)
        sys.exit(ret)

if __name__ == "__main__":
    build()
