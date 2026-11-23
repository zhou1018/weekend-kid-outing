---
name: weekend-kid-outing-planner
display_name: 周末遛娃规划通
display_name_en: Weekend Kid Outing Planner
description: "亲子周末出行规划助手。家长填写家庭档案（城市、孩子年龄、预算、交通、偏好）后，每次说「这周带娃去哪」，自动联网检索近期真实的亲子户外攻略与活动信息，核验时效，按天气、年龄适配、距离、预算综合评分排序，输出 3-5 个带真实来源链接的个性化方案和可勾选打卡的行程卡，并自动附雨天高温备选。适用于：这周带娃去哪、周末遛娃、亲子户外推荐、附近适合孩子的地方、给孩子安排活动、下雨天带娃去哪。触发词：遛娃、带娃、亲子、周末去哪、户外。"
description_zh: "亲子周末出行规划助手。首次使用自动采集家庭档案（城市、孩子年龄、预算、交通方式、偏好类型），之后每次问「这周带娃去哪」，实时联网检索该城市近期真实的亲子户外攻略、场馆活动与免费资源，逐条核验时效（超过 3 个月的信息不单独采信），按天气适配、年龄适配、距离通勤、预算、时效五个维度加权评分，输出 Top 3-5 个方案，每个方案含关键信息表、亮点、注意事项、真实可点击的来源链接、可勾选打卡的时间线行程卡与一键导航链接。雨雪高温天气自动把室内方案和雨备排前。绝不编造链接，只做检索、摘要与跳转，不搬运全文，出行安全提示前置。"
description_en: "A weekend family outing planner for parents. On first use it collects a family profile (city, child age, budget, transport, preferences). Then whenever you ask where to take the kids this weekend, it searches the web in real time for recent, genuine family-friendly outdoor guides and venue activities in your city, verifies freshness (posts older than 3 months are never used as the sole source), and ranks candidates with a weighted score across weather fit, age fit, distance, budget and freshness. It outputs the top 3-5 plans, each with a key-info table, highlights, safety tips, real clickable source links, a checkable timeline itinerary card and a one-tap map navigation link. On rainy or hot days indoor options and rain backups are ranked first. It never fabricates URLs - search, summarize and link only."
version: 1.0.0
author: zhoupeisi
examples_zh:
  - "这周带娃去哪？"
  - "周末遛娃，孩子5岁，预算200以内"
  - "下雨天适合带娃去哪"
examples_en:
  - "Where can I take my 5-year-old this weekend?"
  - "Plan a Saturday family outing within budget 200 yuan"
  - "Rainy day indoor options for kids"
allowed-tools:
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Read
  - Write
  - Edit
---

# 周末遛娃规划通 — 亲子周末出行规划助手

帮家长回答那个每周都会出现的问题：**"这周带娃去哪？"**

它是一个规划 Agent：每次提问都**实时联网检索**你所在城市近期的真实亲子户外内容（公众号、本地亲子号、政府公益场馆、搜索引擎收录的小红书/抖音攻略摘要），抽取结构化信息、核验时效、按你的家庭档案和本周天气打分排序，输出带**真实来源链接**的方案和可勾选打卡的行程卡。

- **它不维护内容库**：每次按需检索，不囤积、不搬运全文。
- **它不编造链接**：所有推荐都附可点击的真实来源，查不到就明说。
- **它不替你做决定**：给方案、给理由、给链接，去不去你定。

## 工作流程

### Phase 0 — 加载家庭档案（每次触发先跑）
- 读取档案文件 `~/.workbuddy/outings/family-profile.json`。
- 文件不存在或写入失败时：改用对话内记忆（在回复中向用户复述档案内容即可），不中断流程。
- 档案存在：回复开头一行提示「已载入档案：{城市}/{孩子年龄}/{预算}/{交通}。说"更新档案"可修改」。
- 用户说"更新档案"：重新执行 Phase 1。

### Phase 1 — 家庭档案采集（首次 / 更新时）
用选择题方式采集（一次最多 4 题）：
1. **城市**（决定检索地域与天气，允许自由输入）
2. **孩子年龄**：3–4 岁 / 5–6 岁 / 7–8 岁 / 其他
3. **预算档**：免费优先 / 平价（0–100 元）/ 中档（100–300 元）/ 不限
4. **偏好类型**（可多选）：自然户外 / 博物馆科技馆 / 农场采摘 / 乐园游乐 / 公益免费场馆 / 亲子市集

交通方式（自驾/公交/步行）、单次时长（半日/一日）、已去过或不想去的地方，作为自由补充项，用户可随时补充或说"更新档案"补录。

采集后写入档案文件：
```json
{
  "city": "上海",
  "childAge": "5-6岁",
  "budget": "平价(0-100元)",
  "transport": "自驾",
  "preferences": ["自然户外", "农场采摘"],
  "exclusions": [],
  "updatedAt": "2026-10-29"
}
```

