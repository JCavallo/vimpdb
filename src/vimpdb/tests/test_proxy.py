import os


def test_ProxyToVim_instantiation():
    from vimpdb.proxy import ProxyToVim
    from vimpdb.config import Config
    configuration = Config('vim_client_script', 'vim_server_script',
        'server_name', 6666)
    to_vim = ProxyToVim(configuration)
    assert isinstance(to_vim, ProxyToVim)


def test_ProxyToVim_setupRemote():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_FALSE)
    to_vim.setupRemote()
    lines = to_vim.logged().splitlines()
    assert len(lines) == 7
    assert lines[1] == "expr: exists('*PDB_setup_egg')"
    assert lines[2] == "return: '0'"
    assert lines[3].startswith('send: <C-\\><C-N>:source ')
    assert lines[3].endswith('vimpdb/vimpdb.vim<CR>')
    assert lines[4].startswith('send: :call PDB_setup_egg(')
    assert lines[5].startswith('send: :call PDB_setup_egg(')
    assert lines[6].startswith('send: :call PDB_init_controller(')


def test_ProxyToVim_setupRemote_does_nothing():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_TRUE)
    to_vim.setupRemote()
    assert (to_vim.logged() ==
"""
expr: exists('*PDB_setup_egg')
return: '1'
""")


def test_ProxyToVim_isRemoteSetup():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.isRemoteSetup()
    assert (to_vim.logged() ==
"""
expr: exists('*PDB_setup_egg')
return: None
""")


def test_ProxyToVim_showFeedback_empty():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_TRUE)
    to_vim.showFeedback('')
    assert (to_vim.logged() ==
"""
""")


def test_ProxyToVim_showFeedback_content():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_TRUE)
    to_vim.showFeedback('first\nsecond')
    assert (to_vim.logged() ==
"""
expr: exists('*PDB_setup_egg')
return: '1'
send: :call PDB_show_feedback(['first', 'second'])<CR>
""")


def test_ProxyToVim_showFileAtLine_wrong_file():
    from vimpdb.testing import ProxyToVimForTests
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_TRUE)
    to_vim.showFileAtLine('bla.vim', 1)
    assert (to_vim.logged() ==
"""
""")


def test_ProxyToVim_showFileAtLine_existing_file():
    from vimpdb.testing import ProxyToVimForTests
    from vimpdb.config import get_package_path
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_TRUE)
    existingFile = get_package_path(
        test_ProxyToVim_showFileAtLine_existing_file)
    to_vim.showFileAtLine(existingFile, 1)
    lines = to_vim.logged().splitlines()
    assert len(lines) == 4
    assert lines[1] == "expr: exists('*PDB_setup_egg')"
    assert lines[2] == "return: '1'"
    assert lines[3].startswith('send: :call PDB_show_file_at_line("')
    assert lines[3].endswith(' "1")<CR>')
    assert not '\\' in lines[3]


def test_ProxyToVim_showFileAtLine_existing_file_windows():
    from vimpdb.testing import ProxyToVimForTests
    from vimpdb.config import get_package_path
    to_vim = ProxyToVimForTests()
    to_vim.setState(to_vim.IS_REMOTE_SETUP_IS_TRUE)
    existingFile = get_package_path(
        test_ProxyToVim_showFileAtLine_existing_file)
    existingFile = existingFile.replace(os.sep, '\\')
    to_vim._showFileAtLine(existingFile, 1)
    lines = to_vim.logged().splitlines()
    assert len(lines) == 4
    assert lines[1] == "expr: exists('*PDB_setup_egg')"
    assert lines[2] == "return: '1'"
    assert lines[3].startswith('send: :call PDB_show_file_at_line("')
    assert lines[3].endswith(' "1")<CR>')
    assert not '\\' in lines[3]


def test_ProxyFromVim_instantiation():
    from vimpdb.proxy import ProxyFromVim
    from vimpdb.config import Config
    configuration = Config('vim_client_script', 'vim_server_script',
        'server_name', 6666)
    from_vim = ProxyFromVim(configuration)
    assert isinstance(from_vim, ProxyFromVim)
