import neovim


@neovim.plugin
class FloateryPlugin:
    default_size = ['70 80']
    size_percent = {}

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
            if self.floatingWindow is not None:
                self._unfloat_it()
                return
            arg = self.default_size
        self.log(repr(arg))

        if self.size_percent:
            width_percent = self.size_percent['width']
            height_percent = self.size_percent['height']
        else:
            width_percent, height_percent = [int(i) for i in arg[0].split()]

        self._update_config(width_percent, height_percent)
        if self.floatingWindow is None:
            self._open_floating_window()
        else:
            self._update_floating_window()

        self.size_percent = {
            'width': width_percent,
            'height': height_percent
        }
        self.reopen_buffer = self.nvim.eval(f'winbufnr({self.floatingWindow})')

    def _unfloat_it(self):
        buffer_value = self.nvim.eval(f'winbufnr({self.floatingWindow})')
        if buffer_value > 0:
            self.reopen_buffer = buffer_value
        try:
            self.nvim.command_output(
                f'call nvim_win_close({self.floatingWindow}, 0)')
        except Exception:
            pass
        self.floatingWindow = None

    def _update_config(self, width_percent, height_percent):
        width_editor = self.nvim.eval('&columns')
        height_editor = self.nvim.eval('&lines')

        self.floatingWindowConfig['width'] = int(
            width_percent * width_editor / 100)
        self.floatingWindowConfig['height'] = int(
            height_percent * height_editor / 100)

        col = int((width_editor - self.floatingWindowConfig['width']) / 2)
        row = int((height_editor - self.floatingWindowConfig['height']) / 2)

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
