#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金地投资报告网站生成器
生成可直接用于汇报的静态网站
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

# ============== 配置 ==============
BASE_DIR = Path('Test_result/investment_report_minerU')
SOURCE_DIR = BASE_DIR
OUTPUT_DIR = BASE_DIR / 'site'
IMAGES_DIR = SOURCE_DIR / 'images'
REPORT_DATA_PATH = SOURCE_DIR / 'report_data.json'

# ============== Design Tokens ==============
THEME_CSS = '''/* Design Tokens - 金地投资报告主题 */
:root {
  /* 色彩系统 */
  --color-bg: #FFFFFF;
  --color-surface: #F8F9FA;
  --color-surface-elevated: #FFFFFF;
  --color-text: #1A1A1A;
  --color-text-secondary: #666666;
  --color-text-muted: #999999;
  --color-border: #E5E7EB;
  --color-border-light: #F0F0F0;
  --color-accent: #FF6B35; /* 金地橙色 */
  --color-accent-hover: #E55A2B;
  --color-accent-light: #FFF0EB;
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-info: #3B82F6;

  /* 间距系统 */
  --spacing-xs: 0.25rem;    /* 4px */
  --spacing-sm: 0.5rem;     /* 8px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */
  --spacing-3xl: 4rem;      /* 64px */

  /* 字体系统 */
  --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-family-heading: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 2rem;      /* 32px */
  --font-size-4xl: 2.5rem;    /* 40px */

  /* 圆角 */
  --radius-sm: 0.25rem;   /* 4px */
  --radius-md: 0.5rem;    /* 8px */
  --radius-lg: 0.75rem;   /* 12px */
  --radius-xl: 1rem;      /* 16px */

  /* 阴影 */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

  /* 布局 */
  --header-height: 64px;
  --sidebar-width: 280px;
  --content-max-width: 1200px;
  --container-padding: var(--spacing-lg);
}

/* Dark mode support (optional) */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0F0F0F;
    --color-surface: #1A1A1A;
    --color-surface-elevated: #242424;
    --color-text: #F5F5F5;
    --color-text-secondary: #A0A0A0;
    --color-text-muted: #6B7280;
    --color-border: #2A2A2A;
    --color-border-light: #1F1F1F;
  }
}
'''

