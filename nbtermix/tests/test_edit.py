from nbterm import Notebook


def test_edit0(files):
    nb_path = files / "original" / "nb0.ipynb"
    nb_ref_path = files / "edited" / "nb0.ipynb"
    nb_save_path = files / "edited" / "nb0_edited0.ipynb"
    nb = Notebook(nb_path, no_kernel=True)
    nb.move_down()
    nb.go_down()
    nb.move_up()
    nb.save(nb_save_path)
    nb_ref = nb_ref_path.read_text()
    nb_edited = nb_save_path.read_text()
    assert nb_ref == nb_edited


def test_edit1(files):
    nb_path = files / "original" / "nb0.ipynb"
    nb_ref_path = files / "edited" / "nb0.ipynb"
    nb_save_path = files / "edited" / "nb0_edited1.ipynb"
    nb = Notebook(nb_path, no_kernel=True)
    nb.cut_cell(0)
    nb.paste_cell(2)
    nb.save(nb_save_path)
    nb_ref = nb_ref_path.read_text()
    nb_edited = nb_save_path.read_text()
    assert nb_ref == nb_edited
