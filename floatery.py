import neovim


@neovim.plugin
class FloateryPlugin:
    default_size = ['90 40']

    def __init__(self, nvim):
        self.nvim = nvim
        self.floatingWindow = None
        self.reopen_buffer = None
        self.buffer = None
        self.floatingWindowConfig = {
            'relative': 'editor',
            'width': 50,
            'height': 30,
            'col': 0,
            'row': 0,
            'anchor': 'NW'
        }

    def log(self, message):
        self.nvim.command(f'echom "{message}"')

    @neovim.command('FloatIt', nargs='?')
    def float_it(self, arg):
        if not arg:
            arg = self.default_size

        width, height = [int(i) for i in arg[0].split()]

        self._update_config(width, height)
        if self.floatingWindow is None:
            self._open_floating_window()
        else:
            self._update_floating_window()

        self.reopen_buffer = self.nvim.eval(f'winbufnr({self.floatingWindow})')

    @neovim.command('UnFloatIt')
    def unfloat_it(self):
        self.nvim.command_output(
            f'call nvim_win_close({self.floatingWindow}, 0)')
        self.floatingWindow = None

    def _update_config(self, width, height):
        width_editor = self.nvim.eval('&columns')
        height_editor = self.nvim.eval('&lines')

        self.floatingWindowConfig['width'] = width
        self.floatingWindowConfig['height'] = height

        col = (width_editor - self.floatingWindowConfig['width']) / 2
        row = (height_editor - self.floatingWindowConfig['height']) / 2

        self.floatingWindowConfig.update({'col': col, 'row': row})

    def _open_floating_window(self):
        self.buffer = self.reopen_buffer
        if self.buffer is None:
            self.buffer = self.nvim.current.buffer.number

        options = self.floatingWindowConfig
        try:
            self.floatingWindow = self.nvim.eval(
                f'nvim_open_win({self.buffer}, 1, {options})'
            )
        except Exception:
            self.buffer = None
            self._open_floating_window()

    def _update_floating_window(self):
        options = self.floatingWindowConfig
        window = self.floatingWindow
        try:
            self.nvim.eval(
                f'nvim_win_set_config({window}, {options})'
            )
        except neovim.api.nvim.NvimError:
            # ugly workaround, should just check if the damn window exists)
            self._open_floating_window()