# ============== Main CSS ==============
STYLES_CSS = '''/* 金地投资报告 - 主样式表 */

/* ===== Base ===== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  font-size: 16px;
}

body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  line-height: 1.7;
  color: var(--color-text);
  background-color: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ===== Typography ===== */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-family-heading);
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-text);
  margin-bottom: var(--spacing-md);
}

h1 { font-size: var(--font-size-4xl); }
h2 { font-size: var(--font-size-3xl); }
h3 { font-size: var(--font-size-2xl); }
h4 { font-size: var(--font-size-xl); }
h5 { font-size: var(--font-size-lg); }
h6 { font-size: var(--font-size-base); }

p {
  margin-bottom: var(--spacing-md);
}

a {
  color: var(--color-accent);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--color-accent-hover);
}

/* ===== Header & Navigation ===== */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
  z-index: 1000;
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-xl);
  box-shadow: var(--shadow-sm);
}

.header-logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text);
}

.header-logo img {
  height: 32px;
  width: auto;
}

.top-tabs {
  display: flex;
  gap: var(--spacing-xs);
  margin-left: auto;
}

.top-tab {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.top-tab:hover {
  color: var(--color-text);
  background: var(--color-surface);
}

.top-tab.active {
  color: var(--color-accent);
  background: var(--color-accent-light);
}

/* ===== Layout ===== */
.main-container {
  display: flex;
  margin-top: var(--header-height);
  min-height: calc(100vh - var(--header-height));
}

.sidebar {
  width: var(--sidebar-width);
  position: fixed;
  top: var(--header-height);
  left: 0;
  bottom: 0;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  overflow-y: auto;
  padding: var(--spacing-lg);
  z-index: 100;
}

.sidebar-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--color-border-light);
}

.sidebar-nav {
  list-style: none;
}

.sidebar-nav-item {
  margin-bottom: var(--spacing-xs);
}

.sidebar-nav-link {
  display: block;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
}

.sidebar-nav-link:hover {
  color: var(--color-text);
  background: var(--color-bg);
}

.sidebar-nav-link.active {
  color: var(--color-accent);
  background: var(--color-accent-light);
  font-weight: 500;
}

.content {
  flex: 1;
  margin-left: var(--sidebar-width);
  padding: var(--spacing-2xl) var(--spacing-3xl);
  max-width: calc(100% - var(--sidebar-width));
}

/* ===== Sections & Cards ===== */
.section {
  margin-bottom: var(--spacing-3xl);
  scroll-margin-top: calc(var(--header-height) + var(--spacing-lg));
}

.section-title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--color-accent);
}

.card {
  background: var(--color-surface-elevated);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
  color: var(--color-text);
}

/* ===== Tables ===== */
.table-container {
  overflow-x: auto;
  margin: var(--spacing-lg) 0;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

thead {
  background: var(--color-surface);
}

th {
  padding: var(--spacing-md);
  text-align: left;
  font-weight: 600;
  color: var(--color-text);
  border-bottom: 2px solid var(--color-border);
}

td {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text-secondary);
}

tr:last-child td {
  border-bottom: none;
}

tbody tr:hover {
  background: var(--color-surface);
}

/* ===== Images ===== */
img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.image-card {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.image-card img {
  width: 100%;
  height: auto;
  display: block;
}

.image-caption {
  padding: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-align: center;
}

/* ===== Key Takeaways ===== */
.key-takeaways {
  background: linear-gradient(135deg, var(--color-accent-light) 0%, var(--color-surface) 100%);
  border-left: 4px solid var(--color-accent);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.key-takeaways-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-accent);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-md);
}

.key-takeaways-list {
  list-style: none;
}

.key-takeaways-list li {
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.key-takeaways-list li:before {
  content: "✓";
  position: absolute;
  left: 0;
  color: var(--color-accent);
  font-weight: 600;
}

/* ===== KPI Cards ===== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.kpi-card {
  background: var(--color-surface-elevated);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  text-align: center;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border-light);
}

.kpi-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--spacing-xs);
}

.kpi-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-accent);
}

/* ===== Part4 Design Options ===== */
.design-option {
  background: var(--color-surface-elevated);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  margin: var(--spacing-2xl) 0;
}

.design-option-header {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-hover) 100%);
  color: white;
  padding: var(--spacing-xl);
}

.design-option-title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  margin: 0;
}

.design-option-content {
  padding: var(--spacing-xl);
}

.master-plan-section {
  margin-bottom: var(--spacing-2xl);
}

.master-plan-image {
  width: 100%;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--spacing-lg);
}

.master-plan-points {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
}

.master-plan-point {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-surface);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
}

.master-plan-point:before {
  content: "•";
  color: var(--color-accent);
  font-weight: 600;
}

.unit-mix-table {
  margin: var(--spacing-lg) 0;
}

.model-placeholder {
  background: var(--color-surface);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-3xl);
  text-align: center;
  color: var(--color-text-muted);
}

.model-placeholder-icon {
  font-size: var(--font-size-4xl);
  margin-bottom: var(--spacing-lg);
}

.advantages-list {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-md);
}

.advantages-list li {
  padding: var(--spacing-md);
  background: var(--color-accent-light);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-accent);
  font-size: var(--font-size-sm);
}

/* ===== Mobile Responsive ===== */
@media (max-width: 768px) {
  .top-tabs {
    display: none;
  }

  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .content {
    margin-left: 0;
    padding: var(--spacing-lg);
    max-width: 100%;
  }

  .mobile-menu-btn {
    display: block;
  }
}

@media (min-width: 769px) {
  .mobile-menu-btn {
    display: none;
  }
}

/* ===== Print Styles ===== */
@media print {
  .header, .sidebar, .top-tabs {
    display: none !important;
  }

  .content {
    margin: 0 !important;
    padding: 0 !important;
    max-width: 100% !important;
  }

  .card, .design-option {
    page-break-inside: avoid;
    box-shadow: none;
    border: 1px solid #ddd;
  }
}
'''

