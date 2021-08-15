import os
import shutil
from pathlib import Path

import pytest


HERE = Path(__file__).resolve().parent
TMP_DIR = HERE / "files" / "tmp"


@pytest.fixture
def files():
    return HERE / "files"


@pytest.fixture
def tmp_dir():
    return TMP_DIR


shutil.rmtree(TMP_DIR, ignore_errors=True)
os.makedirs(TMP_DIR, exist_ok=True)
