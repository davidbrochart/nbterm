import os
import asyncio
from pathlib import Path

from nbterm import Notebook


def test_run():
    dir_path = Path(__file__).parent
    nb_path = dir_path/"files"/"original"/ "nb0.ipynb"
    nb_ref_path = dir_path/ "files"/ "run"/ "nb0.ipynb"
    nb_save_path =dir_path/ "files"/ "run"/ "nb0_run.ipynb"

    nb = Notebook(nb_path)
    asyncio.run(nb.run_all())
    nb.save(nb_save_path)

    nb_ref = nb_ref_path.read_text()
    nb_run = nb_save_path.read_text()

    assert nb_ref == nb_run