# ============== JavaScript ==============
APP_JS = '''// 金地投资报告 - 交互脚本

(function() {
  'use strict';

  // ===== 状态管理 =====
  const state = {
    currentPart: null,
    currentSection: null,
    sidebarOpen: false
  };

  // ===== DOM 元素 =====
  const elements = {
    topTabs: document.querySelectorAll('.top-tab'),
    sidebarNavLinks: document.querySelectorAll('.sidebar-nav-link'),
    sections: document.querySelectorAll('.section'),
    sidebar: document.querySelector('.sidebar'),
    mobileMenuBtn: document.querySelector('.mobile-menu-btn'),
    images: document.querySelectorAll('.image-card img')
  };

  // ===== 初始化 =====
  function init() {
    bindEvents();
    initScrollSpy();
    initLightbox();
  }

  // ===== 事件绑定 =====
  function bindEvents() {
    // 顶部导航点击
    elements.topTabs.forEach(tab => {
      tab.addEventListener('click', handleTopTabClick);
    });

    // 侧边栏导航点击
    elements.sidebarNavLinks.forEach(link => {
      link.addEventListener('click', handleSidebarNavClick);
    });

    // 移动端菜单按钮
    if (elements.mobileMenuBtn) {
      elements.mobileMenuBtn.addEventListener('click', toggleSidebar);
    }

    // 点击内容区域关闭移动端侧边栏
    document.querySelector('.content').addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        closeSidebar();
      }
    });
  }

  // ===== 顶部导航处理 =====
  function handleTopTabClick(e) {
    const tab = e.currentTarget;
    const targetPart = tab.dataset.part;

    // 更新激活状态
    elements.topTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    // 滚动到对应Part
    const targetSection = document.querySelector(`[data-part="${targetPart}"]`);
    if (targetSection) {
      targetSection.scrollIntoView({ behavior: 'smooth' });
    }

    // 更新侧边栏
    updateSidebarForPart(targetPart);
  }

  // ===== 侧边栏导航处理 =====
  function handleSidebarNavClick(e) {
    e.preventDefault();
    const link = e.currentTarget;
    const targetId = link.dataset.target;

    const targetElement = document.querySelector(targetId);
    if (targetElement) {
      targetElement.scrollIntoView({ behavior: 'smooth' });
    }

    // 移动端关闭侧边栏
    if (window.innerWidth <= 768) {
      closeSidebar();
    }
  }

  // ===== 侧边栏更新 =====
  function updateSidebarForPart(partId) {
    // 这里可以根据Part切换侧边栏内容
    console.log('Switching to part:', partId);
  }

  // ===== Scroll Spy =====
  function initScrollSpy() {
    const observerOptions = {
      rootMargin: '-20% 0px -70% 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const sectionId = entry.target.id;
          const partId = entry.target.dataset.part;

          // 更新侧边栏
          elements.sidebarNavLinks.forEach(link => {
            link.classList.toggle('active', link.dataset.target === `#${sectionId}`);
          });

          // 更新顶部导航
          elements.topTabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.part === partId);
          });
        }
      });
    }, observerOptions);

    elements.sections.forEach(section => {
      observer.observe(section);
    });
  }

  // ===== Lightbox =====
  function initLightbox() {
    elements.images.forEach(img => {
      img.addEventListener('click', openLightbox);
    });
  }

  function openLightbox(e) {
    const src = e.target.src;
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
      <div class="lightbox-content">
        <img src="${src}" alt="">
        <button class="lightbox-close">&times;</button>
      </div>
    `;
    document.body.appendChild(lightbox);

    lightbox.querySelector('.lightbox-close').addEventListener('click', () => {
      document.body.removeChild(lightbox);
    });

    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) {
        document.body.removeChild(lightbox);
      }
    });
  }

  // ===== 移动端侧边栏 =====
  function toggleSidebar() {
    state.sidebarOpen = !state.sidebarOpen;
    elements.sidebar.classList.toggle('open', state.sidebarOpen);
  }

  function closeSidebar() {
    state.sidebarOpen = false;
    elements.sidebar.classList.remove('open');
  }

  // ===== 启动 =====
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
'''

