---
name: jindi_investment_build_site
description: |
  金地集团【投资部】专项 Skill：将「images 文件夹 + full.md（按页提取的 PPT 内容）」自动生成一套可汇报/可打印的投资分析报告网站。
  ✅固定 6 大 Part 顶部导航 ✅每 Part 侧边导航（Part1/2/4/6 固定小节）✅图片“视觉净化”展示 ✅白底 + 一抹橙色 ✅每 Part 版式差异化
language: zh-CN
org: 金地集团
department: 投资部
scope_tags:
  - investment
  - land-acquisition
  - investment-report
  - ppt-to-web
  - gemdale-internal
routing:
  priority_when_user_says:
    - "我是投资的工作人员"
    - "我是投资部"
    - "我是投拓"
    - "我是投资管理"
    - "我要做投资分析报告"
    - "拿地测算/研判"
  note: |
    当用户自我声明为“投资/投拓/投资管理”等角色时，优先使用本 Skill，并将候选技能范围收敛到带【投资部】标签的 Skills。

inputs:
  # ✅ 用户本次的入参形式：一个解压后的目录，里面有 full.md + images/
  source_dir:
    type: string
    required: true
    description: |
      必填。指向一个目录，该目录至少包含：
      - full.md（按页/按结构提取的 PPT 全文）
      - images/（full.md 引用到的所有图片）
      示例：
      source_dir/
        full.md
        images/
          xxx.jpg
          yyy.png

  # 兼容：若用户分开传入，也支持
  full_md_path:
    type: string
    required: false
    description: 可选。full.md 的绝对/相对路径。若不填，则默认读取 {source_dir}/full.md
  images_dir:
    type: string
    required: false
    description: 可选。images 文件夹路径。若不填，则默认读取 {source_dir}/images

  ui_template:
    type: string
    required: false
    default: "apple-minimal"
    enum:
      - apple-minimal
      - report-pro
      - gemdale-brand
    description: |
      页面风格模板（仅影响“视觉表达”，不改变信息架构）：
      - apple-minimal：白底通透、留白克制、磨砂顶栏、卡片化（推荐）
      - report-pro：投研/咨询研报风格（表格更强）
      - gemdale-brand：金地品牌化（Logo/页脚更强调）

  theme:
    type: object
    required: false
    description: |
      主题覆盖（不填则使用默认白底+橙色）
    fields:
      accent_hex: "#FF6A00"
      bg_hex: "#FFFFFF"
      surface_hex: "#FFFFFF"
      text_hex: "#111827"
      muted_hex: "#6B7280"
      border_hex: "#E5E7EB"

  report_meta:
    type: object
    required: false
    description: 报告元信息（缺失则从 full.md 推断，推断失败用占位符）
    fields:
      report_title: "默认：投资分析报告"
      project_name: "地块/项目名称"
      city: "城市"
      district: "区/板块"
      report_date: "YYYY-MM-DD"
      confidentiality: "默认：内部资料，请勿外传"
      author: "投资部/制作者"
      version: "默认：V1.0"

  image_render_mode:
    type: string
    required: false
    default: "clean-first"
    enum:
      - clean-first       # 默认：优先展示“净化后的信息”，原图收在折叠/弹窗里
      - original-first    # 优先展示原图，同时给出净化摘要
      - clean-only        # 仅展示净化后的信息（如果无法净化则展示原图）
    description: |
      图片展示策略。“净化”指：用视觉理解提取关键信息，重排成清爽的表格/要点/小图，而不是把截图原样塞进网页。

