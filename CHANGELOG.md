# Change Log

## 0.1.0

### Features

- 新增 `install.py` 自动化安装脚本，支持多 OS 自动检测、`--root`/`--test`/`--revert` 参数。
- 建立跨平台策略：`Windows/` 为共享配置文件权威源，`Linux/` 与 `MacOSX/` 通过相对软链接引用。
- 新增 `README.md` 文件清单表格，记录三平台所有文件的本体与软链接关系。
- 新增 `CLAUDE.md` 项目文档，记录跨平台策略与文件同步规范。
- 新增配置文件：`.gemrc`、`.npmrc`、`.pip/pip.conf`、`.isort.cfg`、`.cargo/config.toml`、yapf `style`。
- 新增 Shell 与终端配置：`.tmux.conf`、`.tmux.remote.conf`、`.inputrc`、`.ideavimrc`、powerline 主题。
- 新增 Neovim `init.vim` 引导配置。
- 新增 IPython 集成 powerline 的 `ipython_config.py`。

### Bug Fixes

- 修复 `install.py` 中 `rglob` 不跟随目录软链接导致遗漏文件的问题，改用 `os.walk(followlinks=True)`。
- 修复新版 bash 下 powerline shell UI 兼容性。
- 修复 `pip.ini` 中 `index-url` 格式。
- 修复 `$HOME` 路径解析问题。

### Others

- 将 `.cargo/`、`.config/` 迁移至 `Windows/` 目录，统一跨平台文件管理。
- 调整 powerline 分段显示与 tmux 按键映射。
- 删除已停止维护的 vimperator 配置。
- 初始化仓库结构（`.gitignore`、`README`）。
