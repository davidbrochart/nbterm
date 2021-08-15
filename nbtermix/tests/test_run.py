import asyncio

from nbterm import Notebook


def test_run(files):
    nb_path = files / "original" / "nb0.ipynb"
    nb_ref_path = files / "run" / "nb0.ipynb"
    nb_save_path = files / "run" / "nb0_run.ipynb"
    nb = Notebook(nb_path)
    asyncio.run(nb.run_all())
    nb.save(nb_save_path)
    nb_ref = nb_ref_path.read_text()
    nb_run = nb_save_path.read_text()
    assert nb_ref == nb_run
