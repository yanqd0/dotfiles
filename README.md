# dotfiles

![progress](http://progressed.io/bar/20?title=developing)

## Description

This project holds my personal dot files.

It's not recommended to use it directly.

## File inventory

**本体** = real file &nbsp;|&nbsp; *→ X* = symlink to X &nbsp;|&nbsp; — = not present

| $HOME 路径 | Linux | MacOSX | Windows |
|---|---|---|---|
| `.cargo/config.toml` | *→ Windows* | *→ Windows* | **本体** |
| `.config/nvim/init.vim` | **本体** | *→ Linux* | — |
| `.config/powerline/themes/shell/default.json` | **本体** | *→ Linux* | — |
| `.config/powerline/themes/tmux/default.json` | **本体** | *→ Linux* | — |
| `.config/yapf/style` | **本体** | *→ Linux* | — |
| `.gemrc` | *→ MacOSX* | **本体** | — |
| `.ideavimrc` | *→ MacOSX* | **本体** | — |
| `.inputrc` | *→ MacOSX* | **本体** | — |
| `.ipython/profile_default/ipython_config.py` | **本体** | *→ Linux* | — |
| `.npmrc` | *→ Windows* | *→ Windows* | **本体** |
| `.pip/pip.conf` | *→ Windows* | *→ Windows* | — |
| `.tmux.conf` | **本体** | *→ Linux* | — |
| `.tmux.remote.conf` | **本体** | — | — |
| `.vimperatorrc.local` | **本体** | **本体** | — |
| `_vimperatorrc.local` | — | — | **本体** |
| `pip/pip.ini` | — | — | **本体** |

## Strategy

- **Windows/** holds the canonical copy of any file that also exists on Windows, because Windows does not support symlinks.
- **Linux/** and **MacOSX/** share files via relative symlinks — across each other and to Windows/.
- Platform-specific files (different content or different paths) stay as real files in their own directories.
- When adding or removing files, keep this table and the symlinks in sync.

## Installation

```bash
./install.py         # auto-detect OS
./install.py --os MacOSX   # override
./install.py --test        # dry-run to /tmp
./install.py --revert      # remove installed symlinks
```

## License

[![Unlicense](https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/PD-icon.svg/120px-PD-icon.svg.png)](https://commons.wikimedia.org/wiki/File:PD-icon.svg)

This project is under the term of the **Unlicense**.

> This is free and unencumbered software released into the public domain.
>
> see: <http://unlicense.org>