# ============== HTML Template ==============
def generate_html(report_data: Dict) -> str:
    """生成HTML内容"""

    # 生成Part侧边栏
    part_sidebars = generate_part_sidebars(report_data)

    # 生成Part内容
    part_contents = generate_part_contents(report_data)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{report_data.get('meta', {}).get('project', '投资分析报告')} - 金地集团投资部</title>
  <link rel="stylesheet" href="assets/theme.css">
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <!-- Header -->
  <header class="header">
    <div class="header-logo">
      <span>金地集团｜投资部</span>
    </div>
    <nav class="top-tabs">
      <button class="top-tab active" data-part="home">首页</button>
      <button class="top-tab" data-part="part1">项目概况</button>
      <button class="top-tab" data-part="part2">市场竞争</button>
      <button class="top-tab" data-part="part3">客户定位</button>
      <button class="top-tab" data-part="part4">设计方案</button>
      <button class="top-tab" data-part="part5">运营计划</button>
      <button class="top-tab" data-part="part6">投资测算</button>
    </nav>
    <button class="mobile-menu-btn">☰</button>
  </header>

  <!-- Main Container -->
  <div class="main-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      {part_sidebars}
    </aside>

    <!-- Content -->
    <main class="content">
      {part_contents}
    </main>
  </div>

  <script src="assets/app.js"></script>
