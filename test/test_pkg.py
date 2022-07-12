import nuventure


nuventure.DEBUG_MODE = True

def test_dbg_print(capsys):
    nuventure.dbg_print(nuventure.func_name(), "testing")
    output = capsys.readouterr().out
    assert output == "test_dbg_print: testing\n"