### Phase 2 — 检索近期真实内容
收到"这周去哪"类提问后：
1. **先查天气**：搜索「{城市} 本周末 天气预报」，记录温度、降水、空气质量，作为排序与雨备依据。
2. **多路检索**（每路优先近 1–3 个月内容，城市与当前年份必须进查询词）：
   - 攻略类：「{城市} 亲子 遛娃 户外 攻略」「{城市} 周末 带娃 去哪 小红书」
   - 活动类：「{城市} 亲子 活动 公众号」「{城市} 儿童 免费 活动 场馆」
   - 场馆类：「{城市} 亲子 公园 自然 探索」「{城市} 儿童 博物馆 科技馆 推荐」
3. **只认检索返回的链接**。命中结果进入候选池，每条记录真实来源 URL。
4. **覆盖局限如实记录**：对小红书/抖音站内内容的覆盖有限（平台内容仅部分被搜索引擎收录），命中稀少属正常，输出时须如实声明，并提示"可把你收藏的原帖链接粘贴给我，我帮你解析进方案"。

### Phase 3 — 结构化抽取 + 时效核验
对每个候选，按 `references/field-schema.md` 抽取字段（名称/类型/区域/适龄/距离/费用/时长/天气适配/亮点/注意事项/来源/时效）。

**时效核验铁则**：
- 超过 3 个月的帖子不作为唯一依据；活动类必须核实"本周是否仍举办、场馆是否仍营业"，不能确定就标「需核实」。
- 距离、费用若检索未给出，标「未知」，禁止估算填充。

### Phase 4 — 评分排序 + 个性化推荐
按 `references/field-schema.md` 的权重计算适配度评分（0–100）：年龄适配 25 + 天气适配 25 + 距离通勤 20 + 预算 15 + 时效新鲜度 15。
- 结合档案（年龄/预算/偏好/交通）与天气，给每个方案一句话推荐理由。
- 雨天/高温：自动把室内或清晨/傍晚方案排前，并显式标注「雨备」。
- 输出 Top 3–5 个方案，候选不足就少给，宁缺毋滥。

### Phase 5 — 输出方案 + 视觉卡片（双输出）
**5A. 对话正文（文字版）**：按 `templates/outing-card-template.md` 渲染每个方案：标题 + 适配度 + 推荐理由 → 关键信息表 → 亮点 → 注意事项 → 真实来源链接 → 可勾选行程卡（时间线）→ 导航链接（高德地图 `https://uri.amap.com/search?keyword={名称}{城市}`）。

**5B. 视觉卡片（PNG 版，默认生成 Top 1 方案）**：
1. 按 `references/card-json-schema.md` 把 Top 1 方案字段映射成 JSON，写入临时文件（如 `~/.workbuddy/outings/card-<日期>.json`）。
2. 调用脚本生成 1080×1440 竖版 PNG：
   ```bash
   python3 <本skill目录>/scripts/render_outing_card.py <json路径> --out <输出png路径>
   ```
   - 依赖 Pillow（缺失时提示用户 `pip install pillow`，不要中断文字版输出）。
   - 字体自动跨平台 fallback（macOS PingFang / Windows 微软雅黑 / Linux Noto），无需用户配置。
3. 用 `present_files` 展示生成的 PNG；回复里一句话说明「已生成可保存/分享的行程卡图片」。
4. 用户要求「全部方案都出卡片」时，对 Top 2–5 逐个生成，文件名带方案序号。
5. **降级规则**：脚本不可用（无 Pillow / 无中文字体）时，跳过 5B 只给文字版，并说明原因，绝不让卡片故障阻塞主输出。

文末必须附「数据来源与覆盖说明」：本次检索覆盖的平台、命中数量、覆盖局限的诚实声明与补充建议。

## 铁律（违反即失效）
1. **绝不编造 URL**。所有链接必须来自检索结果或用户粘贴的原帖；无法验证的只给搜索关键词建议，绝不生成假链接。
2. **时效核验**。超 3 个月的帖子不单独采信；活动/场馆须核实本周仍有效，不确定标「需核实」。
3. **版权边界**。只做摘要 + 跳转，不存储、不搬运全文；展示必标来源。
4. **覆盖诚实**。输出末尾必须声明对小红书/抖音站内内容覆盖有限，不夸大能力。
5. **不绕过平台限制**。不做任何绕过目标平台访问控制的行为；更广覆盖引导用户走合规通道（用户贴链接、平台开放能力、授权合作）。
6. **不替决策 + 安全前置**。给方案+理由+链接，去不去家长定；涉水域、高空、野生动物、人群密集的项目必须附注意事项。
