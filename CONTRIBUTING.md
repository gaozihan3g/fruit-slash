# 参与贡献

感谢你愿意帮助改进 Fruit Slash。Bug 报告、玩法建议、文档修正和代码贡献都很欢迎。

## 提交 Issue

提交问题前，请先搜索现有 Issues，避免重复。一个有帮助的 Bug 报告应包含：

- 操作系统、CPU 架构和 Python 版本；
- 使用源码运行还是下载的 Release 版本；
- 可重复问题的最少步骤；
- 预期行为与实际行为；
- 相关错误信息、截图或短视频。

请勿在 Issue 中发布密码、令牌、私钥或其他敏感信息。

## 本地开发

1. Fork 本仓库并克隆你的 Fork。
2. 创建虚拟环境并安装依赖：

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   python3 -m pip install -r requirements.txt -r requirements-build.txt
   ```

3. 从最新的 `main` 创建用途明确的分支，例如 `feature/new-fruit` 或 `fix/collision-edge-case`。
4. 运行游戏并完成手动验证：

   ```bash
   python3 main.py
   ```

## 提交前检查

至少执行以下检查：

```bash
python3 -m compileall -q main.py fruit_slash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 main.py --smoke-test
```

涉及玩法或画面时，还应手动确认：

- 菜单可以开始游戏，`Enter` / `Space` 可以重新开始；
- 水果能被切开，连击、生命和炸弹规则正常；
- `Esc` 可以退出；
- 没有明显的掉帧、异常闪烁或控制台错误。

GitHub Actions 会在 Pull Request 中重新构建 Windows x64、macOS Intel、macOS Apple Silicon 和 Linux x64 四个平台。

## 代码与文档约定

- 遵循现有 Python 风格，优先使用清晰的类型标注和小型函数。
- 不要把生成的 `dist/`、`build/`、虚拟环境或本地最高分文件提交到仓库。
- 新功能应尽量保持项目“代码绘制、无外部素材包”的轻量特色；如确实需要新素材，请在 PR 中说明来源与许可证。
- 面向玩家的行为变化应同步更新 README；面向版本的重要变化应记录在 `CHANGELOG.md` 的 `Unreleased` 部分。
- 每个提交和 PR 尽量只解决一个主题，避免混入无关格式化。

## Pull Request

PR 描述应说明：

- 改了什么以及为什么；
- 玩家或开发者会受到什么影响；
- 如何验证；
- 相关 Issue（如有）；
- 画面变化的前后截图或短视频（如有）。

提交 PR 即表示你同意按照本项目的 [MIT License](LICENSE) 提供你的贡献。
