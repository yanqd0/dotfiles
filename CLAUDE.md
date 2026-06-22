# 项目：dotfiles

## 跨平台策略

三个平台目录：`Linux/`、`MacOSX/`、`Windows/`。

**权威存放规则：**
- 文件同时存在于 Windows → 实体文件放 `Windows/`，`Linux/` 和 `MacOSX/` 用相对软链接指向它。
- 文件仅在 Linux 和 Mac 之间共享（Windows 没有）→ 实体文件放其中一者，另一者用相对软链接指向它（方向因文件而异，以 README.md 清单为准）。
- 平台专属文件 → 各自目录下保留实体文件。

**原因：** Windows 不支持软链接，实体文件必须放在那边。Linux 和 macOS 可以透明跟随软链接链。

**操作指引：** 新增或修改文件时，查阅 README.md 中的文件清单表格并同步更新。用 `install.py --test` 验证三个 OS 模式均通过。

## install.py

### `--revert` 强约束

`_revert` **只删除软链接，永远不删除真实文件或真实目录**。

判别逻辑（任一命中即删除）：

| 对象 | 条件 | 说明 |
|------|------|------|
| 目录软链接 | `resolve()` 落在项目仓库内 | 遗留的目录级安装产物（如 `~/.config/nvim` → `Linux/.config/nvim`） |
| 目录软链接 | target 字符串包含 `src_dir` 路径 | 兜底匹配 |
| 文件软链接 | target 字符串包含 `src_dir` 路径 | 由 `install` 创建的或孤立的项目软链接 |

**绝不删除：**
- 真实文件（`is_symlink() == False`）
- 真实目录（`is_symlink() == False`）
- target 不包含项目路径的软链接（即使已断裂）
- 解析后落在项目仓库内的文件软链接（`followlinks=False` 确保 `os.walk` 不会通过目录软链接进入项目）

**遍历安全：** 使用 `os.walk(dst_root, followlinks=False)`，不跟随目录软链接，避免进入项目树导致死循环或误改项目文件。

## README.md

包含文件清单表格。新增、移动或删除文件时必须同步更新。
