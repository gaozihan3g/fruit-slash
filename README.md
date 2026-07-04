# 水果快斩（Fruit Slash）

一个使用 Python 和 Pygame 编写的水果切割小游戏。美术、粒子和动画均由代码绘制，不需要额外素材。

🌐 [查看在线作品介绍](https://gaozihan3g.github.io/fruit-slash/)

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

最高分会自动保存在同目录下的 `highscore.txt` 中。
