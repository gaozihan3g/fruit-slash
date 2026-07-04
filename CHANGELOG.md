# 更新日志

本文件记录 Fruit Slash 的重要变更。版本格式遵循[语义化版本](https://semver.org/lang/zh-CN/)，日志结构参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### 文档

- 扩展 README，增加游戏截图、功能列表、项目特色、目录结构与开发者说明。
- 新增贡献指南和版本更新日志。
- 完善 GitHub Release 的更新内容、下载说明与已知问题。

## [1.0.2] - 2026-07-04

### 新增

- 增加 macOS Apple Silicon（arm64）原生构建和下载包。
- 在自动构建中检查 macOS 可执行文件架构，避免上传错误架构的软件包。

### 变更

- 发布流程覆盖 Windows x64、macOS Intel、macOS Apple Silicon 和 Linux x64 四个平台。

## [1.0.1] - 2026-07-04

### 新增

- 增加 Windows x64、macOS Intel 和 Linux x64 的 GitHub Actions 自动构建。
- 为每个发布包生成 SHA-256 校验文件。
- 增加无窗口 smoke test，在发布前验证打包后的程序能够启动并运行游戏循环。
- 增加 PyInstaller 构建依赖。

### 修复

- 将最高分存储迁移到各操作系统的用户数据目录，使打包后的只读应用目录也能正常保存记录。

## [1.0.0] - 2026-07-04

### 新增

- 首次公开发布 Fruit Slash。
- 包含五种水果、炸弹、三颗生命、连击计分和动态难度。
- 包含水果分裂、刀光、粒子、闪光和屏幕震动效果。
- 提供菜单、游戏结束、最高分保存与中英文字体适配。
- 发布 GitHub Pages 项目介绍网站。
- 使用 MIT License 开源。

[Unreleased]: https://github.com/gaozihan3g/fruit-slash/compare/v1.0.2...HEAD
[1.0.2]: https://github.com/gaozihan3g/fruit-slash/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/gaozihan3g/fruit-slash/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/gaozihan3g/fruit-slash/releases/tag/v1.0.0
