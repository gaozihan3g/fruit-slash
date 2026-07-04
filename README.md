# 水果快斩（Fruit Slash）

一个使用 Python 和 Pygame 编写的水果切割小游戏。美术、粒子和动画均由代码绘制，不需要额外素材。

🌐 [查看在线作品介绍](https://gaozihan3g.github.io/fruit-slash/)

## 下载

- [Windows x64](https://github.com/gaozihan3g/fruit-slash/releases/latest/download/Fruit-Slash-Windows-x64.zip)
- [macOS Apple Silicon](https://github.com/gaozihan3g/fruit-slash/releases/latest/download/Fruit-Slash-macOS-Apple-Silicon.zip)（Apple M 系列芯片）
- [macOS Intel](https://github.com/gaozihan3g/fruit-slash/releases/latest/download/Fruit-Slash-macOS-Intel.zip)
- [Linux x64](https://github.com/gaozihan3g/fruit-slash/releases/latest/download/Fruit-Slash-Linux-x64.tar.gz)

当前发布包未使用商业开发者证书签名，因此 Windows SmartScreen 或 macOS Gatekeeper 可能在首次运行时显示安全提示。

## 运行

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

## 操作

- 按住鼠标左键并快速划过水果：切开水果并得分
- 连续快速切中水果：获得连击加分
- 漏掉水果：损失一颗生命，共三颗
- 切到炸弹：立即结束本局
- `Enter` / `Space`：开始或重新开始
- `Esc`：退出

最高分会自动保存在当前系统的用户数据目录中。