</body>
</html>'''

    return html


def generate_part_sidebars(report_data: Dict) -> str:
    """生成各Part的侧边栏导航"""
    sidebars = []

    for part in report_data.get('parts', []):
        part_id = part.get('part_id', '')
        part_title = part.get('title', '')

        nav_items = []
        for section in part.get('sections', []):
            section_id = section.get('id', '')
            section_title = section.get('title', '')
            nav_items.append(f'''
              <li class="sidebar-nav-item">
                <a href="#{section_id}" class="sidebar-nav-link" data-target="#{section_id}">{section_title}</a>
              </li>''')

        # Part4特殊处理:添加方案导航
        if part_id == 'part4' and part.get('part4_options'):
            for option in part['part4_options']:
                option_id = option.get('option_id', '')
                option_title = option.get('option_title', '')
                nav_items.append(f'''
                  <li class="sidebar-nav-item">
                    <a href="#{option_id}" class="sidebar-nav-link" data-target="#{option_id}">{option_title}</a>
                  </li>''')

        sidebars.append(f'''
      <div class="sidebar-section" data-part="{part_id}" style="display: none;">
        <div class="sidebar-title">{part_title}</div>
        <ul class="sidebar-nav">
          {''.join(nav_items)}
        </ul>
      </div>''')

    return '\n'.join(sidebars)


def generate_part_contents(report_data: Dict) -> str:
    """生成各Part的内容"""
    contents = []

    for part in report_data.get('parts', []):
        part_id = part.get('part_id', '')
        part_title = part.get('title', '')

        sections_html = []
        for section in part.get('sections', []):
            section_id = section.get('id', '')
            section_title = section.get('title', '')
            section_blocks = section.get('blocks', [])
            key_takeaways = section.get('key_takeaways', [])
            kpis = section.get('kpis', [])

            # 生成内容块
            blocks_html = []
            for block in section_blocks:
                block_type = block.get('type', '')
                block_content = block.get('content', '')

                if block_type == 'text':
                    blocks_html.append(f'<p>{block_content}</p>')
                elif block_type == 'table':
                    blocks_html.append(f'<div class="table-container">{block_content}</div>')
                elif block_type == 'image':
                    blocks_html.append(f'<div class="image-card"><img src="assets/images/{block_content}" alt="{section_title}"></div>')
                elif block_type == 'list':
                    list_items = block_content.split('\\n')
                    list_html = '<ul>' + ''.join(f'<li>{item}</li>' for item in list_items if item.strip()) + '</ul>'
                    blocks_html.append(list_html)

            # 生成KPI卡片
            kpis_html = ''
            if kpis:
                kpis_html = '<div class="kpi-grid">'
                for kpi in kpis[:4]:  # 最多显示4个KPI
                    kpis_html += f'''
                      <div class="kpi-card">
                        <div class="kpi-label">{kpi.get('label', '')}</div>
                        <div class="kpi-value">{kpi.get('value', '')}</div>
                      </div>'''
                kpis_html += '</div>'

            # 生成关键要点
            takeaways_html = ''
            if key_takeaways:
                takeaways_html = f'''
                  <div class="key-takeaways">
                    <div class="key-takeaways-title">关键要点</div>
                    <ul class="key-takeaways-list">
                      {''.join(f'<li>{t}</li>' for t in key_takeaways)}
                    </ul>
                  </div>'''

            sections_html.append(f'''
        <section id="{section_id}" class="section" data-part="{part_id}">
          <h2 class="section-title">{section_title}</h2>
          {takeaways_html}
          {kpis_html}
          {''.join(blocks_html)}
        </section>''')

        # Part4特殊处理:生成方案展示
        if part_id == 'part4' and part.get('part4_options'):
            for option in part['part4_options']:
                option_id = option.get('option_id', '')
                option_title = option.get('option_title', '')
                advantages = option.get('advantages', [])

                advantages_html = ''
                if advantages:
                    advantages_html = f'''
                      <div class="advantages-section">
                        <h4>方案优势</h4>
                        <ul class="advantages-list">
                          {''.join(f'<li>{adv}</li>' for adv in advantages)}
                        </ul>
                      </div>'''

                sections_html.append(f'''
        <section id="{option_id}" class="section" data-part="{part_id}">
          <div class="design-option">
            <div class="design-option-header">
              <h3 class="design-option-title">{option_title}</h3>
            </div>
            <div class="design-option-content">
              <div class="master-plan-section">
                <h4>总平面图</h4>
                <div class="model-placeholder">
                  <div class="model-placeholder-icon">🏗️</div>
                  <p>方案总平面图展示区域</p>
                </div>
                <div class="master-plan-points">
                  <div class="master-plan-point">入口组织清晰</div>
                  <div class="master-plan-point">示范区位置优越</div>
                  <div class="master-plan-point">动静分区合理</div>
                  <div class="master-plan-point">景观轴线明确</div>
                </div>
              </div>
              {advantages_html}
            </div>
          </div>
        </section>''')

        contents.append(f'''
      <div id="{part_id}" data-part="{part_id}">
        {''.join(sections_html)}
      </div>''')

    return '\n'.join(contents)


# ============== Main Generator ==============
def generate_site():
    """生成完整网站"""
    print('[INFO] Starting website generation...')

    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / 'assets').mkdir(exist_ok=True)
    (OUTPUT_DIR / 'assets' / 'images').mkdir(exist_ok=True)

    # 读取报告数据
    print('[INFO] Loading report data...')
    with open(REPORT_DATA_PATH, 'r', encoding='utf-8') as f:
        report_data = json.load(f)

    # 生成HTML
    print('[INFO] Generating HTML...')
    html_content = generate_html(report_data)
    with open(OUTPUT_DIR / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 生成CSS
    print('[INFO] Generating CSS...')
    with open(OUTPUT_DIR / 'assets' / 'theme.css', 'w', encoding='utf-8') as f:
        f.write(THEME_CSS)
    with open(OUTPUT_DIR / 'assets' / 'styles.css', 'w', encoding='utf-8') as f:
        f.write(STYLES_CSS)

    # 生成JavaScript
    print('[INFO] Generating JavaScript...')
    with open(OUTPUT_DIR / 'assets' / 'app.js', 'w', encoding='utf-8') as f:
        f.write(APP_JS)

    # 复制图片
    print('[INFO] Copying images...')
    if IMAGES_DIR.exists():
        for img_file in IMAGES_DIR.glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                shutil.copy2(img_file, OUTPUT_DIR / 'assets' / 'images' / img_file.name)

    # 复制报告数据
    print('[INFO] Copying report data...')
    shutil.copy2(REPORT_DATA_PATH, OUTPUT_DIR / 'assets' / 'report_data.json')

    print(f'[OK] Website generated successfully!')
    print(f'     Output: {OUTPUT_DIR.absolute()}')
    print(f'     Open: {OUTPUT_DIR.absolute() / "index.html"}')


if __name__ == '__main__':
    generate_site()
