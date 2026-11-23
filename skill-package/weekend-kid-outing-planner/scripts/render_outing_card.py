#!/usr/bin/env python3
"""把一条遛娃方案渲染成 1080x1440 竖版 PNG 卡片。

用法：
  python3 render_outing_card.py plan.json [--out card.png]

plan.json 结构见 references/card-json-schema.md。
依赖：Pillow（pip install pillow）。无网络、无外部 API。
"""
import argparse
import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("需要 Pillow：pip install pillow")

W, H = 1080, 1440

FONT_CANDIDATES = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]


def pick_font():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    sys.exit("未找到中文字体；请安装 Noto Sans CJK 或修改 FONT_CANDIDATES")


FONT_PATH = pick_font()
_font_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_PATH, size, index=1 if bold else 0)
    return _font_cache[key]


def fit(draw, text, f, max_w):
    """缩字号直到文本宽度不超限，返回 (字体, 文本)。"""
    while draw.textlength(text, font=f) > max_w and f.size > 20:
        f = font(f.size - 4, bold=False)
    return f, text


def center(draw, box, text, f, fill):
    l, t, r, b = box
    bb = draw.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = l + (r - l - tw) // 2 - bb[0]
    y = t + (b - t - th) // 2 - bb[1]
    draw.text((x, y), text, font=f, fill=fill)


def color(d, fallback):
    v = d or fallback
    v = v.lstrip("#")
    return "#" + v


def render(plan, out):
    img = Image.new("RGB", (W, H), color(plan.get("bg"), "#F7F5EF"))
    dr = ImageDraw.Draw(img)
    ink = color(plan.get("ink"), "#2C2C2A")
    muted = color(plan.get("muted"), "#5F5E5A")

    dr.rounded_rectangle((60, 70, 1020, 1370), radius=48, fill="#FFFFFF",
                         outline="#D3D1C7", width=2)

    # 顶部：方案序号
    dr.rounded_rectangle((110, 130, 420, 200), radius=35, fill="#E1F5EE")
    center(dr, (110, 130, 420, 200), plan.get("label", "方案 1"),
           font(36, True), "#0F6E56")

    # 标题 + 适配度徽章
    title = str(plan.get("title", "未命名方案"))
    tf = fit(dr, title, font(62, True), 630)[0]
    dr.text((110, 240), title, font=tf, fill=ink)
    score = plan.get("score")
    if score is not None:
        dr.rounded_rectangle((780, 245, 970, 315), radius=35, fill="#085041")
        center(dr, (780, 245, 970, 315), f"适配 {score}", font(34, True), "#E1F5EE")

    # 副信息（最多两行）
    y = 350
    for line in plan.get("meta", [])[:2]:
        dr.text((110, y), line, font=font(32), fill=muted)
        y += 55

    dr.line((110, 490, 970, 490), fill="#D3D1C7", width=2)

    # 时间线（最多 5 条）
    y = 550
    for time, desc in plan.get("timeline", [])[:5]:
        dr.ellipse((112, y + 6, 136, y + 30), fill="#7F77DD")
        dr.text((170, y), time, font=font(34, True), fill="#3C3489")
        df = fit(dr, desc, font(34), 620)[0]
        dr.text((330, y), desc, font=df, fill=ink)
        y += 110

    dr.line((110, 990, 970, 990), fill="#D3D1C7", width=2)

    # 标签（最多 3 个）
    for i, label in enumerate(plan.get("tags", [])[:3]):
        x = 110 + i * 295
        dr.rounded_rectangle((x, 1040, x + 270, 1110), radius=30, fill="#E6F1FB")
        lf = fit(dr, label, font(30), 240)[0]
        center(dr, (x, 1040, x + 270, 1110), label, lf, "#185FA5")

    # 亮点 / 注意（各一行）
    notes = plan.get("notes", {})
    dr.rounded_rectangle((110, 1170, 970, 1310), radius=30, fill="#FAEEDA")
    ny = 1195
    for key in ("highlight", "caution"):
        if key in notes:
            line = f"{'亮点' if key == 'highlight' else '注意'}：{notes[key]}"
            nf = fit(dr, line, font(30), 800)[0]
            dr.text((140, ny), line, font=nf, fill="#854F0B")
            ny += 50

    img.save(out, quality=95)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", help="方案 JSON 文件路径")
    ap.add_argument("--out", default="outing-card.png")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    if isinstance(plan, list):
        plan = plan[0]
    out = render(plan, Path(args.out))
    print(f"卡片已生成：{out} ({Image.open(out).size[0]}x{Image.open(out).size[1]})")


if __name__ == "__main__":
    main()
