from __future__ import annotations
from pathlib import Path
from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
import shutil

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "contract"

class build_py(_build_py):
    def run(self):
        target = Path(self.build_lib) / "tigr_contract_artifacts" / "_contract"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(SRC, target)
        super().run()

setup(cmdclass={"build_py": build_py})
