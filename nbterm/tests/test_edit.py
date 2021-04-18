import os

from nbterm import Notebook


def test_edit():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    nb_path = os.path.join(dir_path, "files", "original", "nb0.ipynb")
    nb_ref_path = os.path.join(dir_path, "files", "edited", "nb0.ipynb")
    nb_save_path = os.path.join(dir_path, "files", "edited", "nb0_edited.ipynb")
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
