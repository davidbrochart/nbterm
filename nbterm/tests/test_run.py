import os
import asyncio

from nbterm import Notebook


def test_run():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    nb_path = os.path.join(dir_path, "files", "original", "nb0.ipynb")
    nb_ref_path = os.path.join(dir_path, "files", "run", "nb0.ipynb")
    nb_save_path = os.path.join(dir_path, "files", "run", "nb0_run.ipynb")
    nb = Notebook(nb_path)
    asyncio.run(nb.run_all())
    nb.save(nb_save_path)
    with open(nb_ref_path) as f:
        nb_ref = f.read()
    with open(nb_save_path) as f:
        nb_run = f.read()
    assert nb_ref == nb_run
