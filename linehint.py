import neovim

# call nvim_buf_set_virtual_text(0, -1, 10, [['test', 'NonText']], {})


@neovim.plugin
class LinehintPlugin:
    hg_group = 'NonText'

    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.command('LineHint', nargs='?')
    def line_hist(self, arg):
        if arg:
            message = arg[0]
        else:
            message = ''

        _lineno = int(self.nvim.command_output("echo line('.')")) - 1

        self.nvim.command_output(
            f"call nvim_buf_set_virtual_text(0, -1, {_lineno}, [['{message}',"
            f"'{self.hg_group}']], {{}})"
        )