outputs:
  format: website_bundle
  deliverables:
    - index.html
    - /assets/theme.css           # ✅ 设计 tokens（必须）
    - /assets/styles.css          # 主样式（仅引用 tokens）
    - /assets/print.css           # 打印/PDF 友好样式
    - /assets/app.js              # 交互：scrollspy / smooth / lightbox / mobile nav / accordions
    - /assets/report_data.json    # 结构化数据（Part/Section/Blocks）
    - /assets/images/*            # 拷贝/引用原始图片
---

# 金地集团投资部｜投资分析报告网站生成器（Build-Site：full.md + images）

> 目标：你给一份由 PPT 提取的 `full.md`（按页/按结构分块） + 一堆图片（`images/`），我输出一个“可直接汇报给领导”的网站：结构固定、导航清晰、信息密度可控、图片清爽、不堆杂符号。

---

## 0. 固定信息架构（必须，不随模板变化）

### 顶部导航（Top Tabs 固定）
`首页 / 项目概况 / 市场竞争 / 客户及产品定位 / 设计方案 / 运营计划 / 投资测算`

### 侧边导航（Side Nav）
- 每个 Part 必须有独立侧边栏（桌面端常驻；移动端抽屉）
- Part1/2/4/6 侧边栏标题固定（见下）
- Part3/5 侧边栏由 full.md 自动抽取（见下）

---

## 1. 输入文件结构与解析原则（必须）

### 1.1 默认读取路径
- `full_md = {full_md_path or source_dir + "/full.md"}`
- `images_dir = {images_dir or source_dir + "/images"}`

### 1.2 full.md 的常见结构（需兼容）
- 目录中可能出现：`PART1项目概况 / PART2市场竞争分析 / ...`
- Part 标题可能出现：`# 01 项目概况`、`# 02 市场竞争分析` 等
- 小节标题可能出现：`# 1.1 xxx`、`# 2.1 xxx`、以及“无 # 的纯文本行”（例如 `1.6 红线外不利因素`）

### 1.3 解析输出（必须生成 report_data.json）
解析为：
- report.meta
- report.parts[]：
  - part_id: part1..part6
  - title: 项目概况/市场竞争/...
  - sections[]:
    - id, title
    - blocks[]: {type: "text|table|image|callout|list", ...}
    - key_takeaways[]（强制 3–5 条，空则占位）
    - kpis[]（可选，Part1/6 优先尝试抽取）

---

## 2. Part 与小节映射规则（关键：按你给的固定小节）

### Part1：项目概况（固定 6 项，学区配套可选）
侧边栏顺序固定：
1) 1.1 指标与区位  
2) 1.2 用地条件分析  
3) 1.3 交通分析  
4) 1.4 配套分析  
5) 1.5 学区配套（若 full.md 中不存在“学区/学校/对口”等关键词则不显示）  
6) 1.6 红线外不利因素  

**映射策略：**
- 优先用标题匹配：`# 1.1` / `# 1.2` / `# 1.3` / `# 1.4` / `# 1.5` / `# 1.6`
- 若某小节标题缺少 `#`，则用行首正则：`^\s*1\.6\s+`
- 若仍缺失，则用关键词窗口：
  - 指标与区位：指标、容积率、计容、楼板价、区位、半径、虹桥、地铁距离
  - 用地条件：红线、控规、限高、退界、保障房、装配式、绿建
  - 交通：轨交、地铁、道路、高速、通勤、枢纽
  - 配套：商业、医院、公园、配套
  - 学区：学校、学区、对口、教育
  - 红线外不利：不利因素、噪音、变电站、墓地、高压线、河道

### Part2：市场竞争分析（固定 10 项：1.1–1.9 + 2.0 小结）
侧边栏顺序固定：
1) 1.1 政策  
2) 1.2 全市土地市场  
3) 1.3 区域规划  
4) 1.4 土地市场（地块所在区域）  
5) 1.5 住宅市场（地块所在区域）  
6) 1.6 板块分析  
7) 1.7 销售市场（地块所在区域）  
8) 1.8 竞品分析  
9) 1.9 二手房竞争分析  
10) 2.0 小结  

**映射策略：**
- full.md 里可能写成 `# 2.1 / # 2.2 ...`，所以必须做“关键词映射”：
  - 政策：政策、限购、限售、积分、交易、土拍、拍卖规则
  - 全市土地市场：全市、上海、土拍、成交、溢价、供地、楼板价
  - 区域规划：规划、控规、产业、轨交规划、五大新城
  - 土地市场（区域）：区域土地、板块土拍、近年出让
  - 住宅市场（区域）：新房、供应、成交、去化、价格带
  - 板块分析：板块、客群、产品、竞合、定位
  - 销售市场（区域）：销售、流速、开盘、认购、成交
  - 竞品分析：竞品、项目对比、产品、价格、去化、货值
  - 二手房：二手房、挂牌、成交、学区房、价格
  - 小结：小结、结论、建议、策略、研判

> 若某项找不到内容：仍保留该侧边栏条目，但内容区显示“暂无（PPT 未提供该页/该段）”，并默认折叠。

### Part3：客户及产品定位分析（无固定小节，自动生成侧边栏）
规则：
- 在 Part3 范围内，抽取所有一级/二级标题（`#` / `##`）
- 去掉“Part3 标题行”本身
- 若标题过多（>10），按语义合并：客群/产品/价格/户型/定位/机会点/策略等
- 侧边栏标题用“短标题（<=14字）”，超长则自动截断并提供 tooltip

### Part4：设计方案（固定 + 方案列表）
侧边栏结构：
- 4.1 规划边界条件梳理  
- 4.1 设计条件梳理（注意：ID 需区分，可用 `4.1b`）  
- 4.2 方案对比  
- 方案一 / 方案二 / 方案三 ...（从 full.md 自动识别：`方案一`、`方案二`、`Option A/B` 等）

### Part5：运营计划（无固定小节，自动生成侧边栏）
规则同 Part3，但优先识别：
- 工期/里程碑/开盘节奏/回款/营销动作/工程关键节点

### Part6：投资测算（版本列表，固定“版本”导航）
侧边栏：
- 版本一 / 版本二 / 版本三 ...（从 full.md 自动识别：`版本`、`测算`、`IRR`、`敏感性`、`现金流`）
- 若 full.md 没有显式“版本”标题，则按“测算章节分段”自动生成 Version 1/2/3

---

## 3. 图片“视觉净化”规则（你最关心的点）

你要求：图片只展示重要信息，不要无用杂乱符号。实现策略如下：

### 3.1 图片分类（必须）
对每张图片（或每个 image block）用视觉理解判断类别：
- 区位/地图（含圈层、路网）
- 总图/红线/控规（规划图）
- 表格截图（指标表、竞品表）
- 图表（柱状/折线/饼图）
- 方案对比（多方案平面对比）
- 其他（配图/示意）

### 3.2 净化输出形态（按类别强制选择）
- 表格截图 → “重建为 HTML 表格 + 关键列突出”，原图收起
- 地图/区位 → 提取关键点清单（如：地铁距离、商圈、医院、学校）+ 一张原图（可缩略）
- 图表 → 优先提取关键结论（趋势/极值/同比）+ 若能读数则输出小表格
- 方案图 → 每方案 3–5 条“差异点”+ 关键指标卡片（货值/套数/户配等，若能提取）
- 其他 → 直接作为画廊图展示，但必须加 caption（从上下文推断）

### 3.3 原图保留策略（可控）
- `clean-first`：默认只在“展开原图”或 lightbox 中看到原图
- `original-first`：先展示原图，下方给“净化摘要”
- `clean-only`：只展示净化结果；净化失败才降级为原图

---

## 4. 视觉与组件系统（白底 + 一抹橙色，且每 Part 版式不同）

### 4.1 必须输出 Design Tokens：assets/theme.css
- 色彩：bg / surface / text / muted / border / accent / accent-weak
- 间距：8pt 网格
- 圆角：默认 12；图片 16；Apple 模板可 20
- 阴影：三档，Apple 模板更轻

> **styles.css 中禁止硬编码颜色/间距**；只能引用 tokens（例如 `var(--accent)`）。（见“必须输出 theme.css + tokens”要求）  

### 4.2 统一组件（必须以组件渲染，而非自由排版）
- ModuleCard（小节容器）
- Lead（章节导语）
- KeyTakeaways（3–5 条，必有）
- KpiRow（Part1/6 表格前优先生成）
- DataTable（sticky head + 横向滚动 + zebra）
- FigureGallery（统一 figure/caption/圆角）
- Callout（结论/风险/机会点）
- Accordion（长表格/附录折叠）
- Chips（机会点关键词）

---

## 5. 每个 Part 的差异化版式（必须“各不相同”，但整体统一）

### 首页（Cover）
- Hero：项目名 + 报告标题 + 版本/日期
- Chips：8–12 个“机会点关键词”
- Meta：4–6 项轻量元信息
- 右侧：封面主视觉（区位/总平/航拍三选一，若无则留空）

### Part1：两栏 + KPI 强调
- 顶部：KPI 卡片行（容积率/计容/起拍楼板价/地铁距离…能提取多少算多少）
- 主体：左“文字/结论”，右“图片画廊/地图/红线图”
- 表格：默认折叠（Accordion），提供“展开明细”

### Part2：卡片矩阵 + 竞品对比
- 政策/市场：以 Callout + 小图表摘要呈现
- 竞品：竞品卡片网格（名称/定位/价格带/流速/结论）
- 末尾：2.0 小结必须突出（大 Callout）

### Part3：人物画像/定位画布
- 用 Persona Cards（客群）+ Positioning Cards（产品）+ Pricing Band（价格带）
- 若有“结论页”：以“大字结论”风格呈现

### Part4：方案总览 + 方案页
- 先做“方案对比总览”（对比表 + 差异 badge）
- 再按 方案一/二/三 单独模块：每方案固定 3 块
  - 总平/规划图 gallery
  - 户配/面积段（若能提取）
  - 优势 & 风险（bullet）

### Part5：时间轴/里程碑
- 用 Timeline（纵向）展示关键节点（开盘/回款/拿证/施工…）
- 详细表格折叠

### Part6：版本 Tab + 财务 KPI
- 版本切换（tabs）
- 每版本展示：IRR/NPV/毛利率/峰值资金等 KPI（能提取多少算多少）
- 敏感性分析：表格 + 结论 Callout

---

## 6. 交互与可用性（必须）

- scrollspy：Top Tabs + Side Nav 双高亮
- smooth scroll：点击侧边栏平滑滚动
- 图片 lightbox：支持 caption、ESC 关闭、左右切换（同一 gallery）
- Mobile：Side Nav 抽屉（Drawer）+ 顶部“目录”按钮
- 性能：图片 `loading="lazy"`，首屏优先加载封面图与当前 Part 的首段

---

## 7. 输出文件结构（必须）

```
site/
  index.html
  assets/
    theme.css
    styles.css
    print.css
    app.js
    report_data.json
    images/
      *.jpg|png
```

---

## 8. 生成步骤（Claude Code 执行清单）

1) 校验输入目录：full.md + images/ 是否存在；统计图片数量  
2) 解析 full.md → report_data.json（Part/Section/Blocks）  
3) 为每个 section 生成：
   - key_takeaways（3–5）
   - kpis（可选）
4) 对每个 image block 执行“视觉净化”并生成：
   - cleaned_summary（要点/表格/结论）
   - caption（从上下文推断）
5) 生成静态站点文件（index.html + assets/*）  
6) 自检：
   - Top Tabs 是否包含 7 个项
   - 每个 Part 是否有 Side Nav（Part3/5 自动）
   - Part1 是否按“学区配套可选”处理
   - 表格是否横向滚动 + sticky head
   - styles.css 是否无硬编码颜色（仅 tokens）
   - 全站是否白底 + 橙色点缀

---

## 9. 验收标准（必须达标）

- ✅ 结构：Top Tabs + 每 Part Side Nav 完整
- ✅ Part1/2/4/6 小节命名与顺序严格符合需求
- ✅ 图片默认不堆杂：优先呈现“净化信息”，原图可展开
- ✅ 视觉：白底 + 一抹橙色；卡片/表格/图片风格统一
- ✅ 每 Part 版式“明显不同”但不跳脱
- ✅ 可打印：print.css 输出 A4 友好分页、隐藏交互控件
