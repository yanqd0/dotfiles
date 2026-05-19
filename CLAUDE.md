# 项目：dotfiles

## 跨平台策略

三个平台目录：`Linux/`、`MacOSX/`、`Windows/`。

**权威存放规则：**
- 文件同时存在于 Windows → 实体文件放 `Windows/`，`Linux/` 和 `MacOSX/` 用相对软链接指向它。
- 文件仅在 Linux 和 Mac 之间共享（Windows 没有）→ 实体文件放其中一者，另一者用相对软链接指向它（方向因文件而异，以 README.md 清单为准）。
- 平台专属文件 → 各自目录下保留实体文件。

**原因：** Windows 不支持软链接，实体文件必须放在那边。Linux 和 macOS 可以透明跟随软链接链。

**操作指引：** 新增或修改文件时，查阅 README.md 中的文件清单表格并同步更新。用 `install.py --test` 验证三个 OS 模式均通过。

## README.md

包含文件清单表格。新增、移动或删除文件时必须同步更新。
