import os

from nbterm import Notebook


def test_edit0():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    nb_path = os.path.join(dir_path, "files", "original", "nb0.ipynb")
    nb_ref_path = os.path.join(dir_path, "files", "edited", "nb0.ipynb")
    nb_save_path = os.path.join(dir_path, "files", "edited", "nb0_edited0.ipynb")
    nb = Notebook(nb_path, no_kernel=True)
    nb.move_down()
    nb.go_down()
    nb.move_up()
    nb.save(nb_save_path)
    with open(nb_ref_path) as f:
        nb_ref = f.read()
    with open(nb_save_path) as f:
        nb_edited = f.read()
    assert nb_ref == nb_edited


def test_edit1():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    nb_path = os.path.join(dir_path, "files", "original", "nb0.ipynb")
    nb_ref_path = os.path.join(dir_path, "files", "edited", "nb0.ipynb")
    nb_save_path = os.path.join(dir_path, "files", "edited", "nb0_edited1.ipynb")
    nb = Notebook(nb_path, no_kernel=True)
    nb.cut_cell(0)
    nb.paste_cell(2)
    nb.save(nb_save_path)
    with open(nb_ref_path) as f:
        nb_ref = f.read()
    with open(nb_save_path) as f:
        nb_edited = f.read()
    assert nb_ref == nb_edited
