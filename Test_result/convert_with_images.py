# -*- coding: utf-8 -*-
"""
重新生成包含图片的投资分析报告HTML
"""

import re
import html

def parse_markdown_to_html(md_file):
    """将markdown转换为HTML，保留图片引用"""

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 分割成行
    lines = content.split('\n')

    html_parts = []
    in_table = False
    table_rows = []

    for line in lines:
        # 图片引用：![](images/xxx.jpg) -> <div class="figure-item">...
        if re.match(r'^!\[\]\(images/.+\)$', line.strip()):
            img_match = re.search(r'!\[\]\(images/([^)]+)\)', line)
            if img_match:
                img_file = img_match.group(1)
                html_parts.append(f'''              <div class="figure-item">
                <img class="figure-img" src="assets/images/{img_file}" alt="{img_file}">
              </div>''')
            continue

        # 一级标题 # -> .section-title 或 .part-title
        if line.startswith('# '):
            title = line[2:].strip()
            if 'PART' in title.upper() or title in ['项目概况', '市场竞争分析', '客户及定位分析', '设计方案', '运营计划', '投资测算']:
                # Part标题
                part_id = title.replace(' ', '').lower()
                if 'PART1' in title.upper() or '项目概况' in title:
                    part_id = 'part1'
                elif 'PART2' in title.upper() or '市场竞争' in title:
                    part_id = 'part2'
                elif 'PART3' in title.upper() or '客户' in title:
                    part_id = 'part3'
                elif 'PART4' in title.upper() or '设计' in title:
                    part_id = 'part4'
                elif 'PART5' in title.upper() or '运营' in title:
                    part_id = 'part5'
                elif 'PART6' in title.upper() or '投资' in title:
                    part_id = 'part6'

                html_parts.append(f'''
          <header class="section-header">
            <h2 class="section-title">{title}</h2>
          </header>''')
            else:
                html_parts.append(f'''          <h3 class="section-subtitle">{title}</h3>''')
            continue

        # 二级标题 ## -> .section-subtitle
        if line.startswith('## '):
            title = line[3:].strip()
            html_parts.append(f'''          <h3 class="section-subtitle">{title}</h3>''')
            continue

        # 三级标题 ###
        if line.startswith('### '):
            title = line[4:].strip()
            html_parts.append(f'''          <h4>{title}</h4>''')
            continue

        # 表格处理 <table>开头
        if line.strip().startswith('<table>'):
            in_table = True
            table_rows = [line]
            continue
        elif in_table and line.strip().startswith('</table>'):
            table_rows.append(line)
            table_html = '\n'.join(table_rows)
            html_parts.append(f'''          <div class="table-wrapper">
            {table_html}
          </div>''')
            in_table = False
            table_rows = []
            continue
        elif in_table:
            table_rows.append(line)
            continue

        # 普通段落
        if line.strip() and not line.startswith('#'):
            # 跳过空行
            if line.strip() == '':
                continue

            # 转义HTML特殊字符
            text = html.escape(line.strip())

            # 处理特殊符号
            text = text.replace('■', '<strong>■</strong>')
            text = text.replace('√', '<strong>√</strong>')
            text = text.replace('✓', '<strong>✓</strong>')

            # 处理数学公式 $xxx$ -> xxx
            text = re.sub(r'\$(.*?)\$', r'\1', text)

            html_parts.append(f'''          <p>{text}</p>''')

    return '\n'.join(html_parts)

def generate_complete_html():
    """生成完整的HTML文件"""

    # HTML头部
    html_head = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="松江区泗泾04-08号地块投资分析报告">
  <meta name="author" content="金地集团投资部">
  <title>松江区泗泾04-08号地块投资分析报告</title>

  <!-- 样式表 -->
  <link rel="stylesheet" href="assets/theme.css">
  <link rel="stylesheet" href="assets/styles.css">
  <link rel="stylesheet" href="assets/print.css" media="print">
</head>
<body>
  <!-- 顶部导航 -->
  <nav class="topnav">
    <div class="topnav-inner">
      <div class="topnav-brand">松江区泗泾04-08号地块</div>
      <div class="topnav-tabs">
        <a class="topnav-tab active" data-part="cover" href="#cover">首页</a>
        <a class="topnav-tab" data-part="part1" href="#part1">项目概况</a>
        <a class="topnav-tab" data-part="part2" href="#part2">市场竞争</a>
        <a class="topnav-tab" data-part="part3" href="#part3">客户及产品定位</a>
        <a class="topnav-tab" data-part="part4" href="#part4">设计方案</a>
        <a class="topnav-tab" data-part="part5" href="#part5">运营计划</a>
        <a class="topnav-tab" data-part="part6" href="#part6">投资测算</a>
      </div>
      <button class="mobile-menu-btn" aria-label="菜单">
        <span class="menu-icon">☰</span>
      </button>
    </div>
  </nav>

  <!-- 主内容 -->
  <main class="main">
    <div class="container">

      <!-- 首页封面 -->
      <section id="cover" class="part">
        <div class="container-narrow">
          <div style="text-align: center; padding: 4rem 0;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: var(--accent); margin-bottom: 1rem;">
              松江区泗泾04-08号地块
            </h1>
            <h2 style="font-size: 2rem; font-weight: 600; color: var(--text-primary); margin-bottom: 2rem;">
              投资分析报告
            </h2>
            <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 2rem; flex-wrap: wrap;">
              <div style="text-align: center;">
                <div style="font-size: 0.875rem; color: var(--text-muted);">板块</div>
                <div style="font-size: 1.125rem; font-weight: 600; color: var(--text-primary);">泗泾</div>
              </div>
              <div style="text-align: center;">
                <div style="font-size: 0.875rem; color: var(--text-muted);">容积率</div>
                <div style="font-size: 1.125rem; font-weight: 600; color: var(--text-primary);">1.2</div>
              </div>
              <div style="text-align: center;">
                <div style="font-size: 0.875rem; color: var(--text-muted);">计容面积</div>
                <div style="font-size: 1.125rem; font-weight: 600; color: var(--text-primary);">2.32万㎡</div>
              </div>
              <div style="text-align: center;">
                <div style="font-size: 0.875rem; color: var(--text-muted);">起拍楼板价</div>
                <div style="font-size: 1.125rem; font-weight: 600; color: var(--accent);">2.3万/㎡</div>
              </div>
            </div>
            <div class="chips" style="justify-content: center;">
              <span class="chip">轨交1.3km</span>
              <span class="chip">外郊环</span>
              <span class="chip">纯低密社区</span>
              <span class="chip">配套成熟</span>
              <span class="chip">学区二梯队</span>
              <span class="chip">无不利因素</span>
            </div>
            <p style="margin-top: 2rem; color: var(--text-muted); font-size: 0.875rem;">
              内部资料，请勿外传 · 金地集团投资部
            </p>
          </div>
        </div>
      </section>
'''

    # 解析markdown内容
    content_html = parse_markdown_to_html(r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result\investment_report_minerU\full.md')

    # HTML尾部
    html_tail = '''
    </div>
  </main>

  <!-- 脚本 -->
  <script src="assets/app.js"></script>
</body>
</html>'''

    return html_head + content_html + html_tail

if __name__ == '__main__':
    # 生成HTML
    html = generate_complete_html()

    # 写入文件
    output_file = r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result\investment_report_website\index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[OK] HTML generated: {output_file}")

    # Count images
    img_count = html.count('<img class="figure-img"')
    print(f"[OK] Images included: {img_count}")
